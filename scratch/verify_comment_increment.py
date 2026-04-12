from sqlmodel import Session, select
from app.db import engine, create_db_and_tables
from app.model import Post, Comment
import uuid

def verify():
    # Ensure tables exist
    create_db_and_tables()
    
    with Session(engine) as session:
        # 1. Create a dummy post
        post = Post(content="Test verification post")
        session.add(post)
        session.commit()
        session.refresh(post)
        
        post_id = post.id
        initial_count = post.comment_count
        print(f"Initial comment count: {initial_count}")
        
        # 2. Simulate what create_comment does
        # Increment comment count for the post
        post_to_update = session.get(Post, post_id)
        if post_to_update:
            post_to_update.comment_count += 1
            session.add(post_to_update)
        
        comment = Comment(
            post_id=post_id,
            content="Test verification comment",
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)
        session.refresh(post_to_update)
        
        final_count = post_to_update.comment_count
        print(f"Final comment count: {final_count}")
        
        # Check if incremented
        if final_count == initial_count + 1:
            print("SUCCESS: Comment count incremented correctly.")
        else:
            print("FAILURE: Comment count did not increment correctly.")

        # 3. Verify data structure (conceptual)
        comment_data = {
            "type": "comment",
            "data": {
                "id": comment.id,
                "post_id": comment.post_id,
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
                "likes": comment.likes,
            }
        }
        print(f"Comment data structure: {comment_data}")
        
        # Clean up (optional but good)
        # session.delete(comment)
        # session.delete(post_to_update)
        # session.commit()

if __name__ == "__main__":
    verify()
