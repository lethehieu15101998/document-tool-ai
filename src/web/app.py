from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.web.api import router
from src.web.routers.file_router import router as file_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(file_router)
