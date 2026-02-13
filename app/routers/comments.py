from fastapi import APIRouter, HTTPException, Request
from typing import List
from ..schemas import CommentCreate, Comment

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)

@router.post("/", response_model=Comment)
async def create_comment(request: Request, comment: CommentCreate):
    try:
        supabase = request.app.state.supabase
        data = comment.dict()
        response = await supabase.table("comments").insert(data).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create comment")
            
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/post/{post_id}", response_model=List[Comment])
async def get_comments_by_post(post_id: int, request: Request):
    try:
        supabase = request.app.state.supabase
        response = await supabase.table("comments").select("*").eq("post_id", post_id).order("created_at", desc=False).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
