import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.auth import get_current_user
from api.schemas.common import ReturnJSON

from database.models.user import UserModel

from services.conversation.conversation_service import ConversationService

router = APIRouter(
    tags=["Conversations"],
)

conversation_service = ConversationService()


@router.get(
    "/repositories/{repository_id}/conversations",
    response_model=ReturnJSON,
)
def list_conversations(
    repository_id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
):
    try:
        conversations = conversation_service.list_conversations(
            user_id=current_user.id,
            repository_id=repository_id,
        )

        return ReturnJSON(
            message="Conversations fetched successfully.",
            data=conversations,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=ReturnJSON,
)
def list_messages(
    conversation_id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
):
    try:
        messages = conversation_service.get_messages(
            user_id=current_user.id,
            conversation_id=conversation_id,
        )

        return ReturnJSON(
            message="Messages fetched successfully.",
            data=messages,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
