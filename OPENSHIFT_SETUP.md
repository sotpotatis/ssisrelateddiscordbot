# OpenShift Setup

This is a tutorial about how to get the bot up and running on an OpenShift server.
It is made for the GUI and mainly adapted for the Stockholm Science & Innovation School's self-hosted server,
which is where I am running the bot.

## Instructions

1. Create a new project in OpenShift:
- Click "Add" in the sidebar
- Choose "Import from Git"
- For the git repo URL, enter `https://github.com/sotpotatis/ssisrelateddiscordbot.git`
- When asked for build strategy, select "Dockerfile".

2. Add a `PersitentVolumeClaim`:
- Click "Project" in the sidebar
- Click on "0 PersistentVolumeClaims"

    *Alternative*:
- Click on

3. Attach the volume to the bot:
- Click on "Topology" in the sidebar
- Right click the OpenShift logo inside the frame of your project and select "Add storage"
- Under "`PersistentVolumeClaim`", select the previously created volume.
- To avoid any further configuration, use `/ssis_bot_data` as the mount path.
- Leave subpath empty.

4. Edit the `BuildConfig`:
- Click on "Builds" in the sidebar
- Select the build config for the bot and click on it
- Go to "Environment" and fill out at least the `SSIS_BOT_TOKEN` environment variable.
Set it to the bot token to use.