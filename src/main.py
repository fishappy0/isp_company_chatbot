import os
import json
import peewee
import streamlit as st
from llm import rag_llm

from utils import init_db_and_acc, insert_data_to_db, init_vdb
from models import customer_data

credentials = {}

config = {}

if "COHERE_API_KEY" not in os.environ:
    with open("./../credentials.json", "r") as f:
        credentials = json.load(f)
        os.environ["COHERE_API_KEY"] = credentials["COHERE_API_KEY"]
        os.environ["GROQ_API_KEY"] = credentials["GROQ_API_KEY"]
        os.environ["LANGSMITH_API_KEY"] = credentials["LANGSMITH_API_KEY"]

    with open("./../config.json", "r") as f:
        config = json.load(f)
        os.environ["LANGSMITH_TRACING"] = config["debug"]["LANGSMITH_TRACING"]
        os.environ["LANGSMITH_ENDPOINT"] = config["debug"]["LANGSMITH_ENDPOINT"]
        os.environ["LANGSMITH_PROJECT"] = config["debug"]["LAMGSMITH_PROJECT"]

if "POSTGRES_USER" not in os.environ:
    with open("./../credentials.json", "r") as f:
        credentials = json.load(f)
        os.environ["POSTGRES_USER"] = credentials["db"]["root"]["user"]
        os.environ["POSTGRES_PASSWORD"] = credentials["db"]["root"]["password"]

connection_string = f"postgresql://{os.environ['LLM_DB_USER']}:{os.environ['LLM_DB_PASSWORD']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['POSTGRES_DB']}"
# connection_string = f"postgresql://{credentials['db']['llm']['user']}:{credentials['db']['llm']['password']}@{credentials['db']['host']}:{credentials['db']['port']}/{credentials['db']['database']}"

# Jank db insertion and initialization
# if not main thread
if os.environ["INIT_DB_ON_STARTUP"] == "TRUE":
    print("[isp_company_chatbot init] Initializing databases...")
    init_db_and_acc()
    pwdb = peewee.PostgresqlDatabase(
        os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
    )
    try:
        cursor = pwdb.execute_sql("SELECT * FROM customer_data;")
    except Exception as e:
        if "does not exist" in str(e):
            insert_data_to_db()
    init_vdb()
    print("[isp_company_chatbot init] Initialization complete!")
    os.environ["INIT_DB_ON_STARTUP"] = "false"

session_id = None
if "session_id" in st.session_state:
    session_id = st.session_state["session_id"]

st.title("ISP Company Chatbot")

if st.button("Clear chat history"):
    st.session_state.messages = []
chat_window = st.container()

if "messages" not in st.session_state:
    st.session_state.messages = []

with chat_window:
    if prompt := st.chat_input("Say hi to the chatbot"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        output = rag_llm(connection_string=connection_string).answer(
            {"question": prompt, "redis_session_id": session_id}
        )
        redis_session_id = str(output["redis_session_id"])
        response = str(output["response"])
        st.session_state.session_id = redis_session_id
        st.session_state.messages.append({"role": "assistant", "content": response})
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
