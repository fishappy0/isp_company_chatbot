from rag import (
    GroqGenerator,
    HydeRetriever,
    SqlSearch,
    RetrievalGrader,
    AnswerGrader,
    GradeHallucinations,
    Router,
)


class rag_llm:
    def __init__(self, **kwargs):
        self.groq_generator = GroqGenerator()
        self.hyde_retriever = HydeRetriever()
        self.sql_search = SqlSearch(connection_string=kwargs["connection_string"])
        self.retrieval_grader = RetrievalGrader()
        self.answer_grader = AnswerGrader()
        self.grade_hallucinations = GradeHallucinations()
        self.router = Router()

    def fallback(self):
        return self.groq_generator.answer(
            {
                "question": "\n\n System: you are unable to answer the question at the moment. Please tell the user and then apologize"
            }
        )

    def answer(self, x):
        question = x["question"]
        tool_choice = self.router.get_route(question)  # QA & Routing
        ret = ""
        redis_session_id = x["redis_session_id"] if "redis_session_id" in x else None
        if "tool_calls" in tool_choice.response_metadata:  ### Vector DB Search route
            tool = tool_choice.response_metadata["tool_calls"][0]["function"]["name"]
            if tool == "VectorStore":
                docs = self.hyde_retriever.answer(
                    {"question": question}
                )  # Docs retrieved from choma with HyDe
                grade = self.retrieval_grader.is_relevant(
                    docs, question
                )  # Relevant to question?
                if grade.is_relevant == "no":
                    return self.groq_generator.answer(
                        "\n\n"
                        + "System: Unable to find relevant documents. Apologize for the inconvenience."
                    )
                else:
                    is_grounded = False
                    regen_count = 3
                    while is_grounded == False:
                        ans = self.groq_generator.answer(
                            {
                                "question": question,
                                "data": docs,
                                "redis_session_id": (redis_session_id),
                            }
                        )
                        ret = ans["response"]
                        redis_session_id = ans["redis_session_id"]

                        hallu_check = self.grade_hallucinations.is_grounded(
                            {
                                "documents": docs,
                                "generation": ret,
                            }
                        )  # Hallucination checker
                        if hallu_check.binary_score == "yes":
                            is_grounded = True
                        regen_count -= 1
                        if regen_count == 0:
                            return {
                                "response": self.fallback(),
                                "redis_session_id": redis_session_id,
                            }

                    is_answered = self.answer_grader.has_answered(
                        {"question": x["question"], "generation": ret}
                    )  # Answer Grader
                    if is_answered.replace(".", "").lower() == "yes":
                        return {"response": ret, "redis_session_id": redis_session_id}
                    else:
                        return {
                            "response": self.fallback(),
                            "redis_session_id": redis_session_id,
                        }

            elif tool == "SqlSearch":  ### SQL Search route
                query = self.sql_search.generate_sql_query(x)
                data = self.sql_search.execute_query(
                    query
                )  # Data retrieved from sql database

                question_with_sql = (
                    x["question"]
                    + "\n\nWith the following SQL query: "
                    + query["query"]
                )

                grade = self.retrieval_grader.is_relevant(
                    data, question_with_sql
                )  # Relevant to question?
                is_grounded = False
                regen_count = 3
                while is_grounded == False:
                    ans = self.groq_generator.answer(
                        {
                            "question": question_with_sql,
                            "data": data,
                            "redis_session_id": (redis_session_id),
                        }
                    )
                    ret = ans["response"]
                    redis_session_id = ans["redis_session_id"]

                    hallu_check = self.grade_hallucinations.is_grounded(
                        {
                            "documents": data,
                            "generation": ret,
                        }
                    )  # Hallucination checker
                    if hallu_check.binary_score == "yes":
                        is_grounded = True
                    regen_count -= 1
                    if regen_count == 0:
                        return {
                            "response": self.fallback(),
                            "redis_session_id": redis_session_id,
                        }

                is_answered = self.answer_grader.has_answered(
                    {"question": x["question"], "generation": ret}
                )  # Answer Grader
                if is_answered.replace(".", "").lower() == "yes":
                    return {"response": ret, "redis_session_id": redis_session_id}
                else:
                    return {
                        "response": self.fallback(),
                        "redis_session_id": redis_session_id,
                    }
        else:
            return {"response": self.fallback(), "redis_session_id": redis_session_id}
