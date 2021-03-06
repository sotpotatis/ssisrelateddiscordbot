'''utils\clubs.py
Contains helper functions related to getting data about clubs.'''
from utils.general import get_json, write_json, CLUBS_DATA_FILEPATH, get_now
import logging
from nextcord import Embed

#Logging
logger = logging.getLogger(__name__)

def get_clubs_data():
    '''Shortcut function to get data about clubs.'''
    return get_json(CLUBS_DATA_FILEPATH)

def write_clubs_data(club_data):
    '''Shortcut function to write data to the clubs file.

    :param club_data: Data to write.'''
    write_json(CLUBS_DATA_FILEPATH, club_data)

def get_club_ids():
    '''Function to get all IDs of clubs that have been created.'''
    club_ids = []
    for club in get_clubs_data()["clubs"]:
        club_ids.append(club["id"])
    return club_ids #Return list of club IDs

def get_club_by_id(requested_club_id, return_index=False):
    '''Shortcut function to find a club by its id.

    :param requested_club_id: The name of the club.

    :returns the club data if found, None if the club can not be found.'''
    #Iterate through clubs to try to find the club
    index = 0
    for club_id in get_club_ids():
        if club_id == requested_club_id:
            for club in get_clubs_data()["clubs"]:
                if club["id"] == requested_club_id:
                    club_data = club
                    break
            return club_data if not return_index else (club_data, index)
        index += 1
    return None if not return_index else (None, None)

def get_club_subscribers(club_data):
    '''Function to get all subscribers to a club.

    :param club_data: The data for the club as a dictionary.

    :returns: A list of user IDs that are subscribing to the club
    '''
    return [subscriber["user_id"] for subscriber in club_data["subscribers"]]

def is_subscriber_to_club(club_data, user_id):
    '''Function to check if a user is subscribing to a club or not.

    :param club_data: The data for the club as a dictionary.

    :param user_id: The user ID that you want to check if it is subscribing.'''
    return True if user_id in get_club_subscribers(club_data) else False

def add_subscriber_to_club(club_id, user_id):
    '''Function for adding a subscriber to a club.

    :param club_id: The club ID to add the subscriber to

    :param user_id: The user ID to add to the club.
    '''
    club_data, club_index = get_club_by_id(club_id, return_index=True)
    if not is_subscriber_to_club(club_data, user_id): #Add subscriber
        club_data["subscribers"].append(
            {
                "user_id": user_id,
                "added_at": str(get_now())
            }
        )
    else:
        logger.info("User is not subscribed.")
    #Update club data
    clubs_data = get_clubs_data()
    clubs_data["clubs"][club_index] = club_data
    write_clubs_data(clubs_data)

def remove_subscriber_from_club(club_id, user_id):
    '''Function for adding a subscriber to a club.

    :param club_id: The club ID to remove the subscriber from

    :param user_id: The user ID to add to the club.
    '''
    logger.info("Removing user from club...")
    club_data, club_index = get_club_by_id(club_id, return_index=True)
    if is_subscriber_to_club(club_data, user_id):
        #Find the subscriber
        subscriber_index = get_club_subscribers(club_data).index(user_id)
        club_data["subscribers"].pop(subscriber_index)
        logger.debug("Change done in memory.")
    else:
        logger.info("User is not subscribed to the club.")
    #Update club data
    clubs_data = get_clubs_data()
    clubs_data["clubs"][club_index] = club_data
    write_clubs_data(clubs_data)
    logger.info("User unsubscribed to the club.")
