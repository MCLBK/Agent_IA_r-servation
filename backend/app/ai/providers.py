import httpx
import json
import re
from abc import ABC, abstractmethod
from app.config import get_settings

settings = get_settings()


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.7) -> str:
        pass

    @abstractmethod
    async def extract_json(self, prompt: str) -> dict:
        pass


class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.7) -> str:
        ollama_messages = [{"role": "system", "content": system_prompt}]
        for m in messages:
            ollama_messages.append({"role": m["role"], "content": m["content"]})

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": ollama_messages,
                        "stream": False,
                        "options": {"temperature": temperature},
                    },
                )
                resp.raise_for_status()
                return resp.json()["message"]["content"]
            except (httpx.ConnectError, httpx.HTTPStatusError):
                return "[Erreur : impossible de contacter le modele IA. Verifiez qu'Ollama est lance.]"

    async def extract_json(self, prompt: str) -> dict:
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.1},
                    },
                )
                resp.raise_for_status()
                text = resp.json()["response"]
                match = re.search(r"\{.*\}", text, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except Exception:
                pass
        return {}


class DemoProvider(LLMProvider):
    """Rule-based provider for demos without an LLM."""

    async def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.7) -> str:
        return ""

    async def extract_json(self, prompt: str) -> dict:
        return {}


def get_provider() -> LLMProvider:
    if settings.AI_PROVIDER == "ollama":
        return OllamaProvider()
    return DemoProvider()
