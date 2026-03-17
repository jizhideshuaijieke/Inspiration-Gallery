import asyncio
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.db import engine
from app.router.admin import router as admin_router
from app.router.artworks import router as artworks_router
from app.router.auth import router as auth_router
from app.router.hall import router as hall_router
from app.router.social import artwork_router as social_artwork_router
from app.router.social import user_router as social_user_router
from app.router.styles import router as styles_router
from app.router.tasks import router as tasks_router
from app.router.users import router as users_router
from app.service.admin_bootstrap import ensure_default_admin
from app.service.artwork_ws_manager import artwork_ws_manager
from app.service.media_store import MEDIA_ROOT, ensure_media_dirs
from app.service.notice_ws_manager import notice_ws_manager
from app.service.ws_manager import task_ws_manager

app = FastAPI(title="Inspiration Gallery API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:8082",
        "http://127.0.0.1:8082",
        "http://localhost:8083",
        "http://127.0.0.1:8083",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(styles_router)
app.include_router(artworks_router)
app.include_router(hall_router)
app.include_router(social_artwork_router)
app.include_router(social_user_router)
app.include_router(admin_router)

ensure_media_dirs()
app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")


@app.on_event("startup")
async def bootstrap_defaults():
    ensure_default_admin()
    task_ws_manager.bind_loop(asyncio.get_running_loop())
    notice_ws_manager.bind_loop(asyncio.get_running_loop())
    artwork_ws_manager.bind_loop(asyncio.get_running_loop())


@app.get("/health")
def health():
    db_status = "up"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        db_status = "down"

    return {
        "code": 0,
        "message": "ok",
        "data": {
            "status": "up",
            "env": settings.app_env,
            "db": db_status,
        },
        "request_id": str(uuid4()),
    }
