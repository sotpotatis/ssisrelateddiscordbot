#startup_bot.sh
#Script that can be used to quickly startup the bot
echo "Starting up SSIS Bot..."
echo "Activating venv..."
source "$SSIS_BOT_WORKING_WORKING_DIRECTORY/venv/bin/activate/"
echo "Starting bot..."
python $SSIS_BOT_WORKING_WORKING_DIRECTORY #Run bot
