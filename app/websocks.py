from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
from typing import List
from uuid import uuid4


connections: List[WebSocket] =[]

app = APIRouter()

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
async def create_post(data: dict):
    post = {
        "id": str(uuid4()),
        "type": "new_post",
        "data": data
    }
    posts.append(post)
    for ws in connections:
        await ws.send_json(post)
    return {"status": "success"}

@app.get("/posts")
async def get_posts():
    return posts
