from pydantic import BaseModel, Field
from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate


class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    is_relevant: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


class RetrievalGrader:
    # Prompt
    preamble = """You are a grader assessing relevance of a retrieved document or data to a user question. \n
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
    If the data is related to the user question based on the provided PostgreSQL query, grade it as relevant. \n
    Answer with 'yes' or 'no' score to indicate whether the document is relevant to the question.
    """

    def __init__(self, **kwargs):
        self.llm = (
            ChatCohere(model=kwargs["model_name"], temperature=0)
            if "model_name" in kwargs
            else ChatCohere(model="command-r-plus", temperature=0)
        )
        self.preamble = kwargs["preamble"] if "preamble" in kwargs else self.preamble

    # LLM with function call
    def is_relevant(self, docs, question):
        structured_llm_grader = self.llm.with_structured_output(
            GradeDocuments, preamble=self.preamble
        )

        grade_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "human",
                    "Retrieved document: \n\n {document} \n\n User question: {question} \n\n Based on the initial instructions answer with just 'yes' or 'no' dont try to say anything else",
                ),
            ]
        )

        retrieval_grader = grade_prompt | structured_llm_grader
        return retrieval_grader.invoke({"question": question, "document": docs})
