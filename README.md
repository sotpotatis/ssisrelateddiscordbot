# SSIS-related Discord Bot

(SSIS=Stockholm Science & Innovation School)

This Discord bot is has various capabilities related to the school Stockholm Science & Innovation School.

> **Warning**
>
> On 2023-03-10, the basic file structure of the bot was changed.
> Please see [this document](MIGRATE_MARCH_2023.md) for more information.

### Feature breakdown

#### Lunch menu information

![Week menu message](screenshots/week_menu.png)

- The bot can retrieve lunch menu information and edit a message it has created with a lunch menu message on a given time each day.

- The bot can send PM's with the lunch menu to users who has subscribed to it. (_this is on the wishlist_)

#### School pentry responsibilities ("Pentryansvar")

![Pentryansvar message](screenshots/pentry.png)

- The bot can send a message to a given channel every week with who has "Pentryansvar" in the school.
  For curious outsiders, this is who are responsible for keeping the dishwashers running in the shared school
  pentries.

#### School club management system

![Clubs](screenshots/clubs.png)

- The bot can manage roles for school clubs (both owners and non-owners).
- The bot can handle subscriptions for people who want to subscribe to school club channels.

#### Administrative commands

- Administrators can manage some features of the bot, like adding new clubs.

> Note that all commands except administrative commands are made using slash commands. Administrative commands are called using text commands.

#### Good morning messages

- The bot will respond with a randomized text response to the first "good morning" message each day sent at a time considered to be morning in the #general channel on the server.
- If the bot detects a message containing "good morning"-related content but the requirements on the first point is not met, the bot will react with an emoji. Standard is the blush emoji,
  with some exceptions during holidays etc.

#### Automated profile picture changes

- The bot will automatically change profile picture when it is a holiday (spring, Halloween, etc.) and use a general profile picture when no holiday period is active.

#### Tech stack

- Using nextcord, a fork of discord.py. I started using this because it supported slash commands and because discord.py got discontinued,
  but it has since then been reborn. Once it gets stable slash command support, this project should switch over to it as soon as possible.

### Setup

#### Retrieving stuff you need

- Of course, you need a Discord Bot token.

- If desired, you can set up some tracking so you get notifications in case the bot goes down.
  If so, you need to set the environment variable `HEALTHCHECKS_PING_URL` to a URL you get when creating a [Healthchecks](https://healthchecks.io)
  check. The default ping frequency is every two minutes, but you can change it if you wish by setting the environment variable `HEALTHCHECKS_PING_FREQ`
  environment variable. This value is in minutes.

_Getting the data correct_

- Edit the configurations files as needed in `data/`:
  - Edit `clubs.json` to add information about clubs
  - Edit `predefined_message.json` to change any of the predefined messages
  - Edit `roles.json` to change the IDs for admin roles.

#### For development (will setup a Virtualenv, run on Linux or WSL)

- Run `setup_script.sh`

For automatic pre-commit formatting using [Black](https://black.readthedocs.io/en/stable/):

- Make sure you have [Pre-commit](https://pre-commit.com) installed.
- Run `pre-commit install`.

#### For production

##### Running using Docker:

###### [Recommended for SSIS students] Running using the Stockholm Science & Innovation School Openshift Cluster

- The reason I recommend this is because the cluser is both very underrated as of today as well as there is a full configuration tutorial
  available. See [the tutorial](OPENSHIFT_SETUP.md) for more instructions.

###### Running user a Dockerfile

- There is a `Dockerfile` available in the repository. This file will by default run the bot and also set
  a subpath, `/ssis_bot_data`, which you should (in some kind of way) mount a volume to for storing user data.
  Docker does not by default provide a filesystem that is retained by default if you just use a build. You may also edit environment variables,
  see below (or optionally, see [general.py](utils/general.py)) for an overview of available file-related variables.

###### Running user Docker-Compose:

- There is an example `docker-compose.yml` file in the repository which includes setup for a volume
  for storing data.

##### Running manually on some kind of Linux-based computer:\*

- There are multiple files available in this repository that has bash scripts and `systemd` services
  which will help you with running the bot. See the following files:

  - If you want to use a `virtualenv` in production, see
    - `ssisbot.service`
    - `startup_bot.sh`
  - If you do _not_ want to use a `virtualenv` in production (and set environment variables directly), see
    - `ssisbot_novenv.service`
    - `startup_bot_no_venv_set_env.sh`

  The latter of these configurations have ran on a school-provided VM.

#### List of available environment variables for configuration

##### Required:

- `SSIS_BOT_TOKEN`: The Discord token for the bot.

##### Optional:

- `HEALTHCHECKS_PING_URL`: A ping URL to a [Healthchecks](https://healthchecks.io) check where the bot
  periodically pings to indicate that it is active. The default ping frequency if not set is 2 minutes.
- `HEALTCHECKS_PING_FREQ`: The ping frequency to any enabled Healthchecks ping. See `HEALTHCHECKS_PING_URL`. Default
  value if unset is 2 minutes.

  > **Note**
  >
  > See the [OpenShift tutorial](OPENSHIFT_SETUP.md) (combined with the [Dockerfile](Dockerfile))
  > for an example of how fluid storage can be set up with environment variables

- `SSIS_DISCORD_BOT_DIRECTORY`: Choose the base directory where the code for the bot can be found. The default is the working directory,
- `SSIS_DISCORD_BOT_STORAGE_IS_FLUID`: If you are using some kind of Docker-like host or other configuration that require
  you to use a different path for the `fluid_data` and the `logging` directory (which updates when the bot is running), set this variable to `True`.
  Valid values are `True` or `False` (or other Python bool-convertible). The default value if unset is `False`.
- `SSIS_DISCORD_BOT_FLUID_STORAGE_BASE_PATH`: If you have enabled the fluid storage option, specify where you have mounted a volume for fluid storage. Default if unset is empty.
- `SSIS_DISCORD_BOT_SOURCE_FLUID_DATA_DIRECTORY`: When the fluid storage function (see above) is enabled, the bot will compare the source code's fluid data structure
  and see if the required directories and files have been copied over to the `SSIS_DISCORD_BOT_FLUID_STORAGE_BASE_PATH`. If not, a copy will be ran. This environment variable should therefore
  point to the source `SSIS_DISCORD_BOT_SOURCE_FLUID_DATA_DIRECTORY`. On default, it will point to the `fluid_data` in the current working directory, which should be what you need in most cases.
- `SSIS_DISCORD_BOT_FLUID_DATA_DIRECTORY`: Set a path for the where the `fluid_data` directory is. The default is the `SSIS_DISCORD_BOT_DIRECTORY`/`SSIS_DISCORD_BOT_FLUID_STORAGE_BASE_PATH` (if any)/`fluid_data`
- `SSIS_DISCORD_BOT_STATIC_DATA_DIRECTORY`: Set a path for the where the `static_data` directory is. The default is the `SSIS_DISCORD_BOT_DIRECTORY`/`SSIS_DISCORD_BOT_FLUID_STORAGE_BASE_PATH` (if any)/`static_data`
