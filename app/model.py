from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import List

def get_adjusted_time():
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)

class Post(SQLModel, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    content: str
    created_at: datetime | None = Field(default_factory=get_adjusted_time)
    likes: int = 0
    views: int = 0
    comment_count: int = 0

class Comment(SQLModel, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    post_id: str = Field(index=True)
    content: str
    created_at: datetime | None = Field(default_factory=get_adjusted_time)
    likes: int = 0

class Sec(SQLModel, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    device: str
    messages: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
