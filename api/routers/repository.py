from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.auth import get_current_user
from api.schemas.repository_schema import CreateRepositoryRequest
from api.schemas.common import ReturnJSON
from api.schemas.chat_schema import ChatRequest

from database.models.user import UserModel

from services.repository.repository_service import RepositoryService
from services.chat.chat_service import ChatService

router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
)

repository_service = RepositoryService()
chat_service = ChatService()


@router.post(
    "/{repository_id}/chat",
    response_model=ReturnJSON,
)
def chat(
    repository_id: UUID,
    request: ChatRequest,
    current_user: UserModel = Depends(get_current_user),
):
    try:
        result = chat_service.ask(
            user_id=current_user.id,
            repository_id=repository_id,
            conversation_id=request.conversation_id,
            question=request.question,
        )

        return ReturnJSON(message="Answer generated successfully.", data=result)

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


@router.post(
    "",
    response_model=ReturnJSON,
    status_code=status.HTTP_201_CREATED,
)
def create_repository(
    request: CreateRepositoryRequest,
    current_user: UserModel = Depends(get_current_user),
):
    try:
        repository = repository_service.create_repository(
            user_id=current_user.id,
            clone_url=request.clone_url,
        )

        return ReturnJSON(
            message="Repository created successfully.",
            data=repository,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=ReturnJSON,
)
def list_repositories(
    current_user: UserModel = Depends(get_current_user),
):
    repositories = repository_service.list_repositories(
        user_id=current_user.id,
    )

    return ReturnJSON(
        message="Repositories fetched successfully.",
        data=repositories,
    )


@router.get(
    "/{repository_id}",
    response_model=ReturnJSON,
)
def get_repository(
    repository_id: UUID,
    current_user: UserModel = Depends(get_current_user),
):
    try:
        repository = repository_service.get_repository(
            repository_id=repository_id,
            user_id=current_user.id,
        )

        return ReturnJSON(
            message="Repository fetched successfully.",
            data=repository,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.delete(
    "/{repository_id}",
    response_model=ReturnJSON,
)
def delete_repository(
    repository_id: UUID,
    current_user: UserModel = Depends(get_current_user),
):
    try:
        repository_service.delete_repository(
            repository_id=repository_id,
            user_id=current_user.id,
        )

        return ReturnJSON(
            message="Repository deleted successfully.",
            data=None,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
