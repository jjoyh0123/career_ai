from fastapi import FastAPI
from app.routers import coaching
from app.routers import analysis
app = FastAPI()

# 라우터 등록
app.include_router(coaching.router)
app.include_router(analysis.router)