from fastapi import FastAPI
from app.routers import coaching, analysis
from app.routers import recommendation
app = FastAPI()

# 라우터 등록
app.include_router(coaching.router)
app.include_router(analysis.router)
app.include_router(recommendation.router)