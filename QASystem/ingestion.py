from QASystem.logger import logging

logging.info("Entering Ingestion Module")

import os

from dotenv import load_dotenv

from langchain_ai21 import AI21Embeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import PGVector
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.document_loaders import CSVLoader, PyPDFLoader

from QASystem.db_connector import connection_string
from QASystem.constants import *

logger = logging.info("\nData Ingestion Processing File Initialization")
load_dotenv()

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

key=os.getenv("HUGGINGFACEHUB_API_TOKEN")

embeddings = AI21Embeddings(api_key=os.getenv("AI21_API_KEY"))

class DataIngestionProcessing:
    logger = logging.info("Data Ingestion Processing Started")
    def __init__(self, file_path):
        self.file_path = file_path

    def split_data(self):
        # Determine the file type based on the extension
        _ ,file_extension = os.path.splitext(self.file_path)

        if file_extension.lower() == '.csv':
            logging.info(f"Reading CSV file : {self.file_path}")
            loader = CSVLoader(self.file_path)

        elif file_extension.lower() == '.xlsx':
            logging.info(f"Reading Excel file : {self.file_path}")
            loader=UnstructuredExcelLoader(self.file_path, mode="elements")

        elif file_extension.lower() == '.pdf':
            logging.info(f"Reading PDF file {self.file_path}")
            loader=PyPDFLoader(self.file_path)

        else:
            raise ValueError(f"File extension {file_extension} not supported")


        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size= 1000, chunk_overlap=150)
        docs = text_splitter.split_documents(data)
        return docs


    def push_data_db(self, docs):
        print('Converting Embedding into Vectors')
        logging.info(f"Pushing Started Total {len(docs)} number of documents into database")
        PGVector.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name=PGSQL_COLLECTION_NAME,
            connection_string=connection_string,
            pre_delete_collection=False
        )
        print(f"{self.file_path} is Pushed successfully into {PGSQL_COLLECTION_NAME}")
        logging.info(f"\nPushing Finished Total {len(docs)} number of documents into database")
        logging.info(f"\nExiting Data Ingestion Processing File Initialization")







