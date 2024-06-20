import os

import psycopg2
from dotenv import load_dotenv

from QASystem.logger import logging
from QASystem.constants import *

from langchain.vectorstores.pgvector import PGVector
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()
#print(os.getenv('PGSQL_DB_PASSWORD'))
#print(os.getenv('PGSQL_DB_HOST'))

# Database connection parameter
user=PGSQL_DB_USER_NAME
database_name=PGSQL_DATABASE_NAME
host=os.getenv('PGSQL_DB_HOST')
password=os.getenv('PGSQL_DB_PASSWORD')
collection=PGSQL_COLLECTION_NAME

try:
    logging.info("Connecting to PostgreSQL database...")
    # Start connection to the database
    conn = psycopg2.connect(
        dbname=database_name,
        user=user,
        host=host,
        password=password,
        port=PGSQL_PORT
    )
    logging.info(f"Connected to PostgreSQL DB {conn}")
    logging.info("Connection successful...")
    # Create a cursor object using the cursor()
    cursor = conn.cursor()

    # Execute SQL Query
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"PGSQL Database version: {db_version}")

    # closing the cursor
    cursor.close()
    conn.close()
    print(f"PGSQL Database connection closed")

except (Exception, psycopg2.DatabaseError) as error:
    print(f"Error while connecting the PostgreSQL : {error}")


logging.info("Started creating the connection string")
connection_string = PGVector.connection_string_from_db_params(host=host,
                                    driver=PGVECTOR_DRIVER,
                                    port=PGSQL_PORT,
                                    database=database_name,
                                    user=user,
                                    password=password)


logging.info("Connection string created")
logging.info(f"The connection string is {connection_string}")
logging.info(f"Collection names is {collection}")

