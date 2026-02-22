from fastapi import APIRouter, HTTPException, Request
from typing import List
from ..schemas import PostCreate, Post
from ..storage import Storage
from fastapi.responses import Response, JSONResponse

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.get("/upload/{count}")
async def get_upload_url(count: int, request: Request):
    try:
        storage = Storage()
        return storage.generate_upload_url(count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Post)
async def create_post(request: Request, post: PostCreate):
    supabase = request.app.state.supabase
    print(post)
    response = await supabase.rpc(
    "create_post_with_images",
    {
        "p_content": post.content,
        "p_anonymous_id": post.anonymous_id,
        "p_image_keys": post.images,
        "p_title": post.title,
        "p_deletion_password": post.deletion_password
    }
).execute()
    
    return Response(status_code=200)
   

@router.get("/", response_model=List[Post])
async def get_posts(request: Request):
    try:
        supabase = request.app.state.supabase
        # Select posts and the count of comments
        # Assumes a foreign key relationship exists between comments and posts
        response = await supabase.table("posts").select("*, comments(count), post_images(object_key)").order("created_at", desc=True).execute()
        
        return JSONResponse(status_code=200, content=response.data)
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
            
        if post_data.get("images"):
            storage = Storage()
            post_data["images"] = storage.generate_download_url(post_data["images"])
            
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
        
        post_data = update_res.data[0]
        if post_data.get("images"):
            storage = Storage()
            post_data["images"] = storage.generate_download_url(post_data["images"])
             
        return post_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{post_id}/views", response_model=Post)
async def increment_views(post_id: int, request: Request):
    try:
        supabase = request.app.state.supabase
        
        # Fetch current views
        res = await supabase.table("posts").select("views").eq("id", post_id).execute()
        
        if not res.data or len(res.data) == 0:
             raise HTTPException(status_code=404, detail="Post not found")
             
        current_views = res.data[0].get("views") or 0
        new_views = current_views + 1
        
        # Update views
        update_res = await supabase.table("posts").update({"views": new_views}).eq("id", post_id).select("*, comments(count)").execute()
        
        if not update_res.data or len(update_res.data) == 0:
             raise HTTPException(status_code=500, detail="Failed to increment views")
             
        post_data = update_res.data[0]
        comments_data = post_data.get("comments", [])
        if isinstance(comments_data, list) and len(comments_data) > 0:
            post_data["comment_count"] = comments_data[0].get("count", 0)
        else:
            post_data["comment_count"] = 0

        if post_data.get("images"):
            storage = Storage()
            post_data["images"] = storage.generate_download_url(post_data["images"])

        return post_data
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
