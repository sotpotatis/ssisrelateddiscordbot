'''menu.py
Contains commands related to menu.

The function mostly uses a task loop
'''
import datetime
from nextcord.ext.commands import Cog
from nextcord.ext import tasks
from nextcord import Embed
from utils.menu import *
from utils.general import get_now, get_current_day_name, MAIN_SERVER_ID
from utils.color_const import MENU_EMBED_COLOR
import utils.subscription as subscription

#Text that links to where you can find the week menu
WEEK_MENU_LINK_TEXT = "Veckomenyn kan du hitta [här](https://20alse.ssis.nu/lunch) alternativt [här](https://www.eatery.se/kista-nod)."

class Menu(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_menu_message.start()  # Start task for sending and editing menu messages
        self.send_subscribed_menu_messages.start()  # Start task for sending out subscribed menu messages

    def cog_unload(self):
        '''Function that calls when the cog is unloaded.
        Cancels updating of all the menu messages.'''
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
            day_dishes_text += "* " + dish_text + "\n"
        return day_dishes_text

    def menu_is_available(self, menu_data):
        '''Checks if menu data from today is available.

        :param menu_data: The menu data received from get_eatery_menu.'''
        return menu_data is not None and get_current_day_name() in menu_data["days"]

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
        menu_data = await get_eatery_menu(menu_id=DEFAULT_EATERY_MENU_ID, week=search_week)
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
            week_message = await information_channel.send_message(embed=final_message)
            saved_menu_data["menu_information_message_ids"]["week"] = week_message.id
        #And there's also a "today" message. However, we don't want to spam the channel - if we can't send the message, we should just simply ignore it
        #Retrieve current day
        current_day_name = get_current_day_name()
        logger.info(f"It is {current_day_name} today. Checking for meny data...")
        final_day_message = Embed(
            title=f"🍽 Mat för idag ({get_now().strftime('%d/%m-%Y')})",
            description="Här hittar du maten för idag. Om meddelandet inte har uppdaterats, kolla efter nya meddelanden eller kolla ovanför detta meddelande.",
            color=MENU_EMBED_COLOR,
            url="https://20alse.ssis.nu/lunch"
        )
        final_day_message.set_footer(text=f"Drivs av 20alse Eatery Lunch API | Meddelande uppdaterat {get_now().strftime('%Y-%m-%d %H:%M')}.") #Add informational footer about latest update
        if self.menu_is_available(menu_data) and search_week == current_week: #Check if menu data for the current day is available
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

    async def send_daily_menu_message(self):
        '''Sends out a daily menu message to subscribers. This message contains information about the daily menu.'''
        logger.info("Sending out daily menu message...")
        # Check if menu is available
        now = get_now()
        today_name = get_current_day_name()
        week = now.isocalendar()[1]
        menu_data = await get_eatery_menu(DEFAULT_EATERY_MENU_ID, week)
        if menu_data != None:
            menu_data = menu_data["menu"]
        if self.menu_is_available(menu_data):
            logger.info("Menu is available.")
            # Get who to send out the message to
            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
            subscribers_to_send_messages_to = subscription.get_users_not_notified_after(midnight, "food", "daily")
            logger.info(f"Sending menu information messages to {len(subscribers_to_send_messages_to)} subscribers.")
            subscriptions_data = subscription.get_subscriptions()
            day_menu_data = menu_data["days"][today_name]
            day_menu_text = self.get_dish_text_for(day_menu_data["dishes"], day_menu_data)
            daily_menu_message = Embed(
                title="🍽️ Mat idag på Eatery",
                description=f"Hej där! Här är dagens meny på Eatery:",
                color=MENU_EMBED_COLOR
            )
            daily_menu_message.add_field(name="Meny", value=day_menu_text, inline=False)
            daily_menu_message.add_field(name="Se veckomenyn", value=WEEK_MENU_LINK_TEXT, inline=False)
            for subscriber_user_id in subscribers_to_send_messages_to:
                try:
                    user = self.bot.get_user(subscriber_user_id)
                    if user is not None:
                        await user.send(embed=daily_menu_message)
                    else:
                        raise Exception("User is None.")
                    logger.info(f"Successfully sent message to {user.mention}.")
                    subscriptions_data["subscriptions"]["food"]["daily"]["subscriptions"][str(subscriber_user_id)]["last_notified_at"] = str(now)
                except Exception as e:
                    logger.warning(f"Failed to send menu information to {subscriber_user_id}. This might be because their DMs are closed (exception was: {e}).", exc_info=True)
            # Update subscription data
            if len(subscribers_to_send_messages_to) > 0:
                logger.info("Updating subscription tracking file...")
                subscription.update_subscriptions(subscriptions_data)
        else:
            logger.warning("Menu is not available. No daily message will be sent!")

    async def send_weekly_menu_message(self):
        '''Sends out a weekly menu message with the week menu to subscribers.'''
        logger.info("Sending out weekly menu message...")
        now = get_now()
        week_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=7-now.isoweekday())
        logger.info(week_start)
        # Check if menu is available
        menu_data = await get_eatery_menu(DEFAULT_EATERY_MENU_ID, now.isocalendar()[1])
        if menu_data != None:
            menu_data = menu_data["menu"]
        if self.menu_is_available(menu_data):
            logger.info("Week menu is available.")
            # Get who to send the message to
            subscribers_to_send_messages_to = subscription.get_users_not_notified_after(week_start, "food", "weekly")
            menu_message = Embed(
                title=menu_data["title"],
                description="Nedan hittar du menyn.",
                color=MENU_EMBED_COLOR
            )
            subscription_data = subscription.get_subscriptions()
            for day in menu_data["days"].keys():
                day_data = menu_data["days"][day]
                menu_text = self.get_dish_text_for(day_data["dishes"], day_data)
                menu_message.add_field(name=day_data["day_name"]["swedish"], value=menu_text, inline=False)
            menu_message.add_field(name="Se menyn", value=WEEK_MENU_LINK_TEXT, inline=False)
            for subscriber_user_id in subscribers_to_send_messages_to:
                try:
                    user = self.bot.get_user(subscriber_user_id)
                    if user is not None:
                        await user.send(embed=menu_message)
                        logger.info(f"Successfully sent weekly menu to user: {user.mention}.")
                        subscription_data["subscriptions"]["food"]["weekly"]["subscriptions"][str(subscriber_user_id)]["last_notified_at"] = str(get_now())
                    else:
                        raise Exception("User is None.")
                    
                except Exception as e:
                    logger.warning(f"Failed to send menu message to user {subscriber_user_id}. The user might have their DMs closed. The error was: {e}.", exc_info=True)
            logger.info(f"Processed weekly menu messages for {len(subscribers_to_send_messages_to)} subscribers.")
        else:
            logger.warning("Week menu is not available! No weekly message will be sent.")


    @tasks.loop(hours=1)
    async def send_subscribed_menu_messages(self):
        '''Sends out menu messages to people that have subscribed to the menu if a message hasn't been sent to them today already.'''
        now = get_now()
        await self.bot.wait_until_ready() # Wait until the bot is ready
        logger.info("Checking sending of menu messages...")
        # Do not send out messages before 8AM and not after 10PM
        if 9 <= now.hour >= 22:
            logger.info("Will not send out menu message, is too late.")
            return
        logger.info("Checking and sending out messages...")
        await self.send_daily_menu_message()
        logger.info("Handled daily menu messages. Moving on to weekly ones...")
        await self.send_weekly_menu_message()
        logger.info("Handled weekly menu messages.")

