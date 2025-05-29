from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.requirement import router as requirement_router
from app.api.weight_infer import router as weight_infer_router
from app.api.recommendation import router as recommendation_router
from app.db import Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.init_pool()
    yield
    await Database.close_pool()


app = FastAPI(title="RealtorAI API", lifespan=lifespan)

# 统一使用 /api 作为接口前缀
app.include_router(requirement_router, prefix="/api")
app.include_router(weight_infer_router, prefix="/api")
app.include_router(recommendation_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
