import os

from QASystem.logger import logging
from QASystem.ingestion import DataIngestionProcessing
from QASystem.retreiver import ResponseApp
from QASystem.constants import DATA_FILE_PATH
import uuid
from datetime import datetime

from colorama import Fore, Style
import pyfiglet

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
# Initialize colorama
from colorama import init

from datetime import date

today = str(date.today())

def append2log(text):
    global today
    fname = 'chatlog-' + today + '.txt'
    with open(fname, "a", encoding='utf-8') as f:
        f.write(text + "\n")
        f.close


session_id = str(uuid.uuid4())

#IngestionProcessing = DataIngestionProcessing(file_path=DATA_FILE_PATH)
#docs = IngestionProcessing.split_data()
#IngestionProcessing.push_data_db(docs)
"""
def final_retriever(session_id=None):
    try:
        DataIngestionProcessingfile_path=DATA_FILE_PATH)
        docs = IngestionProcessing.split_data()
        IngestionProcessing.push_data_db(docs)
    except Exception as e:
        pass
"""

class user_response:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        init()

    def Ingestion_data(self, file_path):
        IngestionProcessing =DataIngestionProcessing(file_path=file_path)
        docs = IngestionProcessing.split_data()
        IngestionProcessing.push_data_db(docs)

    def response_generator(self):
        title = pyfiglet.figlet_format("Fancy Input")
        print(Fore.CYAN + title + Style.RESET_ALL)
        append2log(f'session_id: {self.session_id}')
        while True:
            append2log(f'\n')
            user_input = input(Fore.GREEN + "Please ask your question: " + Style.RESET_ALL)
            append2log(f"User Question : {user_input} ")
            api = ResponseApp(session_id=self.session_id, user_input=user_input)
            response = api.generate_response()
            append2log(f"AI Response : {response}")
            print(Fore.MAGENTA + f"AI Response: {response}" + Style.RESET_ALL)
            print('-------------------------------------------------')
            #print(response)

    def append2log(self, text):
        global today
        fname = 'chatlog-' + datetime.now().strftime('%m_%d_%Y_%H_%M_%S') + '.txt'
        with open(fname, "a", encoding='utf-8') as f:
            f.write(text + "\n")
        f.close




if __name__ == "__main__":
    user_response = user_response()
    user_response.Ingestion_data(file_path=DATA_FILE_PATH)
    user_response.response_generator()