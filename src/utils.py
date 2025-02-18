import peewee
import json
import os
import psycopg2
from models import (
    area,
    service_plans,
    customer_data,
    active_faults,
    technician_data,
    supported_plans,
)
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# from langchain.vectorstores import Chroma
from langchain_chroma import Chroma


def init_vdb():
    if "COHERE_API_KEY" not in os.environ:
        print(
            "[isp_company_chatbot init] Cohere API key is not found in environment, importing from config file..."
        )
        with open("./../credentials.json", "r") as f:
            config = json.load(f)
            os.environ["COHERE_API_KEY"] = config["COHERE_API_KEY"]

    rec_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=0,
    )

    print("[isp_company_chatbot init] Loading documents...")
    consumer_packages = Docx2txtLoader("./data/consumer_packages.docx").load()
    enterprise_packages = Docx2txtLoader("./data/enterprise_packages.docx").load()
    payment_methods = Docx2txtLoader("./data/payment_methods.docx").load()

    print("[isp_company_chatbot init] Splitting documents...")
    doc_splits = rec_splitter.split_documents(
        consumer_packages + enterprise_packages + payment_methods
    )

    print("[isp_company_chatbot init] Adding documents to vector store...")
    cohere_api_key = os.environ["COHERE_API_KEY"]
    embed = CohereEmbeddings(model="embed-english-v3.0", cohere_api_key=cohere_api_key)
    vector_store = Chroma(
        collection_name="isp_products_information",
        embedding_function=embed,
        persist_directory="./../cvdb",
    )

    vector_store.add_documents(
        documents=doc_splits, ids=[str(i) for i in range(len(doc_splits))]
    )
    return {
        "documents": [
            "consumer_packages.docx",
            "enterprise_packages.docx",
            "payment_methods.docx",
        ]
    }


def init_db_and_acc():
    config = {}
    print(os.environ)
    if "POSTGRES_USER" not in os.environ:
        with open("./../credentials.json", "r") as f:
            config = json.load(f)
            os.environ["POSTGRES_USER"] = config["db"]["root"]["user"]
            os.environ["POSTGRES_PASSWORD"] = config["db"]["root"]["password"]
            os.environ["DB_HOST"] = config["db"]["host"]
            os.environ["DB_PORT"] = config["db"]["port"]

            os.environ["LLM_DB_USER"] = config["db"]["llm"]["user"]
            os.environ["LLM_DB_PASSWORD"] = config["db"]["llm"]["password"]

    print("[isp_company_chatbot init] Connecting to the PG database...")
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

    # Create database if not exist
    cursor = conn.cursor()
    conn.autocommit = True
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'isp_company_data'")
    db_exists = cursor.fetchone()
    if not db_exists:
        print("[isp_company_chatbot init] DB not found, Creating database...")
        cursor.execute("CREATE DATABASE isp_company_data")

    # Create a read-only account for the LLM, in the real world you
    #  just need to create the account for the database, and do checks on SELECT ON ALL TABLES

    try:
        print(
            "[isp_company_chatbot init] LLM account not found, Creating LLM account..."
        )
        cursor.execute(
            f"CREATE USER {os.environ['LLM_DB_USER']} WITH PASSWORD '{os.environ['LLM_DB_PASSWORD']}'"
        )
        cursor.execute(
            f"GRANT CONNECT ON DATABASE isp_company_data TO {os.environ['LLM_DB_USER']}"
        )
        cursor.execute(f"GRANT pg_read_all_data TO {os.environ['LLM_DB_USER']}")

        # Finish the database creation and the llm account creation process
        cursor.close()
        conn.close()
    except psycopg2.errors.DuplicateObject:
        pass

    return {
        "db": os.environ["DB_HOST"],
        "username": os.environ["LLM_DB_USER"],
        "password": os.environ["LLM_DB_PASSWORD"],
    }


def insert_data_to_db():
    # Connect to database
    config = {}
    if "POSTGRES_USER" not in os.environ:
        with open("./../credentials.json", "r") as f:
            config = json.load(f)
            os.environ["POSTGRES_USER"] = config["db"]["root"]["user"]
            os.environ["POSTGRES_PASSWORD"] = config["db"]["root"]["password"]
            os.environ["DB_HOST"] = config["db"]["host"]
            os.environ["DB_PORT"] = config["db"]["port"]

    pwconn = peewee.PostgresqlDatabase(
        os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
    )

    pwconn.connect()
    print("[isp_company_chatbot init] Creating tables...")
    pwconn.create_tables(
        [
            area,
            service_plans,
            customer_data,
            active_faults,
            technician_data,
            supported_plans,
        ]
    )

    print("[isp_company_chatbot init] Inserting data...")
    # Parse data from JSON file
    with open("./data/postgres db/data.json", "r") as f:
        data = json.load(f)

    # Insert data into tables
    for table_name, table_data in data.items():
        table = eval(table_name)
        table.insert_many(table_data).on_conflict("ignore").execute()

    # Close database connection
    pwconn.close()
    return {
        "created_tables": [
            "area",
            "service_plans",
            "customer_data",
            "active_faults",
            "technician_data",
            "supported_plans",
        ]
    }
