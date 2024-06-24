import os
import traceback

from QASystem.logger import logging

import boto3
from langchain_community.vectorstores import PGVector
from langchain.schema import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.memory import PostgresChatMessageHistory  # To store chat history

from langchain_ai21 import ChatAI21
from langchain_ai21 import AI21Embeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import re
from dotenv import load_dotenv
from QASystem.db_connector import connection_string

# local
from QASystem.constants import *

import warnings
warnings.filterwarnings("ignore")

import warnings
warnings.filterwarnings("ignore")

logging.info(f"Entering in retreiver mode")
load_dotenv()


host=os.getenv("PGSQL_DB_HOST")
database=PGSQL_DATABASE_NAME
os.environ['USER'] = 'postgres'
user = PGSQL_DB_USER_NAME
password = os.getenv("PGSQL_DB_PASSWORD")
collection_name = PGSQL_COLLECTION_NAME
ai21_api_key=os.getenv("AI21_API_KEY")
chat_hist_msg_count = CHAT_MESSAGES_HISTORY_COUNT
model_temp = AI21_MODEL_TEMP

logging.info("Environment variables loaded")


# Setting and intializing the bedrock and bedrock embedddings
session=boto3.Session()
logging.info("\nSuccesfully Intiating BOTO3 session")

embeddings = AI21Embeddings(api_key=ai21_api_key)
llm=ChatAI21(model='jamba-instruct',temperature=model_temp, max_tokens=4096,api_key=ai21_api_key)
logging.info("\nLoaded AI21 embedding and AI21 Model model successfully")

# Building PGvector string connection
logging.info("\nStarted creating the connection string")
logging.info(f"\nCollection names is {collection_name}")
logging.info(f"\nSuccesfully loaded the PGVector connection string : {connection_string}")

custom_prompt = """ 
        Your are a Chatbot, your goal is to answer the user question in a proper manner related to the given document only and which \
        question asked by the users. To answer that follow these guideline strictly.

        When it's an first conversation with use always greet them with a greeting message and "how may I assist you?"
        Understand the user question and then give the answer available database of question and answers.

        If you don't know the answer, just mention "I don't know about this, Please ask again"

        Make sure your AI answer should be having correct grammar's, point wise answers and properly explained way.

        Please generate properly formatted answer in markdown, and if it is new line or line gap in answer, please add double space then \n, 
        so I can render that answer as markdown at my app.

        {context}
        """

contextualize_system_prompt = """Given the chat history and latest user question, which might reference context in the chat history 
                            formulate the standalone question which can be understood without the chat history. 
                            Do Not answer the question, just reformulate it if needed and otherwise return it as is. """

logging.info(f"Completed the Prompt Settings")

class ResponseApp:
    def __init__(self, user_input, session_id):
        """
        :param user_input:
        :param session_id: It is used to store the chat history of each user and it should be unique always or for each session.
        """
        self.user_input = user_input
        self.session_id = session_id

    def format_docs(self, docs):
        return '\n'.join(doc.page_content for doc in docs)

    def clean_response(self, response):
        logging.info("Started Cleaning response")
        cleaned_response = re.sub(r'\s+', ' ', response).strip()
        cleaned_response = re.sub(r'[^a-zA-Z0-9\s,.!]', ' ', cleaned_response)
        logging.info("Cleaned response succesfully")
        return cleaned_response

    logging.info(f"Succesfully Cleaned response")

    def generate_response(self):
        logging.info("Started Generating response")
        try:
            logging.info("Started Generating response")
            vector_store = PGVector(collection_name=collection_name,
                                    connection_string=connection_string,
                                    embedding_function=embeddings
                                    )

            retreiver = vector_store.as_retriever(search_kwargs={'k': 20})

            system_prompt = custom_prompt
            logging.info(f"Following prompt as {system_prompt}")

            # I
            logging.info("\n Initiating the connection with PostgreSQL database to storing the chat history of each session")

            chat_history = PostgresChatMessageHistory(
                connection_string=f"postgresql://{user}:{password}@{host}:5432/{database}",
                session_id=self.session_id,
            )
            logging.info(f"Successfully created the chat history to store it into database")

            logging.info(f"Created the contextualize QA system prompt : {contextualize_system_prompt}")

            contextualize_qa_system_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", contextualize_system_prompt),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{question}"),
                ]
            )

            contextualize_qa_chain = contextualize_qa_system_prompt | llm | StrOutputParser()
            logging.info(f"Successfully created contextualize question and answer chain")

            def contextualized_question(input: dict):
                if input.get('chat_history'):
                    return contextualize_qa_chain
                else:
                    return input["question"]

            # RAG Implementation

            QA_PROMPT = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{question}"),
                ]
            )

            chain = (
                    RunnablePassthrough.assign(
                        context=contextualized_question | retreiver | self.format_docs
                    )
                    | QA_PROMPT
                    | llm
            )

            logging.info(f"Successfully created the RAG Chain")

            # Storing last 12 Chats into memory of each user of PGVECTOR Database
            if len(chat_history.messages) <= chat_hist_msg_count:
                msgs = chat_history.messages
                print(f'Total number of previous chat history : {len(chat_history.messages)}')
            else:
                msgs = chat_history.messages[-chat_hist_msg_count:]

            # Asking question to LLM
            # "chat_history"contains the older messages.
            ai_msg = chain.invoke({"question": self.user_input, "chat_history": msgs})

            # response ans
            """
            These two lines is pushing data into PGSQL database.
            """
            chat_history.add_user_message(self.user_input)
            chat_history.add_ai_message(ai_msg.content)

            # return answer and prompt
            logging.info("Successfully created the RAG Chain and returned AI messages")
            return ai_msg.content

        except Exception as e:
            logging.error(e)
            logging.error(traceback.format_exc())
            raise e


