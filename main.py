from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.auth import router as auth_router
from api.routers.repository import router as repository_router
from api.routers.github.github import router as github_router
from api.routers.github.github_auth import router as github_auth_router
from api.routers.conversation import router as conversation_router

app = FastAPI(
    title="Codebase RAG API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(repository_router)
app.include_router(github_router)
app.include_router(github_auth_router)
app.include_router(conversation_router)


@app.get("/")
def root():
    return {"message": "API is running!"}
