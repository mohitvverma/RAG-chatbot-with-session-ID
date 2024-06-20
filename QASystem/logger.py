import logging
import os
from datetime import datetime

"""
We need four things in our logging file
1. File name should created as the logger will run multiple times.
2. Setup the where the logging folder will be created.
3. Setup the path for logging files creating multiple files within the logger folder.
"""

# Here the filename of logs created when the program has runned up is as per the datetime & time when it called.

LOG_FILE_NAME = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Now we create a folder in which all the logs will be stored.
# os.path: Used to get the path & join is used to add a filename in that folder
# os.getcwd(): In which working directory we are working or using.
logs_path = os.path.join("/Users/mohitverma/Documents/Etech-RAG-Chatbot/Etech-RAG",
                         'Logs_data', LOG_FILE_NAME)  # Logs_data -> Folder Name and LOG_FILE_NAME -> Log file name


# Now, we need a control here, If the folder is already there then we do-not need to create the same folder & if Not then only we create it.

if not os.path.exists(logs_path):
    os.makedirs(logs_path, exist_ok=True)
else:
    pass

LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE_NAME)


logging.basicConfig(

    filename = LOG_FILE_PATH,
    # Format of Output : 1-Time, 2-Line number, 3-Name means the logger name if we made our custom logger or used a default logger.
    # level name: Then it will show the level name, 5. Message : It is used to extract the message.

    # Use of S & D : It is used when we want to show the output in specfic format, if 's' used means output in string.
    # If 'd' used means output in digits.

    format ="[ %(asctime)s ] %(name)s  %(lineno)d - %(levelname)s %(message)s",
    level = logging.INFO
    )