import os
from rag import GroqFallbackLLM
import json

credentials = {}
with open("./../credentials.json", "r") as f:
    credentials = json.load(f)

os.environ["COHERE_API_KEY"] = credentials["COHERE_API_KEY"]
os.environ["GROQ_API_KEY"] = credentials["GROQ_API_KEY"]

test_llm = GroqFallbackLLM()
print(test_llm.answer({"question": "Can you combine both modem and router?"}))
