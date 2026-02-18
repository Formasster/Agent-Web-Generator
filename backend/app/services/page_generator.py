from app.services.stitch_adk_client import generate_with_adk
import os
from dotenv import load_dotenv

load_dotenv()

class PageGenerator:
    async def generate(self, plan):
        return await generate_with_adk(plan)