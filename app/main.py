import os
import uuid
import json
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from app.config import settings

# Загружаем промпты из JSON-файла
with open(settings.PROMPTS_PATH, "r", encoding="utf-8") as f:
    prompts = json.load(f)

system_prompt = prompts.get("system_prompt")
tool_data = prompts.get("tool_data")
tool_system_prompts = prompts.get("tool_system_prompts")
anthropic_system_prompt = prompts.get("anthropic_system_prompt")

# Импорт Anthropic-инструмента (пример минимальной реализации)
from AgentFabric.tools.Anthropic import AnthropicLLMTool

anthropic_tool = AnthropicLLMTool(anthropic_system_prompt)

# Импортируем фабрику агента из AgentFabric
from AgentFabric import AgentFactory

app = FastAPI(title="Cocktail Advisor Chat (AgentFabric Integration)")

# Монтируем статику и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Глобальная переменная для хранения экземпляра агента
agent_instance = None

# Событие старта: создаём агента
@app.on_event("startup")
async def startup_event():
    global agent_instance
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    factory = AgentFactory(api_key=settings.OPENAI_API_KEY)
    agent_type = "LangChainAgent"
    model_name = "gpt-4o"
    file_paths = ["data/cocktails.csv"]
    csv_args = {
        "cocktails": {
            "delimiter": ",",
            "quotechar": "\"",
            "fieldnames": ["id", "name", "alcoholic", "category", "glassType", "instructions", "drinkThumbnail", "ingredients", "ingredientMeasures", "text"]
        }
    }
    agent_instance = factory.create_complete_agent(
        agent_type=agent_type,
        model_name=model_name,
        file_paths=file_paths,
        csv_args=csv_args,
        system_prompt=system_prompt,
        tool_data=tool_data,
        tool_system_prompts=tool_system_prompts,
    )

    # Подключаем маршруты (routes)
    from app.routes import chat  # импортируем модуль с роутами
    app.include_router(chat.router)

