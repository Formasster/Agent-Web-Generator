from pydantic import BaseModel
from typing import List, Optional
from app.dto.customization_dto import WebCustomizationDTO


class PromptDTO(BaseModel):
    prompt: str
    images: List[str] = []
    docs: List[str] = []
    customization: Optional[WebCustomizationDTO] = None
    """Personalización opcional. Si se omite, Gemini decide todo automáticamente."""