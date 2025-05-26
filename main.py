# main.py

from fastapi import FastAPI
from app.api.requirement import router as requirement_router

app = FastAPI(title="RealtorAI API")

app.include_router(requirement_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
