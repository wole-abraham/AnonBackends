import argparse
import json
from sqlmodel import Session
from app.db import engine, create_db_and_tables
from app.model import Post, Comment
from datetime import datetime

def insert_post(content: str):
    """Insert a single post into the database."""
    with Session(engine) as session:
        post = Post(content=content)
        session.add(post)
        session.commit()
        session.refresh(post)
        print(f"✅ Successfully inserted post with ID: {post.id}")
        return post

def insert_from_json(filepath: str):
    """Insert multiple posts from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with Session(engine) as session:
            count = 0
            for item in data:
                # We expect "text" or "content" in the JSON
                content = item.get("text") or item.get("content")
                if content:
                    post = Post(content=content)
                    
                    # Optional: mapped fields if they exist in JSON
                    if "id" in item:
                        post.id = item["id"]
                    if "likes" in item:
                        post.likes = item["likes"]
                    if "time" in item:
                        # Assuming time is in milliseconds from epoch
                        post.created_at = datetime.fromtimestamp(item["time"] / 1000.0)
                        
                    session.add(post)
                    count += 1
            
            session.commit()
            print(f"✅ Successfully inserted {count} posts from {filepath}")
    except Exception as e:
        print(f"❌ Error reading or inserting from JSON: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manually insert data into the Anon Platform database.")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Single post parser
    post_parser = subparsers.add_parser("post", help="Insert a single post")
    post_parser.add_argument("-c", "--content", type=str, required=True, help="The text content of the post")
    
    # JSON import parser
    json_parser = subparsers.add_parser("import", help="Import posts from a JSON file")
    json_parser.add_argument("-f", "--file", type=str, required=True, help="Path to the JSON file")
    
    args = parser.parse_args()
    
    # Ensure tables are created before inserting
    create_db_and_tables()
    
    if args.command == "post":
        insert_post(args.content)
    elif args.command == "import":
        insert_from_json(args.file)
    else:
        parser.print_help()
