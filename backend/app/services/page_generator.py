from app.dto.web_plan_dto import WebPlanDTO
from app.services.stitch_client import generate_with_stitch


class PageGenerator:

    async def generate(self, plan: WebPlanDTO) -> str:
        html = await generate_with_stitch(plan)
        return html
