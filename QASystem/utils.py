import constants
from db_connector import conn
from logger import logging
from logger import logging
from constants import *

import os
import psycopg2

import warnings
warnings.filterwarnings("ignore")


conn = psycopg2.connect(
        dbname=constants.PGSQL_DATABASE_NAME,
        user=PGSQL_DB_USER_NAME,
        host=os.getenv('PGSQL_DB_HOST'),
        password=os.getenv('PGSQL_DB_PASSWORD'),
        port=PGSQL_PORT
    )

def database_creation(database_name=None):
    try:
        if database_name is not None:
            logging.info(f"Connecting to PGSQL and checking the Existing and start Creating {database_name}")
            cursor = conn.cursor()
            cursor.execute(f"SELECT datname FROM pg_database WHERE datistemplate = false;")
            rows = cursor.fetchall()

            database_exist = []
            for row in rows:
                database_exist.append(row[0])
                logging.info(f"List of database already exist {database_exist}")

            if database_name not in database_exist:
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE {database_name};")
                cursor.close()
                logging.info(f"\nNew Database {database_name} created successfully")
            else:
                logging.info(f"Database {database_name} is already exists")

            print(f"PGSQL Database connection closed")
        else:
            logging.info(f"\nDatabase Name is None")

    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    database_creation(database_name='testing')





