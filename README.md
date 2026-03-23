# AIAgent - 旅行助手智能体（Thought-Action-Observation）

本项目实现了一个**由真实 LLM 驱动**的旅行助手智能体：

- 通过 `wttr.in` 查询指定城市实时天气（JSON）
- 通过 `Tavily Search API` 根据城市与天气推荐景点
- 使用“Thought-Action-Observation”范式进行多轮推理与工具调用
- 兼容任何 **OpenAI API 兼容**的大语言模型服务（OpenAI/Azure/Ollama/vLLM 等）

## 目录结构

```text
travel_agent/
  __init__.py
  prompt.py
  llm.py
  tools.py
  runner.py
main.py
requirements.txt
.env.example
```

## 安装

建议使用虚拟环境（你可以使用你现有的 `venv`，不强制必须是 `.venv`）：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 配置环境变量

复制并修改 `.env.example`：

```bash
cp .env.example .env
```

至少需要配置：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL_ID`
- `TAVILY_API_KEY`（如果不配，将无法使用景点搜索工具）

## 运行示例

```bash
python main.py
```

> 说明：如果你使用的是我创建的 `.venv`，只需把上面命令里的 `venv` 换成 `.venv` 即可。

你也可以在 `main.py` 中修改 `user_prompt` 来测试不同城市。

## 输出格式说明

智能体会强制模型每轮只输出一对：

```text
Thought: ...
Action: get_weather(city="北京")
```

工具执行结果会以：

```text
Observation: ...
```

当信息足够时，会以：

```text
Action: finish(answer="...")
```

结束循环并输出最终答案。
