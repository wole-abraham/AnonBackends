import dotenv
import os

from supabase import acreate_client, AsyncClient

dotenv.load_dotenv()
url:str = os.getenv("SUPABASE_URL")
key:str = os.getenv("SUPABASE_KEY")

async def create_supabase():
    supabase: AsyncClient = await acreate_client(url, key)
    return supabase


