import os
import json
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
    consumer_packages = Docx2txtLoader("./../data/consumer_packages.docx").load()
    enterprise_packages = Docx2txtLoader("./../data/enterprise_packages.docx").load()
    payment_methods = Docx2txtLoader("./../data/payment_methods.docx").load()

    print("[isp_company_chatbot init] Splitting documents...")
    doc_splits = rec_splitter.split_documents(
        consumer_packages + enterprise_packages + payment_methods
    )

    print("[isp_company_chatbot init] Adding documents to vector store...")
    embed = CohereEmbeddings(model="embed-english-v3.0")
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
