from fastapi import APIRouter, HTTPException, Request
from typing import List
from ..schemas import PostCreate, Post

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.post("/", response_model=Post)
async def create_post(request: Request, post: PostCreate):
    try:
        supabase = request.app.state.supabase
        data = post.dict()
        response = await supabase.table("posts").insert(data).execute()
        
        # Verify response structure, usually response.data is a list of created objects
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create post")
            
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Post])
async def get_posts(request: Request):
    try:
        supabase = request.app.state.supabase
        response = await supabase.table("posts").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{post_id}", response_model=Post)
async def get_post(post_id: int, request: Request):
    try:
        supabase = request.app.state.supabase
        response = await supabase.table("posts").select("*").eq("id", post_id).execute()
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Post not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{post_id}")
async def delete_post(request: Request, post_id: int, password: str):
    try:
        supabase = request.app.state.supabase
        # Check if password matches
        # Note: In a real app, do not select * if sensitive info is stored, but here it's fine
        res = await supabase.table("posts").select("deletion_password").eq("id", post_id).execute()
        
        if not res.data or len(res.data) == 0:
             raise HTTPException(status_code=404, detail="Post not found")
             
        stored_password = res.data[0].get("deletion_password")
        if stored_password != password:
            raise HTTPException(status_code=403, detail="Incorrect deletion password")
            
        delete_response = await supabase.table("posts").delete().eq("id", post_id).execute()
        
        return {"message": "Post deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
