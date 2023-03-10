'''predefined_messages.py
Contains utilities related to the predefined messages function.
'''
from utils.general import STATIC_DATA_DIRECTORY, get_json
import os, logging
PREDEFINED_MESSAGES_PATH = os.path.join(STATIC_DATA_DIRECTORY, "predefined_messages.json")

#Logging
logger = logging.getLogger(__name__)

def get_predefined_messages():
    '''Function to get predefined message fluid_data.'''
    return get_json(PREDEFINED_MESSAGES_PATH)

def get_predefined_message(name):
    '''Function to get a certain predefined message.

    :param name: The name of the predefined message.

    :returns: A dictionary with information if the predefined message is found,
    None if it isn't.'''
    if name not in get_predefined_messages():
        logger.info(f"Requested predefined message \"{name}\" not found.")
    else:
        logger.info(f"Returning predefined message for {name}...")
        return get_predefined_messages()[name]
