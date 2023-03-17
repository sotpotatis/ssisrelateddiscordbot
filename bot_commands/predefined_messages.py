"""predefined_messages.py
The predefined messages are some informational messages about various functions that the bot can post on demand.
To avoid spam, only admins can query this.
"""
import nextcord, logging
from nextcord.ext.commands import Cog, has_permissions, is_owner
from nextcord import Interaction, SlashOption, Embed
from utils.predefined_messages import *
from utils.general import ensure_admin_permissions

# Logging
logger = logging.getLogger(__name__)


class PredefinedMessages(Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        description="Skickar ett hjälp/-infomeddelande till en kanal om någon av bottens funktioner."
    )
    @is_owner()
    async def send_help_message(
        self,
        interaction: Interaction,
        message_id: str = SlashOption(
            name="meddelande", description="Det meddelande som du vill skicka"
        ),
    ):
        logger.info("Got a request to send a help/informational message!")
        # Validate permissions
        if not await ensure_admin_permissions(
            self.bot, interaction.user, interaction.guild, interaction
        ):
            return  # Exit the function if the user isn't an admin
        # Get predefined message
        predefined_message = get_predefined_message(message_id)
        logger.info("Predefined message retrieved. Converting into embeddable...")
        final_message = Embed(
            title=predefined_message["title"]
            if "title" in predefined_message
            else "Information",
            description=predefined_message[
                "message"
            ],  # All predefined messages must have descriptions
            color=predefined_message["color"],
        )
        if "fields" in predefined_message:
            logger.debug("Fields specified. Iterating through them...")
            for field in predefined_message["fields"]:
                # Add field
                final_message.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=False if "inline" not in field else field["inline"],
                )  # All fields must have a name and a value.
        logger.info("Done. Sending predefined message...")
        await interaction.channel.send(embed=final_message)

    @send_help_message.on_autocomplete("message_id")
    async def autocomplete_predefined_messages(
        self, interaction: Interaction, message_id: str
    ):
        """Function to autocomplete a predefined message name."""
        logger.debug("Autocompleting predefined message name...")
        predefined_message_ids = list(get_predefined_messages().keys())
        # Note: This is based on the autocomplete example from https://github.com/nextcord/nextcord/blob/master/examples/application_commands/autocompleted_command.py
        if not message_id:  # If a message ID has not been provided yet
            logger.debug(
                "Message ID has not been autocompleted yet. Providing a whole list..."
            )
            await interaction.response.send_autocomplete(predefined_message_ids)
        else:  # If a predefined message ID has been provided, try to find the closest one
            logger.debug("Message ID has been provided. Using closest value.")
            closest_predefined_message_ids = [
                predefined_message_id
                for predefined_message_id in predefined_message_ids
                if message_id.startswith(predefined_message_id)
            ]
            logger.debug("Sending autocomplete response...")
            await interaction.response.send_autocomplete(closest_predefined_message_ids)
