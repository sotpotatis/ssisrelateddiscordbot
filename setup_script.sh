#setup_script.py
#The setup script can be used to quickly setup the bot.
#NOTE: This does not include setting any advanced configuration parameters. It simply installs all the requirements.

echo "Setup script started..."
#Create virtual environment
pip3 install virtualenv
PROJECT_FOLDER=$(pwd)
cd .. #Move up one level to create venv
echo "Creating venv..."
virtualenv $PROJECT_FOLDER
echo "Venv created."
cd $PROJECT_FOLDER #Move back
source $PROJECT_FOLDER/bin/activate
echo "Venv activated."
echo "Installing dependencies..."
pip install -r "requirements.txt"
echo "Dependencies installed."
#Ask for token
DISCORD_BOT_TOKEN=$(read -s -p "Please enter your Discord bot token: ")
#Save the token
echo "Setting token as environment variable..."
echo export SSIS_BOT_TOKEN=$DISCORD_BOT_TOKEN >> $PROJECT_FOLDER/bin/activate
echo "Token saved as environment variable."
#Do some other things
#Save working directory
echo "export SSIS_BOT_WORKING_WORKING_DIRECTORY=$(pwd)" >> ~/.bashrc
chmod +x "startup_bot.sh" #Change permissions of bot startup script
#Reload session
. ~/.bashrc
echo "BashRC reloaded."
echo "Done! You should be good to go after editing some files in data/."
