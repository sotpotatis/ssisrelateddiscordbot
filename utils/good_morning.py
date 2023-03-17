"""good_morning.py
Contains some helper functions and constants related to the good morning command."""
import datetime

from utils.general import (
    get_json,
    write_json,
    GOOD_MORNING_DATA_FILEPATH,
    GOOD_MORNING_GREETINGS_FILEPATH,
    GOOD_MORNING_RESPONSES_FILEPATH,
    BAD_GOOD_MORNING_STARTS,
    get_now,
)
from nextcord import Message, Emoji
import logging, os, re

logger = logging.getLogger(__name__)

# Constants related to regex for detecting good morning message. TODO: Exclude bad adjectives in a sexier way
# Bad morning beginnings, such as "next morning", "bad morning", etc.
BAD_MORNING_BEGINNINGS = (
    open(BAD_GOOD_MORNING_STARTS, "r", encoding="UTF-8").read().splitlines()
)
BAD_MORNING_BEGINNINGS_TEXT = "|".join(BAD_MORNING_BEGINNINGS)
GOOD_MORNING_REGEX_TEXT = (
    f"^(?!(({BAD_MORNING_BEGINNINGS_TEXT})))(?=.*mo+r+(g*o+n+|n+i*n+g*))"
)
GOOD_MORNING_REGEX = re.compile(GOOD_MORNING_REGEX_TEXT, flags=re.IGNORECASE)
logger.info(f"Loaded {len(BAD_MORNING_BEGINNINGS)} bad morning beginnings")
# Good morning phrases
GOOD_MORNING_PHRASES = (
    open(GOOD_MORNING_GREETINGS_FILEPATH, "r", encoding="UTF-8").read().splitlines()
)  # Encoding is so funny
GOOD_MORNING_RESPONSES = (
    open(GOOD_MORNING_RESPONSES_FILEPATH, "r", encoding="UTF-8").read().splitlines()
)
logger.info(
    f"Loaded {len(GOOD_MORNING_PHRASES)} good morning phrases, {len(GOOD_MORNING_PHRASES)} responses"
)

GOOD_MORNING_REACTION_EMOJIS = {
    "seasonal": [
        {
            "from": {"month": 10, "day": 24},
            "to": {"month": 10, "day": 31},
            "emoji": "🎃",
        },  # Halloween emoji
        {
            "from": {"month": 12, "day": 20},
            "to": {"month": 12, "day": 25},
            "emoji": "🎅",
        },  # Christmas emoji
        {
            "from": {"month": 1, "day": 1},
            "to": {"month": 1, "day": 1},
            "emoji": "🎆",
        },  # New year's emoji
    ],
    "fallback": "☺️",
}

# Constants: for functions
ACTION_SEND_MESSAGE = "send_message"
ACTION_REACT = "react"
REGEX_IS_SPECIAL_CHARACTER = "|".join(
    [
        "\.",
        "\*",
        "-",
        ":",
        "(",
        ")",
        "\/",
        "\\",
        "&",
        "%",
        "$",
        "#",
        "@",
        "!",
        "~",
        "'",
        '"',
    ]
)
REQUIRED_FILES = [
    GOOD_MORNING_DATA_FILEPATH,
    GOOD_MORNING_RESPONSES_FILEPATH,
    GOOD_MORNING_GREETINGS_FILEPATH,
]
for filepath in REQUIRED_FILES:
    if not os.path.exists(filepath):  # Must exist, see example file
        raise FileNotFoundError(
            f"Can not find good morning related file {filepath}. It must be created for the bot to start."
        )


def write_to_good_morning_file(data):
    """Writes new JSON content to the good morning file.

    :param data: The fluid_data to write."""
    write_json(GOOD_MORNING_DATA_FILEPATH, data)


def get_good_morning_data():
    """Gets good morning fluid_data file content."""
    return get_json(GOOD_MORNING_DATA_FILEPATH)


def remove_punctuation(input_string):
    """Trims a string for punctuation and other special characters than spaces and A-Z.

    :param input_string: The input string."""
    return re.sub(REGEX_IS_SPECIAL_CHARACTER, "", input_string.strip())


def matches_good_morning(content):
    """Checks if a string matches a good morning message."""
    return (
        re.search(GOOD_MORNING_REGEX, content)
        or remove_punctuation(content).lower() in GOOD_MORNING_PHRASES
    )


def check_is_good_morning_message(message: Message, bot_user_id: int):
    """Checks if a message is a good morning message (that is relevant to react to) or not.

    :param message: The message that has been sent

    :param bot_user_id: The user ID of the bot

    :returns An action what to do with the message: ACTION_SEND_MESSAGE if message should be sent,
    ACTION_REACT if message should be reacted to, and None if there is no reaction"""
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
            action = (
                ACTION_REACT
                if good_morning_data["message_sent_at"] == today_date
                or not is_morning
                or not is_general_channel
                else ACTION_SEND_MESSAGE
            )
            logger.info(
                f"Action: {action} (channel: {message.channel}, is morning {is_morning})"
            )
            return action
    return None


def get_good_morning_emoji() -> str:
    """Gets the emoji to react to good morning messages with.
    Reaction emojis are seasonal, so there will be exclusive emojis around Christmas etc.

    :returns: The good morning emoji as a string"""
    now = get_now()
    reaction_emoji = GOOD_MORNING_REACTION_EMOJIS["fallback"]
    # Check emojis if there is any seasonal one
    for seasonal_reaction_emoji in GOOD_MORNING_REACTION_EMOJIS["seasonal"]:
        emoji_active_from = seasonal_reaction_emoji["from"]
        emoji_active_to = seasonal_reaction_emoji["to"]
        emoji_active_from_dt = datetime.date(
            year=now.year,
            month=emoji_active_from["month"],
            day=emoji_active_from["day"],
        )
        emoji_active_to_dt = datetime.date(
            year=now.year, month=emoji_active_to["month"], day=emoji_active_to["day"]
        )
        if emoji_active_from_dt <= now.date() <= emoji_active_to_dt:
            emoji = seasonal_reaction_emoji["emoji"]
            logger.info(f'Found active seasonal emoji "{emoji}"! Using...')
            reaction_emoji = emoji
    return reaction_emoji  # Return found reaction emoji
