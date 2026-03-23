from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from .llm import OpenAICompatibleClient


_ONE_TA_PAIR_PATTERN = re.compile(
    r"(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)",
    re.DOTALL,
)


@dataclass
class AgentRunner:
    llm: OpenAICompatibleClient
    system_prompt: str
    tools: Dict[str, Callable[..., str]]
    max_loops: int = 5

    def run(self, user_prompt: str) -> str:
        prompt_history: List[str] = [f"用户请求: {user_prompt}"]
        final_answer: Optional[str] = None

        for _ in range(self.max_loops):
            full_prompt = "\n".join(prompt_history)

            llm_output = self.llm.generate(full_prompt, system_prompt=self.system_prompt)
            llm_output = (llm_output or "").strip()

            # 只保留一对 Thought-Action，避免模型输出多段
            m = _ONE_TA_PAIR_PATTERN.search(llm_output)
            if m:
                llm_output = m.group(1).strip()

            prompt_history.append(llm_output)

            action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
            if not action_match:
                prompt_history.append("Observation: 错误:模型输出中未找到 Action。")
                break

            action_str = action_match.group(1).strip()

            # finish(answer="...")
            if action_str.startswith("finish"):
                fm = re.search(r"finish\(answer=\"(.*)\"\)\s*\Z", action_str, re.DOTALL)
                if fm:
                    final_answer = fm.group(1)
                else:
                    final_answer = "错误:finish() 解析失败。"
                break

            tool_m = re.search(r"(\w+)\(", action_str)
            args_m = re.search(r"\((.*)\)\s*\Z", action_str, re.DOTALL)
            if not tool_m or not args_m:
                prompt_history.append("Observation: 错误:无法解析工具调用。")
                continue

            tool_name = tool_m.group(1)
            args_str = args_m.group(1)
            kwargs = dict(re.findall(r"(\w+)=\"([^\"]*)\"", args_str))

            if tool_name in self.tools:
                try:
                    observation = self.tools[tool_name](**kwargs)
                except TypeError as e:
                    observation = f"错误:工具参数不匹配 - {e}"
                except Exception as e:
                    observation = f"错误:工具执行异常 - {e}"
            else:
                observation = f"错误:未定义的工具 '{tool_name}'"

            prompt_history.append(f"Observation: {observation}")

        return final_answer or "错误:未能在最大循环次数内完成任务。"
