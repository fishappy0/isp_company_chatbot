import os
from rag import GroqGenerator
import json

credentials = {}
with open("./../credentials.json", "r") as f:
    credentials = json.load(f)

config = {}
with open("./../config.json", "r") as f:
    config = json.load(f)

os.environ["COHERE_API_KEY"] = credentials["COHERE_API_KEY"]
os.environ["GROQ_API_KEY"] = credentials["GROQ_API_KEY"]
os.environ["REDIS_URL"] = config["REDIS_URL"]

test_llm = GroqGenerator()
print(
    test_llm.answer(
        {
            "question": "Thank you, I guess I will have to call you guys and schedule an upgrade appointment. I think that's it for now.",
            "data": "Currently there is a service disruption on Elm st, due to a severed fiber optic line caused by heavy weather. Team dispatched, repair time 2 hours",
            # "redis_session_id": "d8d2ffa5cfc84555be1fbfc0b36bf2f7",
        }
    )
)
