#Project dockerfile
#If you think "Docker is cool" or if you just want to run ssisrelateddiscordbot
#in a Docker containter, here is the file for that ;)
#Psst! This deploys on the school's OpenShift cluser without a problem ;)
FROM python:3.9
COPY . /bot
WORKDIR /bot
# Install requirements
RUN pip install -r requirements.txt
# Run app
CMD ["python", "main.py"]