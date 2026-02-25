from app.dto.prompt_dto import PromptDTO
from app.dto.web_plan_dto import WebPlanDTO
from app.dto.result_dto import GeneratedPageDTO
from app.dto.customization_dto import WebCustomizationDTO
from app.services.plan_analyzer import analyze_prompt_with_gemini
from app.services.page_generator import PageGenerator
import logging

logger = logging.getLogger(__name__)


class WebBuilderAgent:

    def __init__(self):
        self.generator = PageGenerator()

    async def analyze_prompt(
        self,
        prompt: str,
        images: list | None = None,
        docs: list | None = None,
        customization: WebCustomizationDTO | None = None,
    ) -> WebPlanDTO:
        """
        Analiza el prompt con Gemini como clasificador inteligente.
        Entiende cualquier petición libre sin depender de palabras clave.
        Si el cliente envía customization, sus valores tienen prioridad.
        """
        return await analyze_prompt_with_gemini(
            prompt=prompt,
            images=images,
            docs=docs,
            customization=customization,
        )

    async def run(self, prompt_dto: PromptDTO) -> GeneratedPageDTO:
        """
        Orquesta el flujo completo:
          1. Gemini clasifica el prompt y construye el plan (UNA sola vez)
          2. Stitch/Gemini genera el HTML según el plan
          3. Devuelve GeneratedPageDTO con html + framework + site_type

        site_type se incluye en el resultado para que los routers puedan
        guardarlo en BD sin una segunda llamada a Gemini.
        """
        # 1. Clasificación — única llamada a Gemini clasificador
        plan = await self.analyze_prompt(
            prompt=prompt_dto.prompt,
            images=prompt_dto.images or None,
            docs=prompt_dto.docs or None,
            customization=prompt_dto.customization,
        )

        # 2. Generación HTML
        html = await self.generator.generate(plan)

        # 3. Resultado con site_type propagado
        return GeneratedPageDTO(
            html=html,
            framework="html",
            site_type=plan.site_type,
        )