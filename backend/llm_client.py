import os
from typing import Optional
import requests


class LLMClient:
    def __init__(
        self,
        provider: str = "openai",
        model_name: str = "Qwen3-8B",
        base_url: str = "http://127.0.0.1:8001/v1/chat/completions",
        timeout: int = 300,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        api_key: str = ""
    ):
        self.provider = provider
        self.model_name = model_name
        self.base_url = base_url
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.api_key = api_key or ""

    def generate(self, prompt: str) -> Optional[str]:
        if self.provider == "none":
            return None

        if self.provider == "ollama" or "/api/generate" in self.base_url:
            return self._ollama(prompt)

        return self._openai_chat(prompt)

    def _get_api_key(self) -> str:
        """
        优先使用前端传入的 api_key。
        如果前端没填，再读服务器环境变量。
        """
        if self.api_key:
            return self.api_key

        if "deepseek.com" in self.base_url:
            return os.environ.get("DEEPSEEK_API_KEY", "")

        return os.environ.get("OPENAI_API_KEY", "")

    def _openai_chat(self, prompt: str) -> Optional[str]:
        headers = {
            "Content-Type": "application/json"
        }

        api_key = self._get_api_key()
        if api_key:
            headers["Authorization"] = "Bearer {}".format(api_key)

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "top_p": 0.9,
            "max_tokens": self.max_tokens,
            "stream": False
        }

        # DeepSeek 接口可用 OpenAI-compatible 格式。
        # 这里默认不开 thinking，避免角色对话太慢。
        if "deepseek.com" in self.base_url:
            payload["thinking"] = {"type": "disabled"}

        try:
            resp = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

        except Exception as e:
            print("[WARN] OpenAI-compatible call failed:", e)
            return None

    def _ollama(self, prompt: str) -> Optional[str]:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }

        try:
            resp = requests.post(
                self.base_url,
                json=payload,
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip()

        except Exception as e:
            print("[WARN] Ollama call failed:", e)
            return None
