import os
import json
from llm import rag_llm

credentials = {}
with open("./../credentials.json", "r") as f:
    credentials = json.load(f)

config = {}
with open("./../config.json", "r") as f:
    config = json.load(f)

os.environ["COHERE_API_KEY"] = credentials["COHERE_API_KEY"]
os.environ["GROQ_API_KEY"] = credentials["GROQ_API_KEY"]
os.environ["LANGSMITH_API_KEY"] = credentials["LANGSMITH_API_KEY"]
os.environ["REDIS_URL"] = config["REDIS_URL"]

os.environ["LANGSMITH_TRACING"] = config["debug"]["LANGSMITH_TRACING"]
os.environ["LANGSMITH_ENDPOINT"] = config["debug"]["LANGSMITH_ENDPOINT"]
os.environ["LANGSMITH_PROJECT"] = config["debug"]["LAMGSMITH_PROJECT"]

connection_string = f"postgresql://{credentials['db']['llm']['user']}:{credentials['db']['llm']['password']}@{credentials['db']['host']}:{credentials['db']['port']}/{credentials['db']['database']}"
llm = rag_llm(connection_string=connection_string)
print(
    llm.answer(
        {
            # # "question": "My name is John Doe, I live in 123 Elm street, what packages are available in my area?",
            # # "question": "What is the speed of the Sky and giga package? tell me the price as well",
            # "redis_session_id": "ae2bbac96bd1f8f3e59526fac3c",
        }
    )
)
# router = Router()
# print(
#     router.get_route(
#         {
#             "question": "My name is John Doe, I live in 123 Elm street, what packages are available in my area?"
#         }
#     ).response_metadata["tool_calls"][0]["function"]["name"]
# )
# hallu_grader = GradeHallucinations()
# print(
#     hallu_grader.is_hallucinated(
#         {
#             "documents": [
#                 "there are currently a service disruption on Elm st, due to a severed fiber optic line caused by heavy weather",
#                 "The repair is going to take 2 hours",
#             ],
#             "generation": "Currently there is a service disruption on Elm st, due to a severed fiber optic line caused by heavy weather. Team dispatched, repair time 2 hours",
#         }
#     )
# )

# ans_grader = AnswerGrader()
# print(
#     ans_grader.has_answered(
#         {
#             "question": "What is the router of the lux 800 package?",
#             "generation": "The Lux 800 package provides customers with 2 devices: a Modem AX8000C and a Mesh AX8000C. These are Wi-Fi 6 enabled devices that can help create a strong and stable internet connection throughout your home or workplace.",
#         }
#     )
# )

# os.environ["LANGSMITH_TRACING"] = config["debug"]["LANGSMITH_TRACING"]
# os.environ["LANGSMITH_ENDPOINT"] = config["debug"]["LANGSMITH_ENDPOINT"]
# os.environ["LANGSMITH_PROJECT"] = config["debug"]["LAMGSMITH_PROJECT"]

# sql_query_retriever = SqlSearch(
#     connection_string=f"postgresql://{credentials['db']['llm']['user']}:{credentials['db']['llm']['password']}@{credentials['db']['host']}:{credentials['db']['port']}/{credentials['db']['database']}"
# )
# retrieval_grader = RetrievalGrader()
# hyde_retriever = HydeRetriever()

# q = "My name is John Doe, I live in 123 Elm street, what packages are available in my area?"
# query = sql_query_retriever.generate_sql_query({"question": q})
# ret = sql_query_retriever.execute_query(query)
# q = q + "\n\nWith the following SQL query: " + str(query)

# # q = "What is the router of the lux 800 package?"
# # ret = hyde_retriever.answer({"question": q})

# print(str(ret))

# print(retrieval_grader.is_relevant(ret, q).is_relevant)

# retriever = HydeRetriever()
# # print(
#     retriever.answer(
#         {
#             "question": "What is the router of the lux 800 package?",
#         }
#     )
# )
# test_llm = GroqGenerator()
# print(
#     test_llm.answer(
#         {
#             "question": "Thank you, I guess I will have to call you guys and schedule an upgrade appointment. I think that's it for now.",
#             "data": "Currently there is a service disruption on Elm st, due to a severed fiber optic line caused by heavy weather. Team dispatched, repair time 2 hours",
#             # "redis_session_id": "d8d2ffa5cfc84555be1fbfc0b36bf2f7",
#         }
#     )
# )
