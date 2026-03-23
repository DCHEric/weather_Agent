from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI


@dataclass(frozen=True)
class OpenAICompatibleClient:
    """用于调用任何兼容 OpenAI Chat Completions 接口的 LLM 服务。"""

    model: str
    api_key: str
    base_url: str

    def __post_init__(self) -> None:
        # dataclass(frozen=True) 里不能直接赋值 self.client
        object.__setattr__(self, "client", OpenAI(api_key=self.api_key, base_url=self.base_url))

    def generate(self, prompt: str, system_prompt: str) -> str:
        """调用 LLM 生成回答（非流式）。"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
        )
        return resp.choices[0].message.content or ""
