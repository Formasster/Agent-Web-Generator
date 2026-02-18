from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List
from sqlalchemy.orm import Session
from app.dto.prompt_dto import PromptDTO
from app.dto.result_dto import GeneratedPageDTO
from app.agents.web_builder_agent import WebBuilderAgent
from app.db.database import get_db
from app.db import repository
import os
import asyncio
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
agent = WebBuilderAgent()


@router.post("/generate", response_model=GeneratedPageDTO)
async def generate_page(data: PromptDTO, db: Session = Depends(get_db)):
    result = await agent.run(data)

    # Guardar en BD usando session_id genérico para requests sin sesión de usuario
    session_id = f"api_{uuid.uuid4().hex}"
    user = repository.get_or_create_user(db, session_id)
    plan = agent.analyze_prompt(data.prompt)
    repository.save_generated_page(db, user.id, data.prompt, plan.site_type, result.html)
    repository.save_message(db, user.id, "user", data.prompt)
    repository.save_message(db, user.id, "agent", result.html)
    logger.info(f"Página generada vía /generate (tipo: {plan.site_type})")

    return result


@router.post("/generate/upload", response_model=GeneratedPageDTO)
async def generate_with_upload(
    prompt: str = Form(...),
    images: List[UploadFile] = File(default=[]),
    docs: List[UploadFile] = File(default=[]),
    session_id: str = Form(default=None),
    db: Session = Depends(get_db),
):
    """Acepta archivos (imágenes y docs), los guarda en backend/uploads y llama al agente."""
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
    upload_dir = os.path.abspath(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)

    image_paths = []
    for f in images:
        filename = f"{uuid.uuid4().hex}_{f.filename}"
        dest = os.path.join(upload_dir, filename)
        with open(dest, "wb") as out:
            out.write(await f.read())
        image_paths.append(dest)

    doc_paths = []
    for f in docs:
        filename = f"{uuid.uuid4().hex}_{f.filename}"
        dest = os.path.join(upload_dir, filename)
        with open(dest, "wb") as out:
            out.write(await f.read())
        doc_paths.append(dest)

    prompt_dto = PromptDTO(prompt=prompt, images=image_paths, docs=doc_paths)
    result = await agent.run(prompt_dto)

    # Guardar en BD
    effective_session_id = session_id if session_id else f"upload_{uuid.uuid4().hex}"
    user = repository.get_or_create_user(db, effective_session_id)
    plan = agent.analyze_prompt(prompt)
    repository.save_generated_page(db, user.id, prompt, plan.site_type, result.html)
    repository.save_message(db, user.id, "user", prompt)
    repository.save_message(db, user.id, "agent", result.html)
    logger.info(f"Página generada vía /generate/upload (tipo: {plan.site_type}, archivos: {len(image_paths)} imgs, {len(doc_paths)} docs)")

    return result