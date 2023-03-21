"""schedule_caching.py
This file contains some helper functions for handling schedules.
The bot can handle schedules by caching them from the SSIS Schedule API a few times a day,
and that is basically everything that this file handles."""
import datetime

from utils.general import (
    write_json,
    get_json,
    get_active_classes,
    CACHED_SCHEDULE_DATA_FILEPATH,
    get_now,
    BASE_TIMEZONE,
)
import aiohttp, logging, os

logger = logging.getLogger(__name__)

# Constants
DEFAULT_SCHEDULE_JSON = {"schedules": {}, "downloaded_at": None}
CACHED_SCHEDULE_TIMEOUT = (
    60 * 60 * 12
)  # Value in seconds - require caching at least every 12 hours (60 sec * 60 min * 12 hours)
MINIMUM_TIME_BETWEEN_CACHES = (
    60 * 15
)  # Value in seconds - allow caching max once every 15 minutes

# Helper functions
def get_schedule_file():
    """Gets content in the cached schedule file"""
    return get_json(CACHED_SCHEDULE_DATA_FILEPATH)


def update_schedule_file(new_content):
    """Updates the schedule file with new content.

    :param new_content: New content to write to the file."""
    write_json(CACHED_SCHEDULE_DATA_FILEPATH, new_content)


# Create file if doesn't exists
if not os.path.exists(CACHED_SCHEDULE_DATA_FILEPATH):
    logger.info("Creating schedule information file...")
    update_schedule_file(DEFAULT_SCHEDULE_JSON)


def get_cached_schedules():
    """Gets all cached schedules for all active classes.
    If there are no cached schedules for a class, that class's content
    gets replaced with None instead."""
    logger.debug("Getting cached schedules...")
    cached_schedules = get_schedule_file()
    wanted_classes = get_active_classes()
    now = get_now()
    schedules = {}
    for class_name in wanted_classes:
        schedule_data = (
            None  # Set None as schedule fluid_data but look for active schedule below
        )
        if class_name in cached_schedules["schedules"]:
            logger.debug("Class found in file, checking if it has been cached today...")
            schedule_cached_at = datetime.datetime.fromisoformat(
                cached_schedules["schedules"][class_name]["cached_at"]
            ).astimezone(BASE_TIMEZONE)
            if (now - schedule_cached_at).total_seconds() <= CACHED_SCHEDULE_TIMEOUT:
                logger.debug("Schedule has been cached within the allowed timeout.")
                schedule_data = cached_schedules["schedules"][class_name]
            else:
                logger.debug(
                    f"Schedule for {class_name} was cached too long ago ({schedule_cached_at})!"
                )
        else:
            logger.warning(
                f"No cached schedule found for {class_name} (class is not cached)!"
            )
        schedules[class_name] = schedule_data  # Add name to fluid_data
    return schedules  # Return parsed schedule fluid_data


async def cache_schedules():
    """Attempts to cache schedules by downloading them from SSIS's schedule server."""
    logger.info("Attempting to caching schedules...")
    cached_schedules = get_schedule_file()
    now = get_now()
    last_cached_at = cached_schedules["downloaded_at"]
    last_cached_at_parsed = (
        datetime.datetime.fromisoformat(last_cached_at).astimezone(BASE_TIMEZONE)
        if last_cached_at != None
        else None
    )
    if (
        last_cached_at_parsed == None
        or (now - last_cached_at_parsed).total_seconds() >= MINIMUM_TIME_BETWEEN_CACHES
    ):
        logger.info("Caching is allowed. Downloading...")
        # Get all classes that we should download
        classes_to_retrieve = get_active_classes()
        for class_to_retrieve in classes_to_retrieve:
            logger.debug(f"Downloading schedule for {class_to_retrieve}...")
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        "https://api.ssis.nu/cal",
                        params={"room": class_to_retrieve},
                        headers={
                            "User-Agent": "Python/SSIS Discord Bot Schedule Parser"
                        },
                    ) as request:
                        if request.status == 200:
                            logger.info("Request to SSIS API succeeded.")
                            # Parse content - we get nothing if there is no schedule available
                            content = await request.text()
                            if len(content) == 0:
                                logger.info("No schedule available for class today.")
                                raw_class_schedule = {}
                            else:
                                logger.info("Schedule available for today.")
                                raw_class_schedule = await request.json()
                        else:
                            logger.critical(
                                f"Request to SSIS API failed with status code {request.status}."
                            )
                            raw_class_schedule = {}
                    await session.close()
                except Exception as e:
                    logger.critical(
                        f"Something failed in the request to the SSIS API (error {e} occurred).",
                        exc_info=True,
                    )
                    raw_class_schedule = {}
            logger.info(f"Schedule for {class_to_retrieve}: {raw_class_schedule}")
            # Generate schedule content and save
            class_schedule = {
                "cached_at": str(now),
                "schedule_content": raw_class_schedule,
            }
            cached_schedules[class_to_retrieve] = class_schedule
        logger.info("Writing update schedule fluid_data...")
        cached_schedules["downloaded_at"] = str(now)
        update_schedule_file(cached_schedules)
        logger.info("Cached schedules updated.")
    else:
        logger.critical(
            f"Will not cache schedules - time since last cache is too little! {last_cached_at_parsed} was last cache time."
        )
