from __future__ import annotations

import os

from dotenv import load_dotenv

from travel_agent.llm import OpenAICompatibleClient
from travel_agent.prompt import AGENT_SYSTEM_PROMPT
from travel_agent.runner import AgentRunner
from travel_agent.tools import available_tools


def main() -> None:
    load_dotenv()

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    base_url = os.environ.get("OPENAI_BASE_URL", "").strip()
    model_id = os.environ.get("OPENAI_MODEL_ID", "").strip()

    if not (api_key and base_url and model_id):
        raise SystemExit(
            "缺少环境变量：OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL_ID。\n"
            "请参考 README.md 与 .env.example 配置。"
        )

    llm = OpenAICompatibleClient(model=model_id, api_key=api_key, base_url=base_url)

    default_city = os.environ.get("AGENT_DEFAULT_CITY", "北京")
    user_prompt = (
        f"你好，请帮我查询一下今天{default_city}的天气，然后根据天气推荐一个合适的旅游景点。"
    )

    runner = AgentRunner(llm=llm, system_prompt=AGENT_SYSTEM_PROMPT, tools=available_tools, max_loops=5)
    answer = runner.run(user_prompt)
    print(answer)


if __name__ == "__main__":
    main()
