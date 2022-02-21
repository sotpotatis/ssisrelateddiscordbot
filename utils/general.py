'''UTILITIES FUNCTIONS
Provides utilities related to various functions in the bot
'''
import json, os, logging, datetime, pytz
from utils.color_const import ERROR_EMBED_COLOR
from nextcord import Embed

#Logging
logger = logging.getLogger(__name__)

#Paths
BOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) #The directory that the bot runs in
DATA_DIRECTORY = os.path.join(BOT_DIRECTORY, "../data") #Directory for storing data files
CLUBS_DATA_FILEPATH = os.path.join(DATA_DIRECTORY, "clubs.json") #File for storing club data
MENU_SUBSCRIPTIONS_DATA_FILEPATH = os.path.join(DATA_DIRECTORY, "menu_subscriptions.json") #File for storing menu subscription data
ADMINISTRATORS_DATA_FILEPATH = os.path.join(DATA_DIRECTORY, "admins.json") #File for storing admins that have permission to use the bot

#Other constants
BASE_TIMEZONE = "Europe/Stockholm" #Base timezone for the bot

#JSON-related functions
def get_json(filepath):
    '''Retrieves JSON from a certain filepath.'''
    with open(filepath) as json_file:
        return json.loads(json_file.read())

def write_json(filepath, new_json):
    '''Writes JSON to a file at the provided filepath.'''
    with open(filepath, "w") as json_file:
        json_file.write(json.dumps(new_json))

#Time-related functions
def get_now():
    '''Returns the current time in a unviersal timezone (since this app will be deployed in Sweden, it's
    the Swedish timezone (but you can change it above if you'd like to!))'''
    return datetime.datetime.now(tz=pytz.timezone(BASE_TIMEZONE))

#Embeds
def generate_error_embed(title="Sorry! Ett fel inträffade", description="Pinsamt va? Hehe. Jag ber om ursäkt! Peace out! Testa igen senare, eller nåt."):
    '''Shortcut function for generating an embed message that can be sent when an error has occurred.'''
    return Embed(
        title=title,
        description=description,
        color=ERROR_EMBED_COLOR
    )
