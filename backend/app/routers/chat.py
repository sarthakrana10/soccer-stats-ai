import time

from fastapi import APIRouter

from app.agent.graph import build_graph
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter()

graph = build_graph()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    start = time.time()
    result = graph.invoke({"messages": [("human", request.message)]})
    elapsed = time.time() - start

    last_msg = result["messages"][-1]
    answer = last_msg.content or ""

    return ChatResponse(
        answer=answer,
        tools_used=result.get("tools_used", []),
        elapsed_seconds=round(elapsed, 2),
    )
