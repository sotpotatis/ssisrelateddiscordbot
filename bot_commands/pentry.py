'''pentry.py
Contains commands related to "pentryansvar".
'''
from nextcord.ext.commands import Cog
from nextcord.ext import tasks
from utils.pentry import get_pentry_data, get_pentryansvar
import logging
from nextcord import Embed
#Logging
logger = logging.getLogger(__name__)

class Pentry(Cog):
    def __init__(self, bot):
        '''Initializes the cog.'''
        self.bot = bot

    @tasks.loop(hours=24)
    async def pentryansvar_task_loop(self):
        '''The pentryansvar task loop checks if information about pentryansvar has been sent for the current week, or if the data has changed.
        If not, it will try to fix that by downloading information.'''
        logger.info("Checking for pentryansvar information...")
        pentryansvar_data = get_pentryansvar()
        pentryansvar_message_channel = self.bot.get_channel(pentryansvar_data["pentry_information_channel_id"])
