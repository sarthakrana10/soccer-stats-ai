from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.agent.state import AgentState
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import ALL_TOOLS
from app.config import settings


def build_graph():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
    ).bind_tools(ALL_TOOLS)

    tool_node = ToolNode(ALL_TOOLS)

    def agent_node(state: AgentState):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + state["messages"]
        response = llm.invoke(messages)
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
