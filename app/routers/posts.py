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
        # Select posts and the count of comments
        # Assumes a foreign key relationship exists between comments and posts
        response = await supabase.table("posts").select("*, comments(count)").order("created_at", desc=True).execute()
        
        posts_data = response.data
        for post in posts_data:
            # Map comments count to comment_count field
            # PostgREST returns comments as [{'count': n}] or []
            comments_data = post.get("comments", [])
            if isinstance(comments_data, list) and len(comments_data) > 0:
                post["comment_count"] = comments_data[0].get("count", 0)
            else:
                post["comment_count"] = 0
            # Remove keys not in schema if necessary, but Pydantic ignores extras if configured (default is ignore)
                
        return posts_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{post_id}", response_model=Post)
async def get_post(post_id: int, request: Request):
    try:
        supabase = request.app.state.supabase
        response = await supabase.table("posts").select("*, comments(count)").eq("id", post_id).execute()
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Post not found")
            
        post_data = response.data[0]
        comments_data = post_data.get("comments", [])
        if isinstance(comments_data, list) and len(comments_data) > 0:
            post_data["comment_count"] = comments_data[0].get("count", 0)
        else:
            post_data["comment_count"] = 0
            
        return post_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{post_id}/like", response_model=Post)
async def like_post(post_id: int, request: Request):
    try:
        supabase = request.app.state.supabase
        
        # Fetch current likes
        res = await supabase.table("posts").select("likes").eq("id", post_id).execute()
        
        if not res.data or len(res.data) == 0:
             raise HTTPException(status_code=404, detail="Post not found")
             
        current_likes = res.data[0].get("likes") or 0
        new_likes = current_likes + 1
        
        # Update likes
        update_res = await supabase.table("posts").update({"likes": new_likes}).eq("id", post_id).execute()
        
        if not update_res.data or len(update_res.data) == 0:
             raise HTTPException(status_code=500, detail="Failed to like post")
             
        return update_res.data[0]
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
