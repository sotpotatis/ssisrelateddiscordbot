'''good_morning.py
Contains some helper functions and constants related to the good morning command.'''
from utils.general import get_json, write_json, GOOD_MORNING_DATA_FILEPATH, GOOD_MORNING_GREETINGS_FILEPATH, GOOD_MORNING_RESPONSES_FILEPATH, get_now
from nextcord import Message, Emoji
import logging, os, re

logger = logging.getLogger(__name__)

# Constants: regex for detecting good morning message
GOOD_MORNING_REGEX = re.compile("(^|[^i|(över)|(this)|(next)][^ ]) *mo+r+(g*o+n+|n+i*n+g*)", flags=re.IGNORECASE)
REGEX_IS_SPECIAL_CHARACTER = "([^A-Za-z])"

# Good morning phrases
GOOD_MORNING_PHRASES = open(GOOD_MORNING_GREETINGS_FILEPATH, "r", encoding="UTF-8").read().splitlines() # Encoding is so funny
GOOD_MORNING_RESPONSES = open(GOOD_MORNING_RESPONSES_FILEPATH, "r", encoding="UTF-8").read().splitlines()

GOOD_MORNING_REACTION_EMOJI = "☺️"

# Constants: for functions
ACTION_SEND_MESSAGE = "send_message"
ACTION_REACT = "react"

REQUIRED_FILES = [GOOD_MORNING_DATA_FILEPATH, GOOD_MORNING_RESPONSES_FILEPATH, GOOD_MORNING_GREETINGS_FILEPATH]
for filepath in REQUIRED_FILES:
    if not os.path.exists(filepath): #Must exist, see example file
        raise FileNotFoundError(f"Can not find good morning related file {filepath}. It must be created for the bot to start.")

def write_to_good_morning_file(data):
    '''Writes new JSON content to the good morning file.

    :param data: The data to write.'''
    write_json(GOOD_MORNING_DATA_FILEPATH, data)

def get_good_morning_data():
    '''Gets good morning data file content.'''
    return get_json(GOOD_MORNING_DATA_FILEPATH)

def remove_punctuation(input):
    '''Trims a string for punctuation, spaces, etc.

    :param input: The input string.'''
    return re.sub(REGEX_IS_SPECIAL_CHARACTER, input.strip(), "")

def matches_good_morning(content):
    '''Checks if a string matches a good morning message.'''
    return re.search(GOOD_MORNING_REGEX, content) or remove_punctuation(content).lower() in GOOD_MORNING_RESPONSES

def check_is_good_morning_message(message:Message, bot_user_id:int):
    '''Checks if a message is a good morning message (that is relevant to react to) or not.

    :param message: The message that has been sent

    :param bot_user_id: The user ID of the bot

    :returns An action what to do with the message: ACTION_SEND_MESSAGE if message should be sent,
    ACTION_REACT if message should be reacted to, and None if there is no reaction'''
    # Check if channel is the same
    good_morning_data = get_good_morning_data()
    now = get_now()
    today_date = str(now.date())
    is_morning = 6 <= now.hour <= 11
    good_morning_channel_id = good_morning_data["message_channel_id"]
    is_general_channel = message.channel.id == good_morning_channel_id
    if not message.author.bot and message.author.id != bot_user_id:
        # Check if message matches content
        if matches_good_morning(message.content):
            logger.info("Detected a good morning message!")
            # Check whether a message should be sent or if we should react
            return ACTION_REACT if good_morning_data["message_sent_at"] == today_date or not is_morning or not is_general_channel else ACTION_SEND_MESSAGE
    return None

