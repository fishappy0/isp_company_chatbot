from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
import chromadb
import os


class HydeRetriever:
    preample = """You are a summary assistant for question-answering tasks.
                Given the following question, generate a paragraph that answers the question."""

    def __init__(self, **kwargs):
        self.llm = (
            ChatGroq(model=kwargs["model_name"], temperature=0)
            if "model_name" in kwargs
            else ChatGroq(model="mixtral-8x7b-32768", temperature=0)
        )
        self.preample = kwargs["preamble"] if "preamble" in kwargs else self.preample

    def answer(self, x):
        if "question" not in x:
            raise ValueError("Missing question")

        retriever = Chroma(
            client=chromadb.PersistentClient(path="./../cvdb"),
            collection_name="isp_products_information",
            embedding_function=CohereEmbeddings(model="embed-english-v3.0"),
        ).as_retriever()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.preample),
                ("human", "{question}"),
            ]
        )
        chain = prompt | self.llm | StrOutputParser()
        hyde_doc = chain.invoke({"question": x["question"]})

        return retriever.invoke(hyde_doc)
