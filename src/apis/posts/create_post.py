import datetime
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apis.dependencies import get_session, get_current_user, CurrentUser
from src.models.post import Post


class CreatePostRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(max_length=500)


class CreatePostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime.datetime


async def handler(
    request: CreatePostRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CreatePostResponse:
    print(
        f"[CreatePost] user_id={current_user.id}, username={current_user.username}, role={current_user.role}"
    )
    post = Post(
        title=request.title,
        content=request.content,
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return CreatePostResponse(
        id=post.id, title=post.title, content=post.content, created_at=post.created_at
    )
