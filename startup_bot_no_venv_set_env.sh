#!/usr/bin/bash
#startup_bot_no_venv_set_env.sh
#Script to startup the bot without using a virtual environment,
#but with code to set some environment variables.
if [[ -z "${SSIS_BOT_TOKEN}" ]];then
  SSIS_BOT_TOKEN="BOT TOKEN HERE"
fi
if [[ -z "${SSIS_BOT_WORKING_DIRECTORY}" ]];then
  SSIS_BOT_WORKING_DIRECTORY="BOT DIRECTORY HERE"
fi
#Below sets are optional if you're going to report to Healthchecks.
if [[ -z "${HEALTHCHECKS_PING_URL}" ]];then
  HEALTHCHECKS_PING_URL="HEALTHCHECKS PING URL"
fi
if [[ -z "${HEALTHCHECKS_PING_FREQ}" ]];then
  HEALTHCHECKS_PING_FREQ=2 #Ping frequency in minutes
fi
echo "Running bot..."
python3 SSIS_BOT_WORKING_DIRECTORY