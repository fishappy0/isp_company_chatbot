from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


# Data model
class SqlSearch(BaseModel):
    """
    Sql database search. Use sql database search for information about internet service plans and supported areas, customer data, active faults, technician data, and supported plans.
    """

    query: str = Field(description="The query to use when searching the sql database")


class VectorStore(BaseModel):
    """
    A vectorstore containing documents related to consumer packages, enterprise packages, and payment methods, but does not include the specific detail on which plans are supported where.
    """

    query: str = Field(description="The query to use when searching the vectorstore.")


class Router:
    preamble = """You are an expert at routing a user question to a vectorstore or sql search.
    The vectorstore contains advertisements documents related to consumer packages, enterprise packages, and payment methods.
    Use the vectorstore for questions on these topics. The sql search contains information about internet service plans and supported areas, customer data, active faults, technician data, and supported plans. 
    Use the sql search for questions on these topics. Otherwise, if unrelated to any topic above or unsure say unsupported, don't say anything else, don't try to route."""

    def __init__(self, **kwargs):
        self.llm = (
            ChatCohere(model=kwargs["model_name"], temperature=0)
            if "model_name" in kwargs
            else ChatCohere(model="command-r-plus", temperature=0)
        )
        self.preamble = kwargs["preamble"] if "preamble" in kwargs else self.preamble

    def get_route(self, x):
        # LLM with tool use and preamble
        llm = ChatCohere(model="command-r-plus", temperature=0)
        structured_llm_router = llm.bind_tools(
            tools=[SqlSearch, VectorStore], preamble=self.preamble
        )

        # Prompt
        route_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{question}"),
            ]
        )

        question_router = route_prompt | structured_llm_router

        # Unrelated question test
        response = question_router.invoke({"question": x})

        return response
