"""subscription.py
Commands for handling people that has subscribed to receiving messages for different things.

Subscriptions are split in categories: for example "menu", "schedule", etc."""
from utils.general import (
    get_json,
    write_json,
    SUBSCRIPTIONS_DATA_FILEPATH,
    SUBSCRIPTIONS_SCHEMA_FILEPATH,
    BASE_TIMEZONE,
)
from nextcord import Member
import logging, os, datetime, pytz

# Set up logging
logger = logging.getLogger(__name__)
DEFAULT_SUBSCRIPTION_FILE_CONTENT = {"subscriptions": {}}


def get_subscriptions():
    """Gets content of the subscription file."""
    return get_json(SUBSCRIPTIONS_DATA_FILEPATH)


def update_subscriptions(new_content):
    """Updates the subscription file with new content."""
    write_json(SUBSCRIPTIONS_DATA_FILEPATH, new_content)


def get_available_subscriptions():
    """Gets the available subscriptions."""
    return get_json(SUBSCRIPTIONS_SCHEMA_FILEPATH)


def is_subscribed_to(user: Member, category_name: str, subcategory_name: str):
    '''Check if a user is subscribed to something or not.

    :param user: The user to check if it is subscribed or not.

    :param category_name: Category name for the subscription, for example "menu".

    :param subcategory_name: Subcategory name for the subscription, for example "daily"'''
    subscription_file = get_subscriptions()
    if (
        category_name in subscription_file["subscriptions"]
        and subcategory_name in subscription_file["subscriptions"][category_name]
    ):
        return (
            str(user.id)
            in subscription_file["subscriptions"][category_name][subcategory_name][
                "subscriptions"
            ]
        )
    else:
        message = f"Requested subscription fluid_data for {category_name}:{subcategory_name} which does not seem to exist."
        logger.warning(message)
        raise Exception(message)


def change_subscriber_status(
    category_name: str, subcategory_name: str, user: Member, add=True
):
    """Adds or removes subscriber to something.

    :param category_name: Category name for the subscription, for example "menu".

    :param subcategory_name: Subcategory name for the subscription, for example "daily"

    :param user: The user to check if it is subscribed or not.

    :param add: True to add user, False to remove user.
    """
    logger.info(f"Adding/removing subscriber to {category_name}:{subcategory_name}...")
    subscribed = is_subscribed_to(user, category_name, subcategory_name)
    # Validate that user can be added or removed (must be not in/in database depending on action)
    if add and not subscribed or not add and subscribed:
        # Perform action to user
        subscription_data = get_subscriptions()
        if add:
            subscription_data["subscriptions"][category_name][subcategory_name][
                "subscriptions"
            ][str(user.id)] = {"last_notified_at": None}
        else:
            del subscription_data["subscriptions"][category_name][subcategory_name][
                "subscriptions"
            ][str(user.id)]
        update_subscriptions(subscription_data)
        logger.info("User was added/removed to subscription.")
    else:
        logger.warning(
            "User is already subscribed or unsubscribed! You should create a check for this and handle it somewhere else."
        )


def get_users_not_notified_after(timestamp, category_name, subcategory_name):
    """Retrieves a list of users that has not been notified within a certain timespan.

    :param timestamp: Any users not notified after or at this will be returned.

    :param category_name: The subscription category to check.

    :param subcategory_name: The subscription subcategory to check.

    :returns: A list of user IDs that have not been notified."""
    logger.debug(
        f"Getting users not notified after {timestamp} in {category_name}/{subcategory_name}..."
    )
    # Get the category
    subcategory_data = get_subscriptions()["subscriptions"][category_name][
        subcategory_name
    ]["subscriptions"]
    subscribers_to_notify = []
    for user_id, subscription_data in subcategory_data.items():
        if subscription_data["last_notified_at"] != None:
            if (
                datetime.datetime.fromisoformat(
                    subscription_data["last_notified_at"]
                ).astimezone(tz=pytz.timezone(BASE_TIMEZONE))
                >= timestamp
            ):
                continue
        subscribers_to_notify.append(int(user_id))
    return subscribers_to_notify  # Return list of subscribers to notification


# Make sure that subscription file exists
if not os.path.exists(SUBSCRIPTIONS_DATA_FILEPATH):
    logger.info("Creating subscriptions fluid_data file...")
    update_subscriptions(DEFAULT_SUBSCRIPTION_FILE_CONTENT)
# Make sure that subscription file includes the schema
logger.info("Ensuring that subscription file matches schema...")
subscriptions_schema = get_available_subscriptions()
subscriptions = get_subscriptions()
for category_name, category_data in subscriptions_schema.items():
    file_changed = False
    if category_name not in subscriptions["subscriptions"]:
        logger.info(f"Adding category {category_name} to available subscriptions...")
        subscriptions["subscriptions"][category_name] = {}
        file_changed = True
    for subcategory in category_data["subcategories"]:
        if subcategory not in subscriptions["subscriptions"][category_name]:
            logger.info(f"Adding subcategory {subcategory} to {category_name}...")
            subscriptions["subscriptions"][category_name][subcategory] = {
                "subscriptions": {}
            }
            file_changed = True
    if file_changed:
        logger.info("Updating subscriptions file...")
        update_subscriptions(subscriptions)
    else:
        logger.info("Subscription file matches schema. All good!")
