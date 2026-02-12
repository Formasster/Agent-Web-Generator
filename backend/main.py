from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="AI Web Builder")

app.include_router(router)
