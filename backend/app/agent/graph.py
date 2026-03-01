from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.agent.state import AgentState
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import ALL_TOOLS
from app.config import settings


def build_graph():
    llm = ChatNVIDIA(
        model="moonshotai/kimi-k2.5",
        api_key=settings.nvidia_api_key,
    ).bind_tools(ALL_TOOLS)

    tool_node = ToolNode(ALL_TOOLS)

    def agent_node(state: AgentState):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + state["messages"]
        response = llm.invoke(messages)
        # Kimi K2.5 sometimes puts the answer in reasoning_content instead of content
        if not response.content and response.additional_kwargs.get("reasoning_content"):
            response.content = response.additional_kwargs["reasoning_content"]
        tools_used = state.get("tools_used", [])
        if response.tool_calls:
            tools_used = tools_used + [tc["name"] for tc in response.tool_calls]
        return {"messages": [response], "tools_used": tools_used}

    def should_continue(state: AgentState):
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return END

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()
