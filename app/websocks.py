from fastapi import WebSocket, WebSocketDisconnect, Request, APIRouter
from sqlmodel import Session, select
from .db import engine
from typing import List
from uuid import uuid4
from .model import Post, Comment, Sec
from fastapi.responses import JSONResponse
import re


connections: List[WebSocket] =[]

app = APIRouter()

restricted_names = ["jessica", "jess", "abraham", "abe"]

def normalize_text(text: str) -> str:
    text = text.lower()
    # Leetspeak translation map for common letter substitutions
    replacements = {
        '3': 'e', '$': 's', '!': 'i', '1': 'i', 
        '@': 'a', '4': 'a', '0': 'o', '5': 's', 
        '7': 't', '8': 'b'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return re.sub(r'[^a-z]', '', text)


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
    if any(name in normalize_text(data.get("text", "")) for name in restricted_names):
        return {"status": "successs"}
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
    if any(name in normalize_text(data.get("content", "")) for name in restricted_names):
        return {"status": "successs"}
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

@app.post("/sec")
async def create_sec(request: Request, data: dict):
    # check_version(request)
    print(data)
    with Session(engine) as session:
        
        sec = Sec(
            device=data["device"],
            messages=data["messages"],
        )
        session.add(sec)
        session.commit()
        session.refresh(sec)
    sec_data = {
        "id": sec.id,
        "device": sec.device,
        "messages": sec.messages,
    }
    return {"status": "successs"}

@app.get("/sec")
async def get_sec(request: Request):
    # check_version(request)
    with Session(engine) as session:
        secs = session.exec(select(Sec)).all()
        secs_data  = []
        for sec in secs:
            secs_data.append({
                "id": sec.id,
                "device": sec.device,
                "messages": sec.messages,
            })
        return secs_data