'''UTILITIES FUNCTIONS
Provides utilities related to various functions in the bot
'''
import asyncio
import json, os, logging, datetime, pytz, nextcord.utils
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
PENTRYANSVAR_DATA_FILEPATH = os.path.join(DATA_DIRECTORY, "pentryansvar.json") #File for storing pentryansvar data
ROLE_DATA_FILEPATH = os.path.join(DATA_DIRECTORY, "roles.json") #File for storing roles data
LOGGING_DIRECTORY = os.path.join(BOT_DIRECTORY, "../logging")
LOGGING_HANDLER_FILEPATH = os.path.join(LOGGING_DIRECTORY, "log.log")
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
        json_file.write(json.dumps(new_json, indent=True))

#Time-related functions
def get_now():
    '''Returns the current time in a unviersal timezone (since this app will be deployed in Sweden, it's
    the Swedish timezone (but you can change it above if you'd like to!))'''
    return datetime.datetime.now(tz=pytz.timezone(BASE_TIMEZONE))

#Embeds
def generate_error_embed(title="Sorry! Ett fel inträffade", description="Pinsamt va? Hehe. Jag ber om ursäkt! Peace out! Testa igen senare, eller nåt.", *args, **kwargs):
    '''Shortcut function for generating an embed message that can be sent when an error has occurred.'''
    return Embed(
        *args,
        title=title,
        description=description,
        color=ERROR_EMBED_COLOR,
        **kwargs
    )

#Other
async def class_name_to_role(bot, guild, class_name):
    '''Tries to parse a class name to a role that maps for the corresponding class.

    :param bot: The bot (nextcord.Commands) that is used when finding the role.

    :param class_name: The class name (e.g. "TE20A" that the bot should find roles for)

    :param guild: The guild to search for roles in.'''
    logger.info(f"Trying to find a role for {class_name}...")
    role = nextcord.utils.find(lambda x: x.name.upper() == class_name.upper(), guild.roles)
    logger.debug(f"Found class role: {role}.")
    logger.info("Finished searching for role.")
    return role

async def find_person_tag(bot, guild, wanted_person_name, class_name):
    '''Tries to find an individual person (student) based on its name.

     :param bot: The bot (nextcord.Commands) that is used when finding the role.

    :param guild: The guild to search for roles in.

    :param class_name: The class name (e.g. "TE20A") that the person is in

    :param wanted_person_name: The name that the person has.
    '''
    logger.info(f"Trying to find {wanted_person_name} in the server...")
    #Persons are found by first searching by class. Since otherwise, it's quite impossible to track a person unless they have a unique name
    class_role = await class_name_to_role(bot, guild, class_name)
    if class_role == None:
        logger.info("The person's class could not be found. Returning None...")
        return None
    logger.debug("Class role found. Trying to find person...")
    #Parse person name
    wanted_person_name = wanted_person_name.capitalize() #Ensure capitalization of name
    #Handle the following scenarios:
    #Match Albin [surname] => Albin [surname]
    #...but not Albin S. => Albin H.
    if len(wanted_person_name.split(" ")) > 1:
        logger.debug("The person that is wanted has a surname specified!")
        wanted_person_surname = wanted_person_name.split(" ")[1]
        wanted_person_surname.strip(".") #So we can match names like Albin Se... => Albin S.
    else:
        logger.debug("The person that is wanted has not a surname specified!")
        wanted_person_surname = None

    def person_name_filter(guild_member):
        '''Filter used for finding a person name in the guild.'''
        guild_member_name = guild_member.name.capitalize() #Get the name and capitalize it
        #Remove class from guild member name (class names are added inside parantheses)
        if len(guild_member_name.split("(")) < 2:
            logger.debug(f"Note: Class name could not be removed for guild member with name {guild_member_name}.")
        else:
            guild_member_name = guild_member_name.split("(")[0]
        person_first_name = guild_member_name.split(" ")[0] #Get the person's first name
        if len(guild_member_name.split(" ")) < 2:
            logger.debug(f"Note: Last name for name \"{guild_member_name}\" is not available.")
            person_last_name = None
        else:
            person_last_name = guild_member_name.split(" ")[1] #Get the person's last name
        #Match and return the match
        if guild_member.has_role(class_role) and wanted_person_name == person_first_name: #Check class role and name.
            #Match surname if specified
            if wanted_person_surname == None:
                return True
            elif person_last_name.startswith(wanted_person_surname):
                return True
            else: #(no match)
                return False
        else: #(no match)
            return False
    person = nextcord.utils.find(person_name_filter, guild.members)
    logger.debug(f"Found person: {person}")
    logger.info("Finished searching for person.")
    return person

def get_roles():
    '''Returns the role file which contains static information about various roles on the server.'''
    return get_json(ROLE_DATA_FILEPATH)

async def ensure_admin_permissions(bot, user, guild, interaction_or_ctx=None):
    '''Function to ensure that a user calling the command has permissions to execute administrative commands on the bot.
    If not, an error message is automatically set.

    :param bot: The nextcord.commands bot to use.

    :param user: The user to check permissions for.

    :param guild: The guild that is being used.

    :returns True if the user is an admin, False if the user isn't.'''
    logger.debug(f"Checking permissions for user {user.mention}...")
    #Get the roles
    roles = get_roles()
    admin_role = roles["administrator_role_id"]
    moderator_role = roles["moderator_role_id"]
    #Check if the user is either a moderator or administrator
    if any([await nextcord.utils.get(guild.roles, id=role_id) for role_id in [admin_role, moderator_role]]):
        logger.debug("User is admin or moderator!")
        #Return True
        return True
    else:
        logger.debug("User is not admin or moderator. Returning error...")
        #If an interaction or context is sent, we can send a message about the error
        if interaction_or_ctx != None:
            logger.debug(f"Interaction of type {type(interaction_or_ctx)} has been set.")
            error_embed = generate_error_embed(
                "Du är inte en admin eller moderator...",
                "...Och därför har du inte behörigheterna som krävs att utföra detta kommando.",
                footer="Detta meddelande kommer att raderas efter 1 minut."
            )
            if type(interaction_or_ctx) == nextcord.Interaction: #Reply to interaction
                logger.info("Sending error message...")
                error_message = await interaction_or_ctx.response.send_message(embed=error_embed)
                original_message = interaction_or_ctx.message
            #Delete error message
            await asyncio.sleep(60) #Sleep for 60 seconds
            logger.info("Deleting permission denying messages...")
            await error_message.delete()
            await original_message.delete()
            logger.info("Permission denying messages deleted.")
