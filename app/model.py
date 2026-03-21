from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import uuid4

class Post(SQLModel, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    content: str
    created_at: datetime | None = Field(default_factory=datetime.now)
    likes: int = 0
    views: int = 0
    comment_count: int = 0

class Comment(SQLModel, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    post_id: str = Field(index=True)
    content: str
    created_at: datetime | None = Field(default_factory=datetime.now)
    likes: int = 0