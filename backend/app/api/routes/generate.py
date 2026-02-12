from fastapi import APIRouter
from app.dto.prompt_dto import PromptDTO
from app.dto.result_dto import GeneratedPageDTO
from app.agents.web_builder_agent import WebBuilderAgent

router = APIRouter()

agent = WebBuilderAgent()


@router.post("/generate", response_model=GeneratedPageDTO)
async def generate_page(data: PromptDTO):


    result = await agent.run(data)


    return result
