import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from app.api.routes.generate import router as generate_router
from app.api.routes.chat import router as chat_router
from app.db.database import engine, test_connection
from app.db import models

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Web Builder")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(generate_router)
app.include_router(chat_router)


@app.on_event("startup")
async def startup():
    if test_connection():
        models.Base.metadata.create_all(bind=engine)
        logger.info("Tablas creadas/verificadas correctamente")
    else:
        logger.error("No se pudo conectar a la BD al iniciar")