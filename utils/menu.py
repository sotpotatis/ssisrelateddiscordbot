'''menu.py
Contains various utilities related to grabbing menu data and stuff.
'''
import aiohttp

from utils.general import DATA_DIRECTORY, get_json, write_json
import os, logging

#Logging
logger = logging.getLogger(__name__)

MENU_DATA_PATH = os.path.join(DATA_DIRECTORY, "menu.json")
def get_menu_data():
    '''Function to get menu data.

    :returns: Menu data as a dictionary.'''
    return get_json(MENU_DATA_PATH)

def write_menu_data(new_menu_data):
    '''Function for writing menu data to a file.

    :param new_menu_data: The menu data to write as a dictionary.'''
    logger.info("Updating menu data...")
    write_json(MENU_DATA_PATH, new_menu_data)

async def get_eatery_menu(menu_id=None, week=None):
    '''Asyncronous function to get Eatery menu data. Returns the menu data as a dictionary.

    :param menu_id: The menu ID to get. Hint: Eatery Kista Nod is 521.

    :param week: The week number to get the menu from.

    :returns: Menu data as a dictionary if found, None ifthe request failed.'''
    logger.info("Getting Eatery menu...")
    async with aiohttp.ClientSession() as session:
        if menu_id != None and week != None:
            logger.info(f"Week and menu ID specified for menu request. Requesting menu {menu_id} for week {week}")
            url = f"https://lunchmeny.albins.website/api/{menu_id}/{week}" #Get menu data for a custom week.
        else:
            logger.info("Week and menu ID not specified for menu. Requesting latest available menu...")
            url = "https://lunchmeny.albins.website/api/" #Get menu data for this week
        async with session.get(url) as request:
            logger.info("Retrieval request finished,")
            if request.status == 200:
                logger.debug("Request finished with status code 200. Getting menu data...")
                menu_data = await request.json()
                logger.info("Menu data retrieved. Returning...")
                return menu_data #Return the menu data
            else:
                logger.warning(f"The menu retrieval request failed with status code {request.status}!")
