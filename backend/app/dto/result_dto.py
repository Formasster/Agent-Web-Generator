from pydantic import BaseModel
from typing import Optional


class GeneratedPageDTO(BaseModel):
    html: str
    framework: str
    site_type: Optional[str] = None  # propagado desde el plan para evitar doble llamada a Gemini