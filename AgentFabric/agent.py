import os
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from operator import itemgetter

import faiss  # убедитесь, что установлен faiss-cpu (или faiss-gpu)
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.document_loaders import CSVLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import AIMessage, HumanMessage
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain.agents import Tool, AgentExecutor, create_tool_calling_agent
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate
)
from langchain.docstore.in_memory import InMemoryDocstore


class Agent(ABC):
    @abstractmethod
    def run_agent(self, question: str, user_id: str) -> tuple[str, List[str]]:
        pass


class LangChainAgent(Agent):
    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0.5, openai_api_key=api_key)
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.vectorstores: Dict[str, FAISS] = {}  # хранилища для статичных источников (например, данные о коктейлях)
        self.tools: List[Tool] = []
        self.agent_executor: Optional[AgentExecutor] = None

        # Словарь для хранения индивидуальных векторных баз истории для каждого пользователя
        self.user_history_stores: Dict[str, FAISS] = {}

        # Дополнительно создаём общее (пустое) хранилище, если потребуется (не используется напрямую)
        self.history_vectorstore = self.create_empty_faiss()

    def create_empty_faiss(self) -> FAISS:
        """
        Создаёт пустой FAISS индекс для хранения истории, вычисляя размерность эмбеддинга.
        Используем InMemoryDocstore, поддерживающий добавление элементов.
        """
        dummy_embedding = self.embeddings.embed_query("dummy")
        dim = len(dummy_embedding)
        index = faiss.IndexFlatL2(dim)
        docstore = InMemoryDocstore({})  # docstore с сохранением порядка вставки
        return FAISS(embedding_function=self.embeddings, index=index, docstore=docstore, index_to_docstore_id={})

    def get_user_history_store(self, user_id: str) -> FAISS:
        """Возвращает FAISS-хранилище истории для указанного пользователя.
           Если хранилище ещё не создано, создаёт новое пустое."""
        if user_id not in self.user_history_stores:
            self.user_history_stores[user_id] = self.create_empty_faiss()
        return self.user_history_stores[user_id]

    def load_data_and_create_faiss(self, file_paths: List[str], csv_args: Optional[Dict[str, str]] = None) -> None:
        csv_args = csv_args or {}

        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1].lower()
            file_name = os.path.splitext(file_name)[0].lower()

            if file_extension == '.csv':
                csv_arg = csv_args.get(file_name.split('.')[0])
                if not csv_arg:
                    raise ValueError(f"csv_args column for {file_name} not provided.")
                loader = CSVLoader(file_path=file_path, csv_args=csv_arg)
                data = loader.load_and_split()
            elif file_extension == '.pdf':
                loader = PyPDFLoader(file_path)
                data = loader.load_and_split()
            else:
                raise ValueError(f"Unsupported file format: {file_extension}. Only .csv and .pdf files are supported.")

            self.vectorstores[file_name] = FAISS.from_documents(data, self.embeddings)

    def create_tool(self, review_chain, tool_name, tool_description):
        @tool()
        def generated_tool(question: str) -> str:
            """Временный докстринг для инструмента"""
            return review_chain.invoke({"question": question})
        generated_tool.name = tool_name
        generated_tool.description = tool_description
        return generated_tool

    def generate_tools(self, 
                       context_key: str = "question", 
                       tool_data: Optional[Dict[str, str]] = None,
                       tool_system_prompts: Optional[Dict[str, str]] = None) -> None:
        tool_data = tool_data or {}
        tool_system_prompts = tool_system_prompts or {}
        
        for file_name, vectorstore in self.vectorstores.items():
            retriever = vectorstore.as_retriever()

            setup_and_retrieval = RunnablePassthrough.assign(
                context=itemgetter(context_key) | retriever
            )

            system_prompt = tool_system_prompts.get(file_name, "You are a helpful assistant.")
            dynamic_system_prompt_template = SystemMessagePromptTemplate(
                prompt=PromptTemplate(template=system_prompt)
            )

            review_human_prompt = HumanMessagePromptTemplate(
                prompt=PromptTemplate(
                    input_variables=["question", "context"],
                    template="""You need to answer the [question] using data from the [context].
[context]
{context}

[question]
{question}"""
                )
            )
            messages = [dynamic_system_prompt_template, review_human_prompt]
            review_prompt_template = ChatPromptTemplate(
                input_variables=["context", "question"],
                messages=messages,
            )

            review_chain = setup_and_retrieval | review_prompt_template | self.llm | StrOutputParser()

            tool_name = file_name
            tool_description = tool_data.get(tool_name, "Default tool description")
            generated_tool = self.create_tool(review_chain, tool_name, tool_description)
            self.tools.append(generated_tool)

    def create_agent(self, system_prompt: str) -> None:
        agent = create_tool_calling_agent(self.llm, self.tools, system_prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools)

    def run_agent(self, question: str, user_id: str) -> tuple[str, List[str]]:
        """
        Обрабатывает запрос для данного user_id, используя историю, сохранённую в индивидуальном FAISS-хранилище.
        Для этого:
          - Из хранилища извлекаются все документы (сообщения) в порядке вставки.
          - Полученная история (список строк) преобразуется в список LangChain-сообщений:
                на четных позициях – HumanMessage, на нечетных – AIMessage.
          - Этот список передаётся в цепочку как "chat_history".
          - После получения нового ответа новые сообщения (вопрос и ответ) добавляются в хранилище с порядковыми идентификаторами.
        Возвращается кортеж: (ответ, полный список сообщений в виде строк).
        """
        if not self.agent_executor:
            raise RuntimeError("Agent not created. Call create_agent() before using.")

        user_history_store = self.get_user_history_store(user_id)
        # Получаем словарь из docstore; предполагается, что ключи – строки, представляющие порядковые номера
        all_docs = user_history_store.docstore._dict  # _dict хранит документы
        ordered_keys = sorted(all_docs.keys(), key=lambda x: int(x))
        chat_history = [all_docs[k].page_content for k in ordered_keys]

        # Преобразуем историю в список сообщений LangChain
        langchain_chat_history = []
        for i, message in enumerate(chat_history):
            if i % 2 == 0:
                langchain_chat_history.append(HumanMessage(content=message))
            else:
                langchain_chat_history.append(AIMessage(content=message))
        
        response = self.agent_executor.invoke({
            "input": question,
            "chat_history": langchain_chat_history
        })
        answer = response["output"]

        next_id = len(ordered_keys)
        # Добавляем новое сообщение пользователя и ответ агента в хранилище с указанными id
        user_history_store.add_texts([question, answer], ids=[str(next_id), str(next_id + 1)])
        
        new_chat_history = chat_history + [question, answer]
        return answer, new_chat_history
