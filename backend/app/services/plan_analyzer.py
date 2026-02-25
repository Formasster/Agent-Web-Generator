"""
plan_analyzer.py
Clasificador inteligente que usa Gemini directamente (sin ADK, sin Stitch)
para analizar cualquier prompt libre y devolver un WebPlanDTO completo.

Flujo:
  prompt libre → Gemini (JSON classifier) → WebPlanDTO
"""

import os
import re
import json
import logging
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types as genai_types

from app.dto.web_plan_dto import WebPlanDTO
from app.dto.customization_dto import WebCustomizationDTO

load_dotenv()

logger = logging.getLogger(__name__)

# Reutiliza la misma API key de Stitch — no necesitas una nueva credencial
_GEMINI_API_KEY = os.getenv("STITCH_API_KEY")
_client = genai.Client(api_key=_GEMINI_API_KEY)
_MODEL = "gemini-2.5-flash"

# Secciones válidas que Gemini puede elegir
VALID_SECTIONS = [
    "hero", "about", "products", "pricing", "contact",
    "faq", "testimonials", "gallery", "blog", "team", "projects",
]

_SYSTEM_PROMPT = f"""
You are a web planning assistant.
Your ONLY job is to analyze the user's request and return a JSON object describing the website plan.

The JSON must follow this exact schema:
{{
  "site_type": "<string: type of website, e.g. dental_clinic, gym, restaurant, ecommerce, portfolio, etc.>",
  "sections": ["<section1>", "<section2>", ...],
  "style": "<string: design style description>"
}}

Rules:
- "site_type": infer it freely from the user's request. Be specific (e.g. "dental_clinic", "yoga_studio", "law_firm").
- "sections": choose only from this list: {VALID_SECTIONS}. Pick 3 to 6 sections that make sense for the request.
- "style": describe the visual style in 3-6 words (e.g. "clean professional medical", "energetic bold gym").
- Return ONLY the raw JSON object. No explanation, no markdown, no code fences.
""".strip()


def _parse_plan_json(raw: str) -> dict:
    """
    Extrae y parsea el JSON devuelto por Gemini.
    Usa regex para encontrar el primer objeto JSON válido en la respuesta,
    ignorando cualquier markdown, backticks o texto extra que el modelo pueda añadir.
    """
    # Busca el primer bloque JSON completo en la respuesta
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        raise json.JSONDecodeError("No JSON object found in response", raw, 0)
    return json.loads(match.group())


def _validate_sections(sections: list) -> list:
    """Filtra secciones inválidas y garantiza al menos hero y contact."""
    valid = [s for s in sections if s in VALID_SECTIONS]
    if "hero" not in valid:
        valid.insert(0, "hero")
    if "contact" not in valid:
        valid.append("contact")
    return valid


async def analyze_prompt_with_gemini(
    prompt: str,
    images: list | None = None,
    docs: list | None = None,
    customization: WebCustomizationDTO | None = None,
) -> WebPlanDTO:
    """
    Llama a Gemini para analizar el prompt y construir un WebPlanDTO.
    Entiende cualquier petición libre sin depender de palabras clave.
    Si el cliente envía customization, sus valores tienen prioridad sobre
    lo que Gemini decida.
    """
    logger.info(f"Analizando prompt con Gemini clasificador: '{prompt[:80]}...'")

    user_message = f"User request: {prompt}"
    if docs:
        user_message += f"\nReferenced documents: {docs}"

    plan_data = None

    try:
        response = await asyncio.to_thread(
            _client.models.generate_content,
            model=_MODEL,
            contents=user_message,
            config=genai_types.GenerateContentConfig(
                system_instruction=_SYSTEM_PROMPT,
                temperature=0.2,        # Baja temperatura → respuestas consistentes
                max_output_tokens=256,
            ),
        )

        raw_json = response.text
        logger.info(f"Respuesta del clasificador: {raw_json}")
        plan_data = _parse_plan_json(raw_json)

    except json.JSONDecodeError as e:
        logger.error(f"Error parseando JSON del clasificador: {e}. Usando fallback.")
    except Exception as e:
        logger.error(f"Error llamando a Gemini clasificador: {e}. Usando fallback.")

    # Fallback si Gemini falla por cualquier motivo
    if not plan_data:
        plan_data = {
            "site_type": "generic",
            "sections": ["hero", "about", "contact"],
            "style": "modern clean",
        }

    # Validar secciones devueltas por Gemini
    sections = _validate_sections(plan_data.get("sections", []))
    site_type = plan_data.get("site_type", "generic")
    style = plan_data.get("style", "modern clean")

    # --- Aplicar customization del cliente (siempre tiene prioridad sobre Gemini) ---
    if customization:
        if customization.sections:
            sections = list(customization.sections)
            logger.info(f"Secciones sobreescritas por cliente: {sections}")
        if customization.style:
            style = customization.style
            logger.info(f"Estilo sobreescrito por cliente: {style}")

        # Parámetros de diseño se concatenan al estilo para que el generador los reciba
        style_extras = []
        if customization.color_scheme:
            style_extras.append(f"color-scheme:{customization.color_scheme}")
        if customization.primary_color:
            style_extras.append(f"primary-color:{customization.primary_color}")
        if customization.font_style:
            style_extras.append(f"font:{customization.font_style}")
        if customization.language:
            style_extras.append(f"language:{customization.language}")
        if style_extras:
            style = f"{style} | {' '.join(style_extras)}"

    plan = WebPlanDTO(
        site_type=site_type,
        sections=sections,
        style=style,
        prompt=prompt,
        images=images,
        docs=docs,
    )

    logger.info(
        f"Plan final → tipo: {plan.site_type} | "
        f"secciones: {plan.sections} | estilo: {plan.style}"
    )
    return plan