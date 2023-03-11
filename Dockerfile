#Project dockerfile
#If you think "Docker is cool" or if you just want to run ssisrelateddiscordbot
#in a Docker containter, here is the file for that ;)
#Psst! This deploys on the school's OpenShift cluser without a problem ;)
FROM python:3.9
# Set environment variables related to directories
ENV SSIS_DISCORD_BOT_STORAGE_IS_FLUID = "True"
ENV SSIS_DISCORD_BOT_FLUID_STORAGE_BASE_PATH = "/ssis_bot_data"
COPY . /bot
WORKDIR /bot
# Install requirements
RUN pip install -r requirements.txt
# Run app
CMD ["python", "main.py"]