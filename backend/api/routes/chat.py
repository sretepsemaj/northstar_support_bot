from fastapi import APIRouter

from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.chatbot_service import handle_chat

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    result = handle_chat(message=request.message, state=request.state)
    return ChatResponse(
        reply=result.reply,
        intent=result.intent.value,
        state=result.state,
        handoff=result.handoff,
        metadata=result.metadata,
    )
