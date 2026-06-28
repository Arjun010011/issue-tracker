
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.database import meta,engine
from app.middleware.timer import time_middleware
from app.routes.auth import router as auth_router
from app.routes.issues import router as issue_router
from app.routes.users import router as user_router
import app.models
meta.create_all(engine)
app = FastAPI()
app.middleware("http")(time_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(issue_router)
app.include_router(user_router)
