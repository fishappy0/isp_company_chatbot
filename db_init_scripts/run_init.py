"""
THIS PROCESS WILL NOT EXIST IN A REAL PROJECT
THIS IS JUST FOR DEMONSTRATION OF THIS PROOF OF CONCEPT PROJECT
"""

from init_db import init_db_and_acc, insert_data_to_db
from init_vdb import init_vdb

# print("[isp_company_chatbot init] Initializing database...")
# init_db_and_acc()
# insert_data_to_db()
print("[isp_company_chatbot init] Initializing vector database...")
init_vdb()
print("[isp_company_chatbot init] Initialization complete!")
