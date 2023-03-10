#Project dockerfile
#If you think "Docker is cool" or if you just want to run ssisrelateddiscordbot
#in a Docker containter, here is the file for that ;)
#Psst! This deploys on the school's OpenShift cluser without a problem ;)
FROM python:3.9
# Set environment variables related to directories
ENV SSIS_DISCORD_BOT_FLUID_DATA_DIRECTORY "/ssis_bot_data/fluid_data"
ENV SSIS_DISCORD_BOT_LOGGING_DIRECTORY "/ssis_bot_data/logging"
COPY /fluid_data /ssis_bot_data/fluid_data
# Copy everything else
COPY . /bot
WORKDIR /bot
# Install requirements
RUN pip install -r requirements.txt
# Run app
CMD ["python", "main.py"]