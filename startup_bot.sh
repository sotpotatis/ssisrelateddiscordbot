#startup_bot.sh
#Script that can be used to quickly startup the bot when using virtual environments
echo "Starting up SSIS Bot..."
echo "Activating virtual environment..."
echo "Starting bot..."
$SSIS_BOT_WORKING_DIRECTORY/bin/python $SSIS_BOT_WORKING_DIRECTORY/main.py #Run bot
