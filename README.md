# SSIS (Stockholm Science & Innovation School)-related Discord Bot

This Discord bot is has various capabilities related to the school Stockholm Science & Innovation School.

### Feature breakdown

#### Lunch menu information

* The bot can retrieve lunch menu information and edit a message it has created with a lunch menu message on a given time each day. 

* The bot can send PM's with the lunch menu to users who has subscribed to it. (*this is on the wishlist*)

#### School pentry responsibilities ("Pentryansvar")

* The bot can send a message to a given channel every week with who has "Pentryansvar" in the school.

#### School club management system

* The bot can manage roles for school clubs (both owners and non-owners).
* The bot can handle subscriptions for people who want to subscribe to school club channels.

#### Administrative commands

* Administrators can manage some features of the bot, like adding new clubs.

> Note that all commands except administrative commands are made using slash commands. Administrative commands are called using text commands

#### Tech stack
* Using nextcord, a fork of discord.py (which nowadays has been discontinued)

### Setup

> Note: this section has to be improved with more details.
 
* Run `setup_script.sh`
* Edit the configurations files as needed in `data/`
