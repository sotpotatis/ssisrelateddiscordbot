'''general.py
Function that contains some general bot tasks, such as changing its status.
'''
from nextcord.ext.commands import Cog
from nextcord.ext import tasks, commands
from nextcord import Status,  ActivityType, Activity, Embed
import logging, aiohttp, os
from utils.general import generate_error_embed

logger = logging.getLogger(__name__)

"""
The bot can report that it is up and running to Healthchecks.io.
This is a service that I use for keeping track that my scripts and stuff are running
properly, and I highly recommend it to anyone.
The function is optional: you can disable it by not setting the environment variable
HEALTHCHECKS_PING_URL.
"""
HEALTHCHECKS_PING_URL = os.environ.get("HEALTHCHECKS_PING_URL")
HEALTHCHECKS_PING_FREQ = int(os.environ.get("HEALTHCHECKS_PING_FREQ")) if "HEALTHCHECKS_PING_FREQ" in os.environ else 2 #Default ping frequency is every 2 minutes
logger.info(f"Healthchecks settings: Ping URL: {HEALTHCHECKS_PING_URL}, ping frequency: {HEALTHCHECKS_PING_FREQ} (minutes)")

class General(Cog):
    def __init__(self, bot):
        '''Initializes the general cog which contains general commands.'''
        self.bot = bot

        #Check if Healthchecks integration has been configured (see above)
        if HEALTHCHECKS_PING_URL != None:
            logger.info("A Healthchecks ping URL has been specified. Healthchecks will be enabled.")
            self.report_ping_to_healthchecks.start() #Start the task for Healthchecks
        else:
            logger.warning("A Healthchecks ping URL has not been specified. (You can ignore this message unless you intend to track the bot using Healthchecks)")

    def cog_unload(self):
        '''Runs when the cog is unloaded.'''
        self.report_ping_to_healthchecks.cancel() #Cancel task on cog unload.

    @Cog.listener()
    async def on_ready(self):
        '''Handler for when the bot becomes ready.'''
        logger.info("Bot is ready!")
        #Set status
        logger.info("Setting bot status...")
        activity = Activity(type=ActivityType.playing, name="SSIS Bot | Lyssnar på kommandon!")
        await self.bot.change_presence(status=Status.online, activity=activity)
        logger.info("Bot status set.")

    @tasks.loop(minutes=HEALTHCHECKS_PING_FREQ)
    async def report_ping_to_healthchecks(self):
        '''The bot can report that it is up and running to Healthchecks.io.
        This is a service that I use for keeping track that my scripts and stuff are running
        properly, and I highly recommend it to anyone.
        The function is optional: you can disable it by not setting the environment variable
        HEALTHCHECKS_PING_URL.'''
        logger.info("Reporting ping status to Healthchecks...")
        async with aiohttp.ClientSession() as session:
            async with session.get(HEALTHCHECKS_PING_URL) as request:
                if request.status == 200: #Check if request was successful
                    logger.info("Ping to Healthchecks was successful.")
                else:
                    logger.warning("Ping to Healthchecks failed!")

    @commands.command(name="eval")
    @commands.is_owner() #Make this only callable by owner
    async def eval(self, ctx, command: str):
        '''Eval command. (of course, this is only callable by the owner)'''
        logger.info("Kör eval-kommando...")
        try:
            result = eval(command)
            final_embed = Embed(
                title="Eval har körts",
                description=f"Resultat: `{result}`"
            )
            logger.info("Eval har körts.")
        except Exception as e:
            logger.info(f"Eval misslyckades ({e})")
            final_embed = generate_error_embed("Eval misslyckades", f"Ett fel inträffade: {e}.")
        await ctx.send(embed=final_embed)
