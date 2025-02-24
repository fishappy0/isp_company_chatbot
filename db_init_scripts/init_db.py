# Create pgdb and load json data to the tables
import peewee
import json
import psycopg2
import os

from models import (
    area,
    service_plans,
    customer_data,
    active_faults,
    technician_data,
    supported_plans,
)


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
    cursor.execute(
        f"SELECT 1 FROM pg_roles WHERE rolname = {os.environ['LLM_DB_USER']}"
    )
    llm_exists = cursor.fetchone()
    if not llm_exists:
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
    with open("./../data/postgres db/data.json", "r") as f:
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
