from fastapi import APIRouter
from backend.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(
        reply="North Star Support Bot is ready. Chat flow logic will be added next.",
        intent="placeholder",
        state=request.state,
        handoff=False,
    )
