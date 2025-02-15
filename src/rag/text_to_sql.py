from langchain_community.utilities import sql_database
from langchain_community.tools import QuerySQLDatabaseTool
from langchain_groq import ChatGroq
from langchain import hub
from typing import TypedDict, Annotated


class QueryOutput(TypedDict):
    query: Annotated[str, ..., "Syntactically valid SQL query."]


class SqlSearch:
    def __init__(self, **kwargs):
        self.llm = (
            ChatGroq(model=kwargs["model_name"], temperature=0)
            if "model_name" in kwargs
            else ChatGroq(model="mixtral-8x7b-32768", temperature=0)
        )
        self.connection_string = kwargs["connection_string"]
        self.sql_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

    def generate_sql_query(self, question: str) -> QueryOutput:
        db = sql_database.SQLDatabase.from_uri(self.connection_string)
        prompt = self.sql_prompt_template.invoke(
            {
                "dialect": db.dialect,
                "top_k": 10,
                "table_info": db.get_table_info(),
                "input": question,
            }
        )

        structured_llm = self.llm.with_structured_output(QueryOutput)
        result = structured_llm.invoke(prompt)
        return {"query": result["query"]}

    def execute_query(self, query: str):
        db = sql_database.SQLDatabase.from_uri(self.connection_string)
        return QuerySQLDatabaseTool(db=db).invoke(query)
