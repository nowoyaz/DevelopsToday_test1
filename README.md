# Cocktail Advisor Chat

Cocktail Advisor Chat — это FastAPI-приложение, использующее LangChain-агент для ответов на вопросы о коктейлях. Система интегрирует векторную базу данных (FAISS) для персонализированной истории общения с каждым пользователем. Для улучшения качества ответов используется Anthropic LLM.

## Основные возможности

- **LLM-интеграция**: Приложение использует OpenAI GPT-4o и Anthropic LLM (через LangChain) для предоставления экспертных ответов.
- **Персонализированная история**: Каждый пользователь получает индивидуальное хранилище FAISS для сохранения истории чатов.
- **RAG (Retrieval-Augmented Generation)**: Агент извлекает релевантные сообщения из истории пользователя для формирования контекстно-зависимых ответов.
- **Гибкая настройка промптов**: Все системные и инструментальные промпты хранятся в `data/prompts.json`, что позволяет легко изменять поведение бота.
- **Модульная архитектура**: Агент вынесен в `AgentFabric` - фабрика для быстрого создания агентов, а серверная логика находится в `app/routes`, что делает код удобным для поддержки и расширения.

## Установка и запуск

### Предварительные требования

- Python 3.12.5

### Установка

1. **Клонирование репозитория**

   ```bash
   git clone https://github.com/nowoyaz/DevelopsToday_test1.git
   ```

2. **Создание и активация виртуального окружения**

   - На macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

   - На Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Установка зависимостей**

   ```bash
   pip install -r requirements.txt
   ```

4. **Настройка переменных окружения**

   Создайте файл `.env` в корневой директории проекта и добавьте:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

5. **Запуск приложения**

   ```bash
   uvicorn app.main:app --reload
   ```

6. **Открытие в браузере**

   Перейдите в [http://localhost:8000](http://localhost:8000).

## О проекте

Основная цель проекта — создание интеллектуального чат-бота для ответов на вопросы о коктейлях, используя передовые языковые модели. Важные аспекты реализации:

- **Разделение логики**: Агент вынесен в отдельный модуль `AgentFabric`, а серверная часть структурирована в `app/routes`.
- **Персонализированное хранение истории**: FAISS используется для сохранения истории диалога пользователей и сохранения информации для конекстов.
- **Поддержка Anthropic LLM**: Используется для повышения качества и читабельности ответов в силу лучших показателей с человеческой речью.
- **Гибкая настройка через JSON**: Все промпты хранятся в `data/prompts.json`, позволяя изменять поведение бота без редактирования кода.



## Контакты

По вопросам и предложениям: [dumpline0@gmail.com], https://t.me/nowoyaz
