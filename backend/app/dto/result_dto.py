from pydantic import BaseModel

class GeneratedPageDTO(BaseModel):
    html: str
    framework: str
    