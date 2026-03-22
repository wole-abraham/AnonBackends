from fastapi import WebSocket, WebSocketDisconnect, Request, APIRouter
from sqlmodel import Session, select
from .db import engine
from typing import List
from uuid import uuid4
from .model import Post, Comment
from fastapi.responses import JSONResponse


connections: List[WebSocket] =[]

app = APIRouter()

restricted_names = ["jessica", "abraham"]


CURRENT_VERSION = "1.0.6"

def check_version(request: Request):
    client_version = request.headers.get("x-app-version")

    if client_version != CURRENT_VERSION:
        raise HTTPException(
            status_code=426,
            detail="OUTDATED_CLIENT"
        )



posts = []

@app.websocket("/ws")
async def websocket_endpoint(ws:WebSocket):
    await ws.accept()
    connections.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        connections.remove(ws)

@app.post("/post")
async def create_post(request: Request, data: dict):
    check_version(request)
    print(data)
    with Session(engine) as session:
        
        post = Post(
            content=data["text"],
        )
        session.add(post)
        session.commit()
        session.refresh(post)
    post_data = {
        "id": post.id,
        "content": post.content,
        "created_at": post.created_at.isoformat(),
        "likes": post.likes,
        "views": post.views,
        "comment_count": post.comment_count
    }
    if post_data['content'].lower() in restricted_names:
        return {"status": "successs"}
    for ws in connections:
        await ws.send_json(post_data)
    return {"status": "successs"}

@app.get("/posts")
async def get_posts(request: Request):
    # check_version(request)
    with Session(engine) as session:
        posts = session.exec(select(Post)).all()
        return posts

@app.post("/comment/{post_id}")
async def create_comment(request: Request, post_id: str, data: dict):
    # check_version(request)
    print(data)
    with Session(engine) as session:
        
        comment = Comment(
            post_id=post_id,
            content=data["content"],
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)
    comment_data = {
        "id": comment.id,
        "post_id": comment.post_id,
        "content": comment.content,
        "created_at": comment.created_at.isoformat(),
        "likes": comment.likes,
    }
    return {"status": "successs"}

@app.get("/comments/{post_id}")
async def get_comments(request: Request, post_id: str):
    # check_version(request)
    with Session(engine) as session:
        comments = session.exec(select(Comment).where(Comment.post_id == post_id)).all()
        comment_data = []
        for comment in comments:
            comment_data.append({
                "id": comment.id,
                "post_id": comment.post_id,
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
                "likes": comment.likes,
            })
        return comment_data

@app.get("/version")
async def version():
    return JSONResponse({"version": CURRENT_VERSION})