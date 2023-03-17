"""menu.py
Contains various utilities related to grabbing menu fluid_data and stuff.
"""
import aiohttp

from utils.general import FLUID_DATA_DIRECTORY, get_json, write_json
import os, logging

# Logging
logger = logging.getLogger(__name__)

MENU_DATA_PATH = os.path.join(FLUID_DATA_DIRECTORY, "menu.json")
DEFAULT_EATERY_MENU_ID = "kista-nod"  # The default menu ID that Eatery Kista Nod uses for their menues (will be dynamically updated though). You can change the used ID in the code by changing this.


def get_menu_data():
    """Function to get menu fluid_data.

    :returns: Menu fluid_data as a dictionary."""
    return get_json(MENU_DATA_PATH)


def write_menu_data(new_menu_data):
    """Function for writing menu fluid_data to a file.

    :param new_menu_data: The menu fluid_data to write as a dictionary."""
    logger.info("Updating menu fluid_data...")
    write_json(MENU_DATA_PATH, new_menu_data)


async def get_eatery_menu(menu_id=None, week=None):
    """Asynchronous function to get Eatery menu fluid_data. Returns the menu fluid_data as a dictionary.

    :param menu_id: The menu ID to get. Hint: Eatery Kista Nod is 521.

    :param week: The week number to get the menu from.

    :returns: Menu fluid_data as a dictionary if found, None ifthe request failed."""
    logger.info("Getting Eatery menu...")
    async with aiohttp.ClientSession() as session:
        if menu_id != None and week != None:
            logger.info(
                f"Week and menu ID specified for menu request. Requesting menu {menu_id} for week {week}"
            )
            url = f"https://lunchmeny.albins.website/api/{menu_id}/{week}"  # Get menu fluid_data for a custom week.
        else:
            logger.info(
                "Week and menu ID not specified for menu. Requesting latest available menu..."
            )
            url = "https://lunchmeny.albins.website/api/"  # Get menu fluid_data for this week
        async with session.get(url) as request:
            logger.info("Retrieval request finished,")
            if request.status == 200:
                logger.debug(
                    "Request finished with status code 200. Getting menu fluid_data..."
                )
                menu_data = await request.json()
                logger.info("Menu fluid_data retrieved. Returning...")
                return menu_data  # Return the menu fluid_data
            else:
                logger.warning(
                    f"The menu retrieval request failed with status code {request.status}!"
                )
