from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_supabase
from .storage import Storage
from .websocks import app as websocket_app
from .db import create_db_and_tables

app = FastAPI(title="Anon Platform Backend")

# Setup CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://anonfront.vercel.app",
    "https://anonfront.vercel.app",
    # Add other origins as needed (e.g., your frontend URL)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for now, restrict for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    app.state.supabase = await create_supabase()
    app.state.storage = Storage()
    create_db_and_tables()


app.include_router(websocket_app)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Anon Platform API"}
