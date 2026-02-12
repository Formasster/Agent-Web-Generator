from app.dto.prompt_dto import PromptDTO
from app.dto.web_plan_dto import WebPlanDTO
from app.dto.result_dto import GeneratedPageDTO
from app.services.page_generator import PageGenerator


class WebBuilderAgent:

    def __init__(self):
        self.generator = PageGenerator()

    def analyze_prompt(self, prompt: str) -> WebPlanDTO:

        prompt_lower = prompt.lower()

        if "tienda" in prompt_lower or "shop" in prompt_lower:
            return WebPlanDTO(
                site_type="ecommerce",
                sections=["hero", "products", "pricing", "contact"],
                style="modern ecommerce"
            )

        if "portfolio" in prompt_lower:
            return WebPlanDTO(
                site_type="portfolio",
                sections=["hero", "projects", "about", "contact"],
                style="minimal modern"
            )

        return WebPlanDTO(
            site_type="landing",
            sections=["hero", "features", "pricing", "contact"],
            style="modern saas"
            
        )

    async def run(self, prompt_dto: PromptDTO) -> GeneratedPageDTO:

        plan = self.analyze_prompt(prompt_dto.prompt)

        html = await self.generator.generate(plan)

        return GeneratedPageDTO(
            html=html,
            framework="html"
        )
