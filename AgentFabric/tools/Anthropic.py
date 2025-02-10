from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class AnthropicLLMTool:
    def __init__(self, system_prompt:str, model_name: str = "claude-3-5-sonnet-20240620"):
        self.model = ChatAnthropic(model=model_name)
        self.system_prompt = system_prompt


    def process_request(self, user_prompt: str) -> str:
        prompt = ChatPromptTemplate.from_messages(
           [
            (
                "system",
                self.system_prompt,
            ),
            ("human", "Your goal is to make the text more realistic and human-like, as if written by a person. Do not write a lengthy response; just edit the current text. Do not include these instructions in your response. Respond only with the [revised text] in the text below:(do not use [revised text] in answer)\n\n[revised text]\n{input}"),
            ]
        )
        chain = prompt | self.model | StrOutputParser()
        return chain.invoke({"input":user_prompt})


