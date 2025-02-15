from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


# Data model
class sql_Search(BaseModel):
    """
    Sql database search. Use sql database search for information about internet service plans and supported areas, customer data, active faults, technician data, and supported plans.
    """

    query: str = Field(description="The query to use when searching the sql database")


class vectorstore(BaseModel):
    """
    A vectorstore containing documents related to consumer packages, enterprise packages, and payment methods, but does not include the specific detail on which plans are supported where.
    """

    query: str = Field(description="The query to use when searching the vectorstore.")


def answer(question):
    # Preamble
    preamble = """You are an expert at routing a user question to a vectorstore or sql search.
    The vectorstore contains advertisements documents related to consumer packages, enterprise packages, and payment methods.
    Use the vectorstore for questions on these topics. The sql search contains information about internet service plans and supported areas, customer data, active faults, technician data, and supported plans. 
    Use the sql search for questions on these topics. Otherwise, if unrelated to any topic above or unsure say unsupported, don't say anything else, don't try to route."""

    # LLM with tool use and preamble
    llm = ChatCohere(model="command-r-plus", temperature=0)
    structured_llm_router = llm.bind_tools(
        tools=[sql_Search, vectorstore], preamble=preamble
    )

    # Prompt
    route_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{question}"),
        ]
    )

    question_router = route_prompt | structured_llm_router

    # Unrelated question test
    response = question_router.invoke(
        {"question": "Who will the Bears draft first in the NFL ?"}
    )

    return response
