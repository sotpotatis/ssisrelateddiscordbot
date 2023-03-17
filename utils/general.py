"""UTILITIES FUNCTIONS
Provides utilities related to various functions in the bot
"""
import asyncio
import json, os, logging, datetime, pytz, nextcord.utils
import shutil
from typing import Optional, Dict

from utils.color_const import ERROR_EMBED_COLOR
from nextcord import Embed, Activity, ActivityType

# Logging
logger = logging.getLogger(__name__)

# Paths
# ABOUT FLUID STORAGE
# In an environment such as a docker container, data storage will be separated:
# the "fluid data" directory explained below (short explanation; it stores data that is updated
# as the bot is running) will be mounted at a different volume and path from everything else.
# On the first start (when the fluid data volume is brand new), we want to make sure that all files
# are copied from the Dockerfile over to the fluid_data directory.
# We make use of an environent variable to detect whether fluid data storage is enabled or not.
FLUID_STORAGE_ENABLED = bool(os.getenv("SSIS_DISCORD_BOT_STORAGE_IS_FLUID", False))
# If you have a volume for fluid data mounted, the SSIS_DISCORD_BOT_FLUID_STORAGE_BASE_PATH variable
# can be used to specify where the volume is mounted.
FLUID_STORAGE_BASE_PATH = os.getenv("SSIS_DISCORD_BOT_FLUID_STORAGE_BASE_PATH", "")
BOT_DIRECTORY = os.getenv(
    "SSIS_DISCORD_BOT_DIRECTORY", os.getcwd()
)  # The directory that the bot runs in
SOURCE_FLUID_DATA_DIRECTORY = os.getenv(
    "SSIS_DISCORD_BOT_SOURCE_FLUID_DATA_DIRECTORY",  # Where initial fluid data will be (only relevant when using fluid storage (see above))
    os.path.join(BOT_DIRECTORY, "fluid_data"),
)
FLUID_DATA_DIRECTORY = os.getenv(
    "SSIS_DISCORD_BOT_FLUID_DATA_DIRECTORY",
    os.path.join(BOT_DIRECTORY, FLUID_STORAGE_BASE_PATH, "fluid_data"),
)  # Directory for storing bot and user data files (data that is fluid and updated by the bot)
STATIC_DATA_DIRECTORY = os.getenv(
    "SSIS_DISCORD_BOT_STATIC_DATA_DIRECTORY ",
    os.path.join(BOT_DIRECTORY, "static_data"),
)  # Directiory for storing static data (that is not updated by the bot)
CLUBS_DATA_FILEPATH = os.path.join(
    FLUID_DATA_DIRECTORY, "clubs.json"
)  # File for storing club fluid_data
MENU_SUBSCRIPTIONS_DATA_FILEPATH = os.path.join(
    FLUID_DATA_DIRECTORY, "menu_subscriptions.json"
)  # File for storing menu subscription fluid_data
PENTRYANSVAR_DATA_FILEPATH = os.path.join(
    FLUID_DATA_DIRECTORY, "pentryansvar.json"
)  # File for storing pentryansvar fluid_data
ROLE_DATA_FILEPATH = os.path.join(
    STATIC_DATA_DIRECTORY, "roles.json"
)  # File for storing roles fluid_data
CACHED_SCHEDULE_DATA_FILEPATH = os.path.join(
    FLUID_DATA_DIRECTORY, "cached_schedules.json"
)  # File for storing cached schedules
SUBSCRIPTIONS_DATA_FILEPATH = os.path.join(
    FLUID_DATA_DIRECTORY, "subscribed_schedules.json"
)  # File for storing schedule subscriptions
SUBSCRIPTIONS_SCHEMA_FILEPATH = os.path.join(
    FLUID_DATA_DIRECTORY, "available_subscriptions.json"
)  # File for defining available subscriptions
GOOD_MORNING_DATA_FILEPATH = os.path.join(
    FLUID_DATA_DIRECTORY, "good_morning.json"
)  # Data regarding the good morning message
GOOD_MORNING_GREETINGS_FILEPATH = os.path.join(
    STATIC_DATA_DIRECTORY, "good_morning_greetings.txt"
)  # Good morning messages around the world
GOOD_MORNING_RESPONSES_FILEPATH = os.path.join(
    STATIC_DATA_DIRECTORY, "good_morning_responses.txt"
)  # Responses to when people say "good morning"
BAD_GOOD_MORNING_STARTS = os.path.join(
    STATIC_DATA_DIRECTORY, "bad_good_morning_starts.txt"
)  # Bad beginning of the good morning detection, see good_morning.py
SEASONAL_PROFILE_PICTURES_FILEPATH = os.path.join(
    STATIC_DATA_DIRECTORY, "seasonal_profile_pictures.json"
)  # Data for seasonal profile pictures
SEASONAL_PROFILE_PICTURES_DIRECTORY = os.path.join(
    STATIC_DATA_DIRECTORY, "seasonal_profile_pictures"
)
LOGGING_DIRECTORY = os.getenv(
    "SSIS_DISCORD_BOT_LOGGING_DIRECTORY",
    os.path.join(BOT_DIRECTORY, FLUID_STORAGE_BASE_PATH, "logging"),
)
LOGGING_HANDLER_FILEPATH = os.path.join(LOGGING_DIRECTORY, "log.log")
# Other constants
BASE_TIMEZONE = "Europe/Stockholm"  # Base timezone for the bot
BOT_GENERAL_STATUSES = [
    {"type": ActivityType.listening, "text": "Davids serverdatorer som spinner..."},
    {"type": ActivityType.playing, "text": "schack med några treor"},
    {"type": ActivityType.playing, "text": "SSIS Bot | Lyssnar på kommandon"},
    {"type": ActivityType.listening, "text": "kaffemaskinen som gör kaffe"},
    {"type": ActivityType.watching, "text": "3D-skrivarna i Dalek"},
    {"type": ActivityType.watching, "text": "ettor och nollor"},
    {"type": ActivityType.listening, "text": "kommandon"},
    {"type": ActivityType.watching, "text": "alla dessa människor på Discord!"},
    {
        "type": ActivityType.playing,
        "text": "SSIS Bot | https://github.com/sotpotatis/ssisrelateddiscordbot",
    },
    {
        "type": ActivityType.listening,
        "text": "fördelarna med att använda Obsidian för sina anteckningar",
    },
    {
        "type": ActivityType.listening,
        "text": "grytor & kastruller som slamrar nere i Eatery",
    },
    {"type": ActivityType.watching, "text": "Davids robotarm som klappar Yoshi <3"},
    {"type": ActivityType.listening, "text": "Davids robotarm som klappar Yoshi <3"},
    {"type": ActivityType.listening, "text": "God morgon-meddelanden"},
    {"type": ActivityType.playing, "text": "Othello för mig själv i biblioteket"},
    {"type": ActivityType.playing, "text": "Othello med en kompis"},
    {
        "type": ActivityType.listening,
        "text": "massa elever som lånar böcker i biblioteket",
    },
]
MAIN_SERVER_ID = 746412815048376371  # Server to retrieve members from. The bot is intended to be used on one single server and therefore this is hard coded.
# JSON-related functions
def get_json(filepath):
    """Retrieves JSON from a certain filepath."""
    with open(filepath, encoding="UTF-8") as json_file:
        return json.loads(json_file.read())


def write_json(filepath, new_json):
    """Writes JSON to a file at the provided filepath."""
    with open(filepath, "w", encoding="UTF-8") as json_file:
        json_file.write(json.dumps(new_json, indent=True))


# Time-related functions
def get_now():
    """Returns the current time in a unviersal timezone (since this app will be deployed in Sweden, it's
    the Swedish timezone (but you can change it above if you'd like to!))"""
    return datetime.datetime.now(tz=pytz.timezone(BASE_TIMEZONE))


def get_current_day_name():
    """Gets the current day name and returns it"""
    current_day_number = get_now().isoweekday()
    day_mappings = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    current_day_name = day_mappings[current_day_number - 1]
    return current_day_name


# Embeds
def generate_error_embed(
    title: str = "Sorry! Ett fel inträffade",
    description: str = "Pinsamt va? Hehe. Jag ber om ursäkt! Peace out! Testa igen senare, eller nåt.",
    footer: Optional[Dict] = None,
    *args,
    **kwargs,
) -> Embed:
    """Shortcut function for generating an embed message that can be sent when an error has occurred."""
    error_embed = Embed(
        *args, title=title, description=description, color=ERROR_EMBED_COLOR, **kwargs
    )
    # Add a footer to the message if provided
    if footer is not None:
        error_embed.set_footer(**footer)
    return error_embed


# Other
async def class_name_to_role(bot, guild, class_name):
    """Tries to parse a class name to a role that maps for the corresponding class.

    :param bot: The bot (nextcord.Commands) that is used when finding the role.

    :param class_name: The class name (e.g. "TE20A" that the bot should find roles for)

    :param guild: The guild to search for roles in."""
    logger.info(f"Trying to find a role for {class_name}...")
    role = nextcord.utils.find(
        lambda x: x.name.upper() == class_name.upper(), guild.roles
    )
    logger.debug(f"Found class role: {role}.")
    logger.info("Finished searching for role.")
    return role


async def find_person_tag(bot, guild, wanted_person_name, class_name):
    """Tries to find an individual person (student) based on its name.

     :param bot: The bot (nextcord.Commands) that is used when finding the role.

    :param guild: The guild to search for roles in.

    :param class_name: The class name (e.g. "TE20A") that the person is in

    :param wanted_person_name: The name that the person has.
    """
    logger.info(f"Trying to find {wanted_person_name} in the server...")
    # Persons are found by first searching by class. Since otherwise, it's quite impossible to track a person unless they have a unique name
    class_role = await class_name_to_role(bot, guild, class_name)
    if class_role == None:
        logger.info("The person's class could not be found. Returning None...")
        return None
    logger.debug("Class role found. Trying to find person...")
    # Parse person name
    wanted_person_name = (
        wanted_person_name.capitalize()
    )  # Ensure capitalization of name
    # Handle the following scenarios:
    # Match Albin [surname] => Albin [surname]
    # ...but not Albin S. => Albin H.
    if len(wanted_person_name.split(" ")) > 1:
        logger.debug("The person that is wanted has a surname specified!")
        wanted_person_surname = wanted_person_name.split(" ")[1]
        wanted_person_surname.strip(
            "."
        )  # So we can match names like Albin Se... => Albin S.
    else:
        logger.debug("The person that is wanted has not a surname specified!")
        wanted_person_surname = None

    def person_name_filter(guild_member):
        """Filter used for finding a person name in the guild."""
        guild_member_name = (
            guild_member.name.capitalize()
        )  # Get the name and capitalize it
        # Remove class from guild member name (class names are added inside parantheses)
        if len(guild_member_name.split("(")) < 2:
            logger.debug(
                f"Note: Class name could not be removed for guild member with name {guild_member_name}."
            )
        else:
            guild_member_name = guild_member_name.split("(")[0]
        person_first_name = guild_member_name.split(" ")[
            0
        ]  # Get the person's first name
        if len(guild_member_name.split(" ")) < 2:
            logger.debug(
                f'Note: Last name for name "{guild_member_name}" is not available.'
            )
            person_last_name = None
        else:
            person_last_name = guild_member_name.split(" ")[
                1
            ]  # Get the person's last name
        # Match and return the match
        if (
            guild_member.has_role(class_role)
            and wanted_person_name == person_first_name
        ):  # Check class role and name.
            # Match surname if specified
            if wanted_person_surname == None:
                return True
            elif person_last_name.startswith(wanted_person_surname):
                return True
            else:  # (no match)
                return False
        else:  # (no match)
            return False

    person = nextcord.utils.find(person_name_filter, guild.members)
    logger.debug(f"Found person: {person}")
    logger.info("Finished searching for person.")
    return person


def get_active_classes():
    """Gets the classes that are active in the school, aka. the classes that have active education currently
    and have not graduated. For example, for 2022-01, this would be TE[19-21][A-D] and for 2022-08, this would be
    TE[20-22][A-D]."""
    now = get_now()
    # Create index of classes
    class_number_start = now.year - 3 if now.month < 8 else now.year - 2
    class_number_end = now.year - 1 if now.month < 8 else now.year
    classes = []
    for class_year in range(class_number_start, class_number_end):
        for class_letter in ["A", "B", "C", "D"]:
            classes.append(f"TE{class_year[-2:]}{class_letter}")
    return classes


def get_roles():
    """Returns the role file which contains static information about various roles on the server."""
    return get_json(ROLE_DATA_FILEPATH)


async def ensure_admin_permissions(bot, user, guild, interaction_or_ctx=None):
    """Function to ensure that a user calling the command has permissions to execute administrative commands on the bot.
    If not, an error message is automatically set.

    :param bot: The nextcord.commands bot to use.

    :param user: The user to check permissions for.

    :param guild: The guild that is being used.

    :returns True if the user is an admin, False if the user isn't."""
    logger.debug(f"Checking permissions for user {user.mention}...")
    # Get the roles
    roles = get_roles()
    admin_role = roles["administrator_role_id"]
    moderator_role = roles["moderator_role_id"]
    # Check if the user is either a moderator or administrator
    if any(
        [
            nextcord.utils.get(guild.roles, id=role_id)
            for role_id in [admin_role, moderator_role]
        ]
    ):
        logger.debug("User is admin or moderator!")
        # Return True
        return True
    else:
        logger.debug("User is not admin or moderator. Returning error...")
        # If an interaction or context is sent, we can send a message about the error
        if interaction_or_ctx != None:
            logger.debug(
                f"Interaction of type {type(interaction_or_ctx)} has been set."
            )
            error_embed = generate_error_embed(
                "Du är inte en admin eller moderator...",
                "...Och därför har du inte behörigheterna som krävs att utföra detta kommando.",
                footer={"text": "Detta meddelande kommer att raderas efter 1 minut."},
            )
            if type(interaction_or_ctx) == nextcord.Interaction:  # Reply to interaction
                logger.info("Sending error message...")
                await interaction_or_ctx.response.send_message(
                    embed=error_embed, delete_after=60
                )


def string_to_localized_datetime(input: str):
    """Takes a string, converts it to a datetime and also ensures that that datetime
    is in the current BASE_TIMEZONE."""
    return datetime.datetime.fromisoformat(input).astimezone(
        pytz.timezone(BASE_TIMEZONE)
    )


# See the documentation under "FLUID STORAGE" above for information about fluid storage.
# Here, we copy over all files to the fluid storage volume if they do not exist there already.
if FLUID_STORAGE_ENABLED:
    logger.info("Fluid storage is enabled - running data check...")
    if not os.path.exists(FLUID_DATA_DIRECTORY):
        logger.info("Creating directory for fluid data...")
        os.mkdir(FLUID_DATA_DIRECTORY)
    else:
        logger.info("Fluid data directory already created at the target path.")
    if not os.path.exists(LOGGING_DIRECTORY):
        logger.info("Creating directory for logging...")
        os.mkdir(LOGGING_DIRECTORY)
    else:
        logger.info("Logging directory already created at the target path.")
    if SOURCE_FLUID_DATA_DIRECTORY != FLUID_DATA_DIRECTORY:
        logger.info("Checking files...")
        target_fluid_data_directory_files = os.listdir(FLUID_DATA_DIRECTORY)
        for file in os.listdir(SOURCE_FLUID_DATA_DIRECTORY):
            if file not in target_fluid_data_directory_files:
                source_filepath = os.path.join(SOURCE_FLUID_DATA_DIRECTORY, file)
                target_filepath = os.path.join(FLUID_DATA_DIRECTORY, file)
                logger.info(
                    f"Copying file {file} to target directory (from {source_filepath} to {target_filepath})..."
                )
                shutil.copy(source_filepath, target_filepath)
            else:
                logger.info(f"{file} already exists in the target directory.")
