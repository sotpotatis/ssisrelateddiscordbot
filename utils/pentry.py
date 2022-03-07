'''pentry.py
Contains various utilities related to grabbing pentry data.
'''
import aiohttp, logging
from utils.general import get_json, write_json, PENTRYANSVAR_DATA_FILEPATH
logger = logging.getLogger(__name__)

def get_pentryansvar_data():
    '''Loads the pentryansvar file, which contains information
    about the current message that has been sent, etc.'''
    return get_json(PENTRYANSVAR_DATA_FILEPATH)

def write_pentryansvar_data(new_data):
    '''Writes data to the file containing pentryansvar data.

    :param new_data: The new data to write to the file.'''
    write_json(PENTRYANSVAR_DATA_FILEPATH, new_data) #Write the new data to the file

async def get_pentryansvar():
    '''Retrieves pentryansvar for the current week.

    :returns The JSON if the request succeeded, None if it didn't.'''
    logger.info("Retrieving pentryansvar...")
    async with aiohttp.ClientSession() as session:
        async with session.get("http://192.168.158.116/api/pentryansvar") as request: #pentryansvar.albins.website will be up again soon. The one provided here is ran locally on the SSIS tnetwork.
            if request.status == 200: #If the request succeeded
                logger.info("Pentryansvar request succeeded. Retrieving JSON...")
                pentry_data = await request.json()
                logger.info("JSON retrieved. Returning...")
                return pentry_data
            else:
                logger.warning("Pentryansvar request returned unknown status code!")
                return None
