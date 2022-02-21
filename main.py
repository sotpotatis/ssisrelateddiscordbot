'''main.py
Runs the bot.'''
import logging, nextcord, os
from nextcord.ext import commands #Import command handler
from bot_commands import clubs, predefined_messages, menu #Import bot commands

#Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

#Get bot token
BOT_TOKEN = os.environ.get("SSIS_BOT_TOKEN")

bot = commands.Bot(command_prefix="ssisb")
logger.info("Adding cogs...")
bot.add_cog(clubs.Clubs(bot))
bot.add_cog(predefined_messages.PredefinedMessages(bot))
bot.add_cog(menu.Menu(bot))
logger.info("Cogs added.")

logger.info("Logging in...")
bot.run(BOT_TOKEN)
