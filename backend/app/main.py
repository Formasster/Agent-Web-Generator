from fastapi import FastAPI
from app.api.routes.generate import router

app = FastAPI(title="AI Web Builder")

app.include_router(router)
