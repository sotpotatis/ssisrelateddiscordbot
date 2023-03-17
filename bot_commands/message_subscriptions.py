"""message_subscriptions.py
A file to interact with the subscription feature, which allows users to
subscribe to get certain messages."""
import logging
from nextcord.ext.commands import Cog
import nextcord
from nextcord import Interaction, SlashOption, Embed
from utils import subscription
from utils.general import generate_error_embed
from utils.color_const import MESSAGE_SUBSCRIPTIONS_EMBED_COLOR


class SubscribedMessagesSubscription(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @nextcord.slash_command(description="Prenumerera på ett meddelandeutskick.")
    async def subscribe_to_message(
        self,
        interaction: Interaction,
        category: str = SlashOption(
            name="kategori", description="Meddelandekategori att prenumerera på"
        ),
        subcategory: str = SlashOption(
            name="meddelandetyp", description="Meddelandetyp att prenumerera på"
        ),
    ):
        """Subscribes to a certain subcategory."""
        self.logger.info("Got a request to subscribe to a club category...")
        # Check if user is subscribed
        if subscription.is_subscribed_to(interaction.user, category, subcategory):
            self.logger.info("User is already subscribed!")
            error_embed = generate_error_embed(
                "Redan prenumererad",
                "Du har redan prenumererat på denna meddelandekanal.",
            )
            await interaction.response.send_message(embed=error_embed, delete_after=60)
            return
        self.logger.info("Subscribing user...")
        subscription.change_subscriber_status(
            category, subcategory, interaction.user, True
        )
        self.logger.info("User was subscribed.")
        final_embed = Embed(
            title="✔Prenumererad!",
            description=f"""Jag har prenumererat dig för att få meddelanden för `{category}`/`{subcategory}`.
            Du kan avprenumerera närsomhelst med kommandot `/unsubscribe_to_message`.""",
            color=MESSAGE_SUBSCRIPTIONS_EMBED_COLOR,
        )
        final_embed.add_field(
            name="Viktigt!",
            value="""Se till att jag kan slidea in i dina DMs... 😉 
        Om du har blockerat mig eller har utökade sekretessinställningar på kommer du inte att få meddelanden från mig.""",
            inline=False,
        )
        final_embed.set_footer(
            text="Psst! Detta meddelande raderas automatiskt efter 60 sekunder."
        )
        await interaction.response.send_message(embed=final_embed, delete_after=60)
        self.logger.info("User subscription handled.")

    @nextcord.slash_command(description="Avrenumerera på ett meddelandeutskick.")
    async def unsubscribe_to_message(
        self,
        interaction: Interaction,
        category: str = SlashOption(
            name="kategori", description="Meddelandekategori att prenumerera på"
        ),
        subcategory: str = SlashOption(
            name="meddelandetyp", description="Meddelandetyp att prenumerera på"
        ),
    ):
        """Unsubscribes to a certain subcategory."""
        self.logger.info("Got a request to unsubscribe to a club category...")
        # Check if user is subscribed
        if not subscription.is_subscribed_to(interaction.user, category, subcategory):
            self.logger.info("User is not subscribed!")
            error_embed = generate_error_embed(
                "Inte prenumererad",
                "Aj då! Jag kan inte avprenumerera dig, för det verkar som att du inte är prenumererad!",
            )
            await interaction.response.send_message(embed=error_embed, delete_after=60)
            return
        self.logger.info("Unsubscribing user...")
        subscription.change_subscriber_status(
            category, subcategory, interaction.user, False
        )
        self.logger.info("User was unsubscribed.")
        final_embed = Embed(
            title="Avprenumererad!",
            description=f"""Jag har avprenumererat dig för att få meddelanden för `{category}`/`{subcategory}`.
                Ångrat dig? Du kan närsomhelst använda `/subscribe_to_message` för att catcha up igen 😉.""",
            color=MESSAGE_SUBSCRIPTIONS_EMBED_COLOR,
        )
        final_embed.set_footer(
            text="Psst! Detta meddelande raderas automatiskt efter 60 sekunder."
        )
        await interaction.response.send_message(embed=final_embed, delete_after=60)
        self.logger.info("User unsubscription handled.")

    @subscribe_to_message.on_autocomplete("category")
    @unsubscribe_to_message.on_autocomplete("category")
    async def autocomplete_category(self, interaction: Interaction, category: str):
        """Function to autocomplete category"""
        subscriptions = subscription.get_subscriptions()
        if not category:  # Provide whole list of categories if none exist.
            self.logger.debug("Autocompleting categories by returning all...")
            await interaction.response.send_autocomplete(
                list(subscriptions["subscriptions"].keys())
            )
        else:  # If a category ID has been set
            self.logger.debug("Autocompleting categories by closest values...")
            closest_category_ids = [
                available_category
                for available_category in subscriptions["subscriptions"].keys()
                if available_category.startswith(category)
            ]
            await interaction.response.send_autocomplete(closest_category_ids)

    @subscribe_to_message.on_autocomplete("subcategory")
    @unsubscribe_to_message.on_autocomplete("subcategory")
    async def autocomplete_subcategory(
        self, interaction: Interaction, subcategory: str, category: str
    ):
        subscriptions = subscription.get_subscriptions()
        if not subcategory:
            subcategories = list(subscriptions["subscriptions"][category].keys())
            if category:
                self.logger.debug("Autocompleting subcategory list by returning all..")
                await interaction.response.send_autocomplete(subcategories)
            else:
                self.logger.debug(
                    "Autocompleting subcategory list by closest values..."
                )
                closest_subcategory_ids = [
                    available_subcategory
                    for available_subcategory in subcategories
                    if available_subcategory.startswith(subcategory)
                ]
                await interaction.response.send_autocomplete(closest_subcategory_ids)
