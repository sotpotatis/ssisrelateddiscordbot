# OpenShift Setup

This is a tutorial about how to get the bot up and running on an OpenShift server.
It is made for the GUI and mainly adapted for the Stockholm Science & Innovation School's self-hosted server,
which is where I am running the bot.

## Instructions

1. **Create a new project in OpenShift:**

- Click "Add" in the sidebar
- Choose "Import from Git"
- For the git repo URL, enter `https://github.com/sotpotatis/ssisrelateddiscordbot.git`
- When asked for build strategy, select "Dockerfile".

2. **Add a `PersitentVolumeClaim`:**

- Click "Project" in the sidebar
- Click on "0 PersistentVolumeClaims"

  _Alternative_:

- Click on "Search" in the sidebar
- Under the "Resources" dropdown next to the search field, select `PersistentVolumeClaim`
- Click on the blue "Create new `PersistentVolumeClaim`" button that should pop up.

3. **Attach the volume to the bot:**

- Click on "Topology" in the sidebar
- Right click the OpenShift logo inside the frame of your project and select "Add storage"
- Under "`PersistentVolumeClaim`", select the previously created volume.
- To avoid any further configuration, use `/ssis_bot_data` as the mount path.
- Leave the subpath option empty.

4. **Edit the `BuildConfig`:**

- Click on "Builds" in the sidebar
- Select the build config for the bot and click on it
- Go to "Environment" and fill out at least the `SSIS_BOT_TOKEN` environment variable.
  Set it to the bot token to use. See the [README.md](README.md) for other valid options.

5. **Rebuild if needed**

- You probably need to rebuild the project after changing the environment variables. In the top right corner of the screen where
  you should be if you just finished Step 4 (the `BuildConfig` configuration screen), click on the `Actions` dropdown in the top right corner
  and select `Start build`
  _Alternative:_
- Click on "Builds" in the sidebar.
- On the `BuildConfig` for the bot, click on the three dots and select "Start build"

6. **Verifying that everything works**

You probably want to verify that the bot is working properly. Here is a tip on how to do so:

- Click on "Project" in the sidebar
- Look under "Recent events" on the right and see if you see any warnings
- Look under the usage graph and check if it looks like things are running (there are some CPU usage, the pod count hasn't recently increased, etc.)
- Under "Inventory" to the left, click on "Pods" and see if there are any warnings or errors for your pods.
  You can also click on a pod to get its logs! (select the pod that does not seem to be related with a build, click on it and then click on "Logs")
