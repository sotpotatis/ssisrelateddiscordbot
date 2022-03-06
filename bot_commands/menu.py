'''menu.py
Contains commands related to menu.

The function mostly uses a task loop
'''
from nextcord.ext.commands import Cog
from nextcord.ext import tasks
from nextcord import Embed
from utils.menu import *
from utils.general import get_now
from utils.color_const import MENU_EMBED_COLOR

class Menu(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_menu_message.start() #Start task for sending and editing menu messages

    def cog_unload(self):
        '''Function that calls when the cog is unloaded.
        Updates all the menu messages.'''
        self.update_menu_message.cancel()

    def get_dish_text_for(self, dishes, day):
        '''Converts a list of dish names into a human-readable format.

        :param dishes: A list of the dish names.

        :param day: Data for the day that information is being sent about.'''
        day_dishes_text = ""
        for dish in dishes:
            dish_text = dish
            #Highlight certain features - a bit hacky but functioning
            if day["special_features"]["sweet_tuesday"]:
                logger.debug("Highlighting Sweet Tuesday...")
                dish_text = dish_text.replace("Sweet Tuesday", "**🍰 Sweet Tuesday**")
            elif day["special_features"]["fruity_wednesday"]:
                logger.debug("Highlighting Fruity Wednesday...")
                dish_text = dish_text.replace("Fruity Wednesday", "**🍓 Fruity Wednesday**")
            elif day["special_features"]["pancake_thursday"]:
                logger.debug("Highlighting Pancake Thursday...")
                dish_text = dish_text.replace("Pancake Thursday", "**🥞 Pancake Thursday**")
            elif day["special_features"]["burger_friday"]:
                logger.debug("Highlighting Burger Friday...")
                dish_text = dish_text.replace("Burger Friday", "**🍔 Burger Friday**")
            day_dishes_text += dish_text + "\n"
        return day_dishes_text

    @tasks.loop(hours=1)
    async def update_menu_message(self, *args, **kwargs):
        '''Updates the menu message if it should be updated.
        Since I maintain this server, I think a request per hour is totally reasonable.
        TODO: Make this command callable by admins if needed'''
        logger.info("Waiting until bot is ready to update menu message...")
        await self.bot.wait_until_ready()  #Wait until the bot is ready
        logger.info("Bot is ready to update menu message...")
        now = get_now()
        current_week = now.isocalendar()[1]
        search_week = current_week if now.isoweekday() < 6 else current_week +1 #On weekends, try to search for data for the next week instead
        menu_data = await get_eatery_menu(menu_id=521, week=search_week)
        logger.debug(f"Menu data: {menu_data}.")
        saved_menu_data = get_menu_data()
        current_menu_data = get_menu_data()["cached_menu"]
        if menu_data != None:
            logger.info("Menu data is available.")
            menu_data = menu_data["menu"]
            saved_menu_data["cached_menu"] = menu_data
            saved_menu_data["menu_cached_at"] = str(get_now())
            final_message = Embed(
                title=f"📄 {menu_data['title']}",
                description="Nedan hittar du veckomenyn.",
                color=MENU_EMBED_COLOR,
                url="https://20alse.ssis.nu/lunch"
            )
            #For each day, add a field with the day menu items
            for day in menu_data["days"].values():
                logger.debug(f"Adding information for day: {day}")
                day_name = day["day_name"]["swedish"]
                logger.debug(f"Adding data for day {day_name}...")
                day_dishes = day["dishes"]
                day_dishes_text = self.get_dish_text_for(day_dishes, day)
                final_message.add_field(name=day_name, value=day_dishes_text, inline=False) #Add information about the dish
        else: #If no menu data is available, add information about that the bot is looking for menu data.
            logger.info("Menu data is not available. Editing messages...")
            final_message = Embed(
                title=f"📄 Ingen veckomeny tillgänglig",
                description="Är det helg, så kom tillbaka på måndag. Är det inte helg så har jag inte koll på menyn just nu. Då är mitt bästa tips att du kollar om menyn finns [här](https://eatery.se/meny/521/lunchmeny-7/).",
                color=MENU_EMBED_COLOR,
                url="https://20alse.ssis.nu/lunch"
            )
        final_message.set_footer(text=f"Drivs av 20alse Eatery Lunch API | Meddelande uppdaterat {get_now().strftime('%Y-%m-%d %H:%M')}")
        #Attempt to edit previous message - if fails, send new message
        logger.info("Trying to edit previous message...")
        #Retrieve channel where menu information messages should be sent to
        information_channel_id = saved_menu_data["menu_information_channel_id"]
        logger.debug(f"Retrieving channel {information_channel_id}")
        information_channel = self.bot.get_channel(information_channel_id)
        logger.info("Saved channel retrieved.")
        logger.debug(f"Channel is: {information_channel}.")
        try:
            previous_week_message = await information_channel.fetch_message(saved_menu_data["menu_information_message_ids"]["week"])
            await previous_week_message.edit(embed=final_message)
        except:
            logger.info("Failed to edit previous message. Sending a new one...")
            week_message = await information_channel.send(embed=final_message)
            saved_menu_data["menu_information_message_ids"]["week"] = week_message.id
        #And there's also a "today" message. However, we don't want to spam the channel - if we can't send the message, we should just simply ignore it
        #Retrieve current day
        current_day_number = get_now().isoweekday()
        day_mappings = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        current_day_name = day_mappings[current_day_number-1]
        logger.info(f"It is {current_day_name} today. Checking for meny data...")
        final_day_message = Embed(
            title=f"🍽 Mat för idag ({get_now().strftime('%d/%m-%Y')})",
            description="Här hittar du maten för idag. Om meddelandet inte har uppdaterats, kolla efter nya meddelanden eller kolla ovanför detta meddelande.",
            color=MENU_EMBED_COLOR,
            url="https://20alse.ssis.nu/lunch"
        )
        final_day_message.set_footer(text=f"Drivs av 20alse Eatery Lunch API | Meddelande uppdaterat {get_now().strftime('%Y-%m-%d %H:%M')}.") #Add informational footer about latest update
        if menu_data != None and current_day_name in menu_data["days"] and search_week == current_week: #Check if menu data for the current day is available
            logger.info("Menu data for day is available.")
            today = menu_data["days"][current_day_name] #Get data for today
            final_day_message.add_field(name="Idag", value=self.get_dish_text_for(today["dishes"], today))
        else:
            logger.info("Menu data for day is not available.")
            final_day_message.add_field(name="Idag", value="Ingen meny finns tillgänglig.")
        try:
            if saved_menu_data["menu_information_message_ids"]["day"] == None:
                logger.info("Sending day information message...")
                day_message = await information_channel.send(embed=final_day_message)
                saved_menu_data["menu_information_message_ids"]["day"] = day_message.id
            else:
                logger.info("Trying to edit today message...")
                previous_day_message = await information_channel.fetch_message(saved_menu_data["menu_information_message_ids"]["day"])
                await previous_day_message.edit(embed=final_day_message)
                logger.info("Today message was edited.")
        except Exception as e:
            logger.warning("Failed to send today menu message! It will be ignored.", exc_info=True)
        #Now, update JSON
        logger.info("Updating cached menu JSON...")
        write_menu_data(saved_menu_data)
        logger.info("Cached menu JSON written to file.")

