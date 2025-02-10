import uuid
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from AgentFabric import AgentFactory  # если требуется создавать агента здесь, иначе использовать глобальный
from app.main import agent_instance, anthropic_tool  # предполагается, что агент уже создан в main.py
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request, response: Response):
    """
    При заходе на страницу проверяем наличие user_id в куках.
    Если его нет, генерируем новый uuid и сохраняем в куках.
    """
    user_id = request.cookies.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        response = templates.TemplateResponse("index.html", {"request": request})
        response.set_cookie(key="user_id", value=user_id)
        return response
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/chat")
async def chat_endpoint(request: Request):
    """
    Обрабатываем POST-запрос:
      - Извлекаем сообщение из тела запроса.
      - Получаем user_id из куки.
      - Вызываем run_agent, передавая user_id, и получаем ответ.
      - Применяем Anthropic-инструмент для улучшения ответа.
      - Возвращаем JSON с итоговым ответом.
    """
    data = await request.json()
    question = data.get("message", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in cookies")
    
    answer, _ = agent_instance.run_agent(question, user_id=user_id)
    

    # Улучшаем ответ через Anthropic-инструмент
    enhanced_answer = anthropic_tool.process_request(answer)
    
    return JSONResponse(content={"response": enhanced_answer})
