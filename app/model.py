from sqlmodel import SQLModel, Field
from datetime import datetime, timedelta, timezone
from uuid import uuid4

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