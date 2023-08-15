"""main.py
Runs the bot."""
import logging, nextcord, os
from logging.handlers import RotatingFileHandler
from nextcord.ext import commands  # Import command handler
from bot_commands import graduation_notice  # Import bot commands
from dotenv import load_dotenv

load_dotenv()
# Set up logging
logger = logging.getLogger(__name__)
# Add handler for console output
log_console_handler = logging.StreamHandler()
LOG_LEVELS = {  # Mapping: human readable string --> logging level.
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}
try:
    log_level = LOG_LEVELS[os.environ.get("SSIS_BOT_LOG_LEVEL", "warning")]
except KeyError:
    raise KeyError("Invalid log level entered.")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=log_level,
    handlers=[log_console_handler],
)  # Set log level to debug and add rotating file handler
# Get bot token
BOT_TOKEN = os.environ.get("SSIS_BOT_TOKEN")
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="ssisb ", intents=intents)
logger.info("Adding cogs...")
cogs = [graduation_notice.GraduationNotice]
i = 1
for cog in cogs:  # Add every cog
    bot.add_cog(cog(bot))
    logger.info(f"Cog {i}/{len(cogs)} added.")
    i += 1
logger.info("Cogs added.")
logger.info("Logging in...")
bot.run(BOT_TOKEN)  # Start bot and log in
