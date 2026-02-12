from pydantic import BaseModel
from typing import List

class WebPlanDTO(BaseModel):
    site_type: str
    sections: List[str]
    style: str
    images: List[str] = []
