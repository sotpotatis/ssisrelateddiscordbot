'''general.py
Function that contains some general bot tasks, such as changing its status.
'''
from nextcord.ext.commands import Cog
from nextcord.ext import tasks, commands
from nextcord import Status, Embed, Activity
import logging, aiohttp, os, random
from utils.general import generate_error_embed, get_now, BOT_GENERAL_STATUSES

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
        #self.change_status_new.start() # Start task for changing status - TODO implement
        self.change_status.start() # Start task for changing status every once in a while

    def cog_unload(self):
        '''Runs when the cog is unloaded.'''
        self.report_ping_to_healthchecks.cancel() #Cancel task on cog unload.
        #self.change_status_new.start() # Start task for changing status to something schedule related - TODO implement
        self.change_status.cancel() # Cancel task for changing status every once in a while

    @Cog.listener()
    async def on_ready(self):
        '''Handler for when the bot becomes ready.'''
        logger.info("Bot is ready!")

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

    @tasks.loop(hours=1)
    async def change_status(self):
        """Changes status of the bot at most every 2 hours"""
        logger.info("Checking for status change...")
        await self.bot.wait_until_ready()
        if random.randint(1,2) == 1 or self.bot.activity is None:
            logger.info("Status of bot should be changed. Generating random status...")
            new_status = random.choice(BOT_GENERAL_STATUSES)
            activity = Activity(type=new_status["type"], name=new_status["text"])
            logger.info(f"Changing status to {new_status['type']}, {new_status['text']}.")
            await self.bot.change_presence(status=Status.online, activity=activity)
        else:
            logger.info("Checked for a status change, but it isn't the time yet.")

    @tasks.loop(minutes=3)
    async def change_status_new(self):
        '''Changes the bot status. The status will be changed to something related to current lessons
        if there is a schedule available. If not, it will be changed to something else.'''
        logger.info("Changing status...")
        now = get_now()
        #Check if schedules are available
        schedule = None
        if now.hour < 9 or now.hour > 17: #No lessons - set general status
            general_status = True
        else:
            general_status = True if schedule == None else False

        if general_status:
            logger.info("Using a general status.")
            status = random.choice(BOT_GENERAL_STATUSES)
            activity = Activity(type=status["type"], name=status["text"])
            logger.info(f"New status: {status}. Changing...")
            await self.bot.change_presence(status=Status.online, activity=activity)
            logger.info("Bot status set.")
        else:
            logger.info("Using informational status.")
            # TODO: Implement


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
