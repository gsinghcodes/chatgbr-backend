import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.auth import get_current_user
from api.schemas.chat_schema import ChatRequest
from api.schemas.common import ReturnJSON

from database.models.user import UserModel

from services.chat.chat_service import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

chat_service = ChatService()


@router.post(
    "",
    response_model=ReturnJSON,
)
def chat(
    request: ChatRequest,
    current_user: UserModel = Depends(get_current_user),
):
    try:
        answer = chat_service.ask(
            repository_id=uuid.UUID(request.repository_id),
            question=request.question,
        )

        return ReturnJSON(
            message="Answer generated successfully.",
            data={
                "answer": answer,
            },
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
