from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    title: Optional[str] = None
    content: str
    is_anonymous: bool = True

class PostCreate(PostBase):
    deletion_password: str

class Post(PostBase):
    id: int
    created_at: datetime
    likes: int = 0
    comment_count: int = 0
    # We don't return the deletion_password

    class Config:
        from_attributes = True  

class CommentBase(BaseModel):
    content: str
    author_name: Optional[str] = "Anonymous"

class CommentCreate(CommentBase):
    post_id: int

class Comment(CommentBase):
    id: int
    post_id: int
    likes: int = 0

    class Config:
        from_attributes = True
