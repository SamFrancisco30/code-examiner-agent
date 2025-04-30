# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.route_service.exec_routes import router as exec_router
from backend.route_service.anal_routes import router as behavior_router

app = FastAPI(title="编程考试后端服务")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routers
app.include_router(exec_router, prefix="/api")
app.include_router(behavior_router, prefix="/api")
