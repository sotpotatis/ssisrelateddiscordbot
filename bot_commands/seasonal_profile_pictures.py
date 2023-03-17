"""seasonal_profile_pictures.py
Contains a cog to change bot profile pictures depending on the current season.
Used to implement special profile pictures for spring, Christmas, etc."""
from nextcord.ext import commands, tasks
import logging, os, datetime, pytz
from utils.general import (
    SEASONAL_PROFILE_PICTURES_FILEPATH,
    get_json,
    get_now,
    SEASONAL_PROFILE_PICTURES_DIRECTORY,
    BASE_TIMEZONE,
)


class SeasonalProfilePictures(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """Initializes the seasonal profile pictures cog."""
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.check_profile_picture_is_correct.start()  # Start task for checking profile picture

    def cog_unload(self):
        """Function that runs each time the cog is unloaded."""
        self.check_profile_picture_is_correct.cancel()

    @tasks.loop(hours=1)
    async def check_profile_picture_is_correct(self, *args, **kwargs):
        """Checks that the bot's profile picture is correct and matches
        the current one active for this season."""
        self.logger.info("Ensuring profile picture matches seasonal profile picture...")
        # Since this is essentially optional, allow an optional check
        if not os.path.exists(SEASONAL_PROFILE_PICTURES_FILEPATH):
            self.logger.warning(
                "No seasonal profile picture path is set! Seasonal profile pictures will be disabled."
            )
            return
        seasonal_profile_pictures = get_json(SEASONAL_PROFILE_PICTURES_FILEPATH)
        # Iterate over seasonal profile pictures
        now = get_now()
        currently_active_profile_picture = None
        for seasonal_profile_picture in seasonal_profile_pictures["seasonal"]:
            active_from = seasonal_profile_picture["active_from"]
            active_to = seasonal_profile_picture["active_to"]
            active_from_dt = datetime.datetime(year=now.year, **active_from).astimezone(
                tz=pytz.timezone(BASE_TIMEZONE)
            )
            active_to_dt = datetime.datetime(year=now.year, **active_to).astimezone(
                tz=pytz.timezone(BASE_TIMEZONE)
            )
            if active_from_dt <= now <= active_to_dt:
                self.logger.info("Found currently active profile picture!")
                currently_active_profile_picture = seasonal_profile_picture
        if currently_active_profile_picture is None:
            if "fallback" in seasonal_profile_pictures:
                currently_active_profile_picture = seasonal_profile_pictures["fallback"]
                self.logger.info(
                    "No currently active profile picture, but we have a fallback."
                )
            else:
                self.logger.info("No currently active profile picture and no fallback.")
                return
        else:
            self.logger.info("Found currently active profile picture!")
        # Open image
        image_data = open(
            os.path.join(
                SEASONAL_PROFILE_PICTURES_DIRECTORY,
                currently_active_profile_picture["filename"],
            ),
            "rb",
        ).read()
        await self.bot.wait_until_ready()
        await self.bot.user.edit(avatar=image_data)
        self.logger.info(
            f"Active image was ensured to {currently_active_profile_picture['filename']}."
        )
