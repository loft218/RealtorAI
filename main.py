from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.services.jieba_custom_dict import add_all_custom_words

from app.api.requirement import router as requirement_router
from app.api.weight_infer import router as weight_infer_router
from app.api.recommendation import router as recommendation_router
from app.api.circle_score import router as circle_score_router
from app.api.community_score import router as community_score_router
from app.api.market_trend import router as market_trend_router
from app.api.market_overview import router as market_overview_router
from app.api.property_policy import router as property_policy_router
from app.api.market_stats import router as market_stats_router
from app.api.community_suggest import router as community_suggest_router

from app.db import Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    add_all_custom_words()  # 应用启动时自动添加所有自定义分词
    await Database.init_pool()
    yield
    await Database.close_pool()


app = FastAPI(title="RealtorAI API", lifespan=lifespan)

# 统一使用 /api 作为接口前缀
app.include_router(requirement_router, prefix="/api")
app.include_router(weight_infer_router, prefix="/api")
app.include_router(recommendation_router, prefix="/api")
app.include_router(circle_score_router, prefix="/api")
app.include_router(community_score_router, prefix="/api")
app.include_router(market_trend_router, prefix="/api")
app.include_router(market_overview_router, prefix="/api")
app.include_router(property_policy_router, prefix="/api")
app.include_router(market_stats_router, prefix="/api")
app.include_router(community_suggest_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
