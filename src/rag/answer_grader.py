from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


# # Preamble
class AnswerGrader:
    preamble = """You are a grader assessing whether an answer addresses OR resolves a question AND is related to the scope of an internet service provider. \n
    Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""

    def __init__(self, **kwargs):
        self.llm = (
            ChatGroq(model_name=kwargs["model_name"], temperature=0)
            if "model_name" in kwargs
            else ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        )
        self.preamble = kwargs["preamble"] if "preamble" in kwargs else self.preamble

    def has_answered(self, x):
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(self.preamble),
                HumanMessage(f"Question: {x['question']} \nAnswer: {x['generation']}"),
            ]
        )
        grader_chain = prompt | self.llm
        return grader_chain.invoke(
            {"question": x["question"], "generation": x["generation"]}
        ).content


# # LLM with function call
# groq_grader = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)


# # Prompt
# def prompt(x):
#     return ChatPromptTemplate.from_messages(
#         [
#             SystemMessage(preamble),
#             HumanMessage(f"Question: {x['question']} \nAnswer: {x['generation']}"),
#         ]
#     )


# grader_chain = prompt | groq_grader
# grader_chain.invoke({"question": test_question, "generation": test_generation})
