'''pentry.py
Contains commands related to "pentryansvar".
'''
from nextcord.ext.commands import Cog
from nextcord.ext import tasks
from utils.pentry import get_pentryansvar_data, get_pentryansvar, write_pentryansvar_data
from utils.general import get_now, class_name_to_role, find_person_tag
from utils.color_const import PENTRYANSVAR_EMBED_COLOR
import logging
from nextcord import Embed
#Logging
logger = logging.getLogger(__name__)

class Pentry(Cog):
    def __init__(self, bot):
        '''Initializes the cog.'''
        self.bot = bot
        self.pentryansvar_task_loop.start() #Start pentryansvar task loop

    def cog_unload(self):
        '''Runs when the cog is unloaded.'''
        self.pentryansvar_task_loop.cancel() #Cancel task on cog unload

    @tasks.loop(hours=24)
    async def pentryansvar_task_loop(self):
        '''The pentryansvar task loop checks if information about pentryansvar has been sent for the current week, or if the data has changed.
        If not, it will try to fix that by downloading information.'''
        logger.info("Checking for pentryansvar information...")
        logger.info("Waiting until bot is ready...")
        await self.bot.wait_until_ready()
        logger.info("Bot is ready.")
        #Don't perform the check on weekends
        if get_now().isoweekday() <= 7:
            pentryansvar_data = await get_pentryansvar()
            cached_pentryansvar_data = get_pentryansvar_data() #This is some data that we have saved about the previous message
            if pentryansvar_data == None:
                logger.warning("Pentryansvar data is not available. Check will be skipped.")
                return #Stop the task
            pentryansvar_message_channel = self.bot.get_channel(cached_pentryansvar_data["pentry_information_channel_id"])

            """
            We have the following conditions now:
            * New week --> Create a new message and post it
            * Old week --> Check if cached data is different --> If yes, update the old message
            """
            last_information_message_sent_for_week = cached_pentryansvar_data["information_message"]["for_week"]
            current_week = get_now().isocalendar()[1] #Get the current week number
            if last_information_message_sent_for_week == current_week:
                logger.info("Message for this week has already been sent.")
                #Check if data has changed
                if cached_pentryansvar_data["cached_data"] != pentryansvar_data:
                    logger.info("Data on server has changed! The message will be updated.")
                    send_new_information_message = False
                else:
                    logger.info("The data has not been changed. The message will not be updated.")
                    return #Stop the task
            else:
                logger.info("Message for this week has not been sent. A new one will be generated.")
                send_new_information_message = True
            #Generate the message
            logger.info("Generating new message with pentry data...")
            final_message = Embed(
                title="Pentryansvar",
                description="Här nedanför ser du vilka som har pentryansvar denna vecka.",
                url="https://20alse.ssis.nu/pentry", #Add link to pentryansvar website
                color=PENTRYANSVAR_EMBED_COLOR
            )
            final_message.set_footer(text="Glöm inte pentryansvaret, så vi slipper högar med koppar och disk i pentryt. Tack!")
            #Sort pentries by number
            pentry_number_sort = lambda pentry: int(pentry["pentry_number"])
            pentryansvar_data.sort(key=pentry_number_sort)
            logger.debug("Pentries sorted.")
            guild = self.bot.get_guild(cached_pentryansvar_data["find_roles_in_guild"]) #Get the guild that we are using for roles
            logger.debug("Guild retrieved.")
            for pentry in pentryansvar_data:
                #Try to find the respective roles for the responsible class
                responsible_class = await class_name_to_role(self.bot, guild, pentry["responsible_class"])
                if responsible_class == None:
                    logger.info("Class role not available.")
                    responsible_class = pentry["responsible_class"].capitalize() #Use the string provided by the API
                else:
                    logger.info("A class role is available.")
                    responsible_class = responsible_class.mention
                responsible_persons = ""
                for person_name in pentry["responsible_persons"]:
                    person_tag = await find_person_tag(self.bot, guild, person_name,  pentry['responsible_class'])
                    responsible_persons += "%s "%(person_tag.mention if person_tag != None else person_name + ",")
                logger.info("Text for responsible persons generated.")
                responsible_persons = responsible_persons.strip(",") #Remove trailing commans
                pentry_field_text = f"📣 **{'Ansvarig klass' if responsible_class != 'Personal' else 'Ansvariga'}**: {responsible_class}" #Create text for responsible persons. Handle a scenario where the school staff ("Personal") has pentryansvar.
                #Add responsible persons if set
                if len(responsible_persons) > 0:
                    logger.info("Adding information about responsible persons...")
                    pentry_field_text += f"\n👥**Ansvariga personer**: {responsible_persons}"
                else:
                    logger.info("Information about responsible persons in the pentry not available.")
                final_message.add_field(name=f"➡ {pentry['pentry_name']}",
                                        value=pentry_field_text,
                                        inline=False)
            #Send the message or edit it
            if send_new_information_message:
                logger.info("Sending new message...")
                pentry_message = await pentryansvar_message_channel.send(embed=final_message)
                logger.info("New pentryansvar message sent.")
                cached_pentryansvar_data["information_message"] = {
                    "id": pentry_message.id,
                    "for_week": current_week
                }
                logger.debug("Information message parameters updated in memory.")
            else:
                logger.info("Editing previous message...")
                previous_message = await pentryansvar_message_channel.fetch_message(cached_pentryansvar_data["information_message"]["id"])
                await previous_message.edit(embed=final_message)
                logger.info("Previous message edited.")
            cached_pentryansvar_data["cached_data"] = pentryansvar_data #Save cached data
            cached_pentryansvar_data["message_last_updated_at"] = str(get_now()) #Update update date
            logger.debug("Cached pentryansvar data updated in memory.")
            logger.info("Updating previous cached data...")
            write_pentryansvar_data(cached_pentryansvar_data)
            logger.info("Updated previous cached data.")
        else:
            logger.info("It is weekend. A check will not be performed.")
        logger.info("Done with pentryansvar message task.")
