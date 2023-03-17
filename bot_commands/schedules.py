"""schedule_caching.py
Contains bot commands related to school schedules as well as tasks
for downloading them."""
import logging
from nextcord.ext.commands import Cog, Bot
from nextcord.ext import tasks
from utils import schedule_caching
from utils.general import get_now


class Schedules(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @tasks.loop(minutes=30)
    async def cache_schedules(self):
        self.logger.debug("Caching schedules...")
        await schedule_caching.cache_schedules()
        self.logger.debug("Schedule caching complete.")

    @tasks.loop(minutes=5)
    async def send_schedule_messages(self):
        """Checks for any messages related to the school schedule should be sent.
        and sends them to subscribed users if available."""
        self.logger.debug("Sending out schedule messages...")
        await self.bot.wait_until_ready()
        self.logger.debug("Bot is ready!")
        # Get current time
        now = get_now()
        if (
            now.hour < 8 or now.hour > 18
        ):  # Skicka inte scheman efter ett visst klockslag
            self.logger.info("Ska inte kolla efter schemameddelanden nu.")
            return
