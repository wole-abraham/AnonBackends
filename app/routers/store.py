from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel
import uuid
from ..schemas import CommentCreate, Comment

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

class Count(BaseModel):
    count: int

@router.get("/{count}")
async def get_upload_url(request: Request, count: int):
    try:
        url = request.app.state.storage.generate_upload_url(count)
        return JSONResponse(status_code=200, content=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))