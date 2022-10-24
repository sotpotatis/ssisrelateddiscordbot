'''good_morning.py
The iconic "good morning" message. This has been a heart of the school server for a long time
and will at the time of this writing be brought back. And of course I am overly dramatic but it
is a total cornerstone and it makes peoples days and of course I should have brought it back earlier.
Sorry.

And for the technical stuff, the bot will send the message once someone says something that matches "good morning"
or similar. In case any other people say good morning, the bot will react with the "blush" emoji.'''
import logging
import random
from nextcord.ext.commands import Cog, Bot
from nextcord import Message, Emoji
from utils.good_morning import get_good_morning_data, check_is_good_morning_message, write_to_good_morning_file, \
    ACTION_SEND_MESSAGE, ACTION_REACT, GOOD_MORNING_RESPONSES, GOOD_MORNING_REACTION_EMOJI
from utils.general import get_now


class GoodMorning(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @Cog.listener("on_message")
    async def on_message(self, message: Message):
        message_action = check_is_good_morning_message(message, self.bot.user.id)
        # Check if any action s have to be done
        if message_action == ACTION_SEND_MESSAGE:
            self.logger.info("Sending a good morning message...")
            response_string = random.choice(GOOD_MORNING_RESPONSES)
            self.logger.info("Writing data to file...")
            good_morning_data = get_good_morning_data()
            good_morning_data["message_sent_at"] = str(get_now().date())
            write_to_good_morning_file(good_morning_data)
            self.logger.info("Data were written to file.")
            await message.reply(response_string)
            self.logger.info("Good morning message sent.")
        if message_action is not None:
            # React to good morning message
            self.logger.info("Reacting to a good morning message...")
            await message.add_reaction(GOOD_MORNING_REACTION_EMOJI)
            self.logger.info("Message reacted to.")
