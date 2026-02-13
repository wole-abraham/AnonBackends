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

@router.post("/{comment_id}/like", response_model=Comment)
async def like_comment(comment_id: int, request: Request):
    try:
        supabase = request.app.state.supabase
        
        # Fetch current likes
        res = await supabase.table("comments").select("likes").eq("id", comment_id).execute()
        
        if not res.data or len(res.data) == 0:
             raise HTTPException(status_code=404, detail="Comment not found")
             
        current_likes = res.data[0].get("likes") or 0
        new_likes = current_likes + 1
        
        # Update likes
        update_res = await supabase.table("comments").update({"likes": new_likes}).eq("id", comment_id).execute()
        
        if not update_res.data or len(update_res.data) == 0:
             raise HTTPException(status_code=500, detail="Failed to like comment")
             
        return update_res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
