### Hallucination Grader
from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


# Data model
class DMHallucinationGrader(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )


class GradeHallucinations:
    preamble = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. Nothing outside of the provided facts. \n
    Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""

    def __init__(self, **kwargs):
        self.llm = (
            ChatCohere(model=kwargs["model_name"], temperature=0)
            if "model_name" in kwargs
            else ChatCohere(model="command-r-plus", temperature=0)
        )
        self.preamble = kwargs["preamble"] if "preamble" in kwargs else self.preamble

    def is_grounded(self, x):
        structured_llm_grader = self.llm.with_structured_output(DMHallucinationGrader)

        hallucination_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.preamble),
                (
                    "human",
                    "Set of facts: \n\n {documents} \n\n LLM generation: {generation}",
                ),
            ]
        )

        hallucination_grader = hallucination_prompt | structured_llm_grader
        return hallucination_grader.invoke(
            {"documents": x["documents"], "generation": x["generation"]}
        )


# def grade_hallucinations(docs, generation):
#     # Preamble
#     preamble = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. Nothing outside of the provided facts. \n
#     Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""

#     # LLM with function call
#     hallu_checker_llm = ChatCohere(model="command-r-plus", temperature=0)
#     structured_llm_grader = hallu_checker_llm.with_structured_output(
#         GradeHallucinations, preamble=preamble
#     )

#     # Prompt
#     hallucination_prompt = ChatPromptTemplate.from_messages(
#         [
#             # ("system", system),
#             (
#                 "human",
#                 "Set of facts: \n\n {documents} \n\n LLM generation: {generation}",
#             ),
#         ]
#     )

#     hallucination_grader = hallucination_prompt | structured_llm_grader
#     hallucination_grader.invoke({"documents": docs, "generation": generation})

#     return hallucination_grader
