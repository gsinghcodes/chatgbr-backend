from uuid import UUID
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse

from api.dependencies.auth import get_current_user
from api.schemas.chat_schema import ChatRequest
from api.schemas.common import ReturnJSON
from api.schemas.repository_schema import CreateRepositoryRequest

from database.models.user import UserModel

from services.chat.chat_service import ChatService
from services.repository.repository_service import RepositoryService

router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
)

repository_service = RepositoryService()
chat_service = ChatService()


@router.post("/{repository_id}/chat")
def chat(
    repository_id: UUID,
    request: ChatRequest,
    current_user: UserModel = Depends(get_current_user),
):
    def event_stream():
        try:
            for event in chat_service.ask(
                user_id=current_user.id,
                repository_id=repository_id,
                conversation_id=request.conversation_id,
                question=request.question,
            ):
                yield f"data: {json.dumps(event)}\n\n"

        except ValueError as exc:
            error_event = {
                "type": "error",
                "message": str(exc),
            }

            yield f"data: {json.dumps(error_event)}\n\n"

        except Exception:

            error_event = {
                "type": "error",
                "message": "Failed to generate response.",
            }

            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post(
    "",
    response_model=ReturnJSON,
    status_code=status.HTTP_201_CREATED,
)
async def create_repository(
    request: CreateRepositoryRequest,
    current_user: UserModel = Depends(get_current_user),
):
    data = await repository_service.create_repository(
        user_id=current_user.id,
        clone_url=request.clone_url,
    )

    return JSONResponse(content=data, status_code=data["status"])


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
