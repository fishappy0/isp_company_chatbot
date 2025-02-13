# Create pgdb and load json data to the tables
import peewee
import json
import psycopg2

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
    with open("./../credentials.json", "r") as f:
        config = json.load(f)

    print("[isp_company_chatbot init] Connecting to the PG database...")
    conn = psycopg2.connect(
        host=config["db"]["host"],
        port=config["db"]["port"],
        user=config["db"]["root"]["user"],
        password=config["db"]["root"]["password"],
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
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'llm'")
    llm_exists = cursor.fetchone()
    if not llm_exists:
        print(
            "[isp_company_chatbot init] LLM account not found, Creating LLM account..."
        )
        cursor.execute(
            f"CREATE USER {config['db']['llm']['user']} WITH PASSWORD '{config['db']['llm']['password']}'"
        )
        cursor.execute(
            f"GRANT CONNECT ON DATABASE isp_company_data TO {config['db']['llm']['user']}"
        )
        cursor.execute(f"GRANT pg_read_all_data TO {config['db']['llm']['user']}")

    # Finish the database creation and the llm account creation process
    cursor.close()
    conn.close()
    return {
        "db": config["db"]["database"],
        "username": config["db"]["llm"]["user"],
        "password": config["db"]["llm"]["password"],
    }


def insert_data_to_db():
    # Connect to database
    config = {}
    with open("./../credentials.json", "r") as f:
        config = json.load(f)

    pwconn = peewee.PostgresqlDatabase(
        config["db"]["database"],
        user=config["db"]["root"]["user"],
        password=config["db"]["root"]["password"],
        host=config["db"]["host"],
        port=config["db"]["port"],
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
