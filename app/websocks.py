from fastapi import WebSocket, WebSocketDisconnect, Request
from fastapi.routing import APIRouter
from typing import List
from uuid import uuid4
from fastapi.responses import JSONResponse


connections: List[WebSocket] =[]

app = APIRouter()

CURRENT_VERSION = "1.0.2"

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
    post = {
        "id": str(uuid4()),
        "type": "new_post",
        "data": data
    }
    posts.append(post)
    for ws in connections:
        await ws.send_json(post)
    return {"status": "success", "id": post["id"]}

@app.get("/posts")
async def get_posts(request: Request):
    check_version(request)
    return posts

@app.get("/version")
async def version():
    return JSONResponse({"version": CURRENT_VERSION})