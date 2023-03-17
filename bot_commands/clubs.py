"""CLUB COMMANDS
Manages bot_commands related to school clubs.
Note that some commands here have been migrated from slash commands to "regular commands".
This is because I am waiting for a proper way to handle slash command permissions in nextcord.
"""
from nextcord.ext import commands
import logging, nextcord, asyncio
from nextcord import Interaction, SlashOption
from utils.clubs import *
from utils.general import generate_error_embed
from utils.color_const import CLUBS_EMBED_COLOR

logger = logging.getLogger(__name__)

# Create a list of clubs
club_data = get_clubs_data()
club_name_options = {club["title"]: club["id"] for club in club_data["clubs"]}


class Clubs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        description="Prenumerera på en klubb och få notiser när klubben har något att meddela."
    )
    async def subscribe_to_club(
        self,
        interaction: Interaction,
        club_id: str = SlashOption(
            name="klubb", description="Den klubb som du vill prenumerera på"
        ),
        # choices=club_name_options)
    ):
        logger.info("Got a request to subscribe to a club!")
        # Get club
        found_club = get_club_by_id(club_id)
        # Add user as a subscriber if not already subscribed
        if not is_subscriber_to_club(found_club, interaction.user):
            logger.info("Adding user as subscriber...")
            # Grant role to user
            role = interaction.guild.get_role(found_club["role_id"])
            if role not in interaction.user.roles:
                await interaction.user.add_roles(role)
            add_subscriber_to_club(club_id, interaction.user)
        logger.info("Addition done. Sending message...")
        final_embed = Embed(
            title="✅ Du lades till!",
            description=f"{interaction.user.mention}, du har nu blivit tillagd och kommer att bli notifierad om uppdateringar från klubben.",
            color=CLUBS_EMBED_COLOR,
        )
        final_embed.add_field(
            name="Avprenumerera",
            value=f"För att avprenumerera från meddelanden, använd kommandot `/unsubscribe_to_club {club_id}`.",
            inline=False,
        )
        final_embed.set_footer(
            text="Psst! Detta meddelande kommer att tas bort efter 60 sekunder."
        )
        message = await interaction.response.send_message(
            embed=final_embed, delete_after=60
        )
        logger.debug("Queuing deletion of user message...")
        await asyncio.sleep(60)
        # Remove the user's message
        await interaction.message.delete()
        await message.delete()
        logger.debug("User message has been deleted.")

    @nextcord.slash_command(
        description="Avprenumerera på en klubb som du har prenumererat att få notiser på."
    )
    async def unsubcribe_to_club(
        self,
        interaction: Interaction,
        club_id: str = SlashOption(
            name="klubb", description="Den klubb som du vill avprenumerera på"
        ),
        # choices=club_name_options)
    ):
        logger.info("Got a request to unsubscribe to a club.")
        # Check if the user is subscribed
        club_data = get_club_by_id(club_id)
        user_id = interaction.user.id
        if not is_subscriber_to_club(club_data, interaction.user):
            logger.info("The user is not a subscriber to the club!")
            await interaction.response.send_message(
                embed=generate_error_embed(
                    title="Du prenumererar inte",
                    description="Du har inte signat upp för notiser till klubben, så jag kan inte avprenumerera dig.",
                ),
                delete_after=60,
            )
            return
        else:
            logger.info("The user is subscribing to the club. Removing...")
            # Remove role from user
            role = interaction.guild.get_role(club_data["role_id"])
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
            remove_subscriber_from_club(club_id, interaction.user)
        # Send confirmation message
        final_embed = Embed(
            title="✅ Avprenumererad",
            description="Du har avprenumereats från klubben. Du borde inte längre få några notiser från den.",
            color=CLUBS_EMBED_COLOR,
        )
        final_embed.set_footer(
            text="Psst! Detta meddelande kommer att tas bort efter 60 sekunder."
        )
        message = await interaction.response.send_message(embed=final_embed)
        logger.debug("Queuing deletion of user message...")
        await asyncio.sleep(60)
        # Remove the user's message
        await interaction.message.delete()
        logger.interaction("User message has been deleted.")

    @nextcord.slash_command(
        description="Detta kommando listar alla klubbar som du kan prenumerera på."
    )
    async def list_clubs(self, interaction: Interaction):
        logger.info("Got a request to list clubs!")
        # Create a pretty list of clubs
        clubs = get_clubs_data()
        final_embed = Embed(
            title="Klubbar",
            description="Här hittar du en lista på tillgängliga klubbar. Genom att prenumerera på någon av dessa, så får du meddelanden varje gång klubben har något att meddela.",
            color=CLUBS_EMBED_COLOR,
        )
        # Iterate through clubs and add information
        for club in clubs["clubs"]:
            logger.debug(f"Handling club data for {club['id']}")
            club_subscription_command = f"**För att prenumerera på denna klubb, använd kommandot `/subscribe_to_club {club['id']}`**"
            # To add a description to the club, set the JSON key "description". The bot adds links to informational messages by default.
            description = ""
            if club["description"] != None:
                logger.debug("Adding set club description to message...")
                description += club["description"]
            if "links" in club:  # Here, you can add a links about the club
                for link in club["links"]:
                    # Both dict and string is allowed as configuration here
                    if type(link) == dict:
                        description += f"- [{link['name']}]({link['url']})"
                    else:
                        description += f"- [Mer information]({link})"
            description += (
                f"\n{club_subscription_command}"  # Add command to subscribe to club
            )
            final_embed.add_field(
                name=f"{club['title']}",
                value=f"{club['emoji'] if club['emoji'] != None else ''}\n{description}",
                inline=False,
            )
        logger.info("List of clubs created. Sending message...")
        await interaction.response.send_message(embed=final_embed)

    @commands.command(description="Detta kommando lägger till en ny klubb.")
    async def add_club(
        self,
        ctx,
        interaction: Interaction,
        club_title: str,  # (description="Titeln som klubben ska ha (t.ex. \"Togethernet\"", required=True),
        club_description: str,  # =SlashOption(description="En kort beskrivning av klubben", required=True),
        role: nextcord.Role,  # = SlashOption(description="Rollen som prenumeranter ska ha", required=False),
        owners_role: nextcord.Role,
    ):  # = SlashOption(description="Rollen som klubbens ägare ska ha", required=False)):
        """Admin command to add a club. Note that this command was originally a slash command, but it has now been migrated
        to a regular command."""
        logger.info("Got a request to add a club!")
        # Generate club fluid_data
        club_id = club_title.replace(" ", "_").replace(
            "-", "_"
        )  # Generate a club ID based on the title
        # Create a role for the club if not specified
        if role == None:
            logger.info("Creating base role...")
            role = await interaction.guild.create_role(name=f"{club_title} - Notiser")
            logger.info("Base role created.")
        else:
            logger.info("Base role specified. Using it...")
        # Create a role for owners of the club if not specified
        if owners_role == None:
            logger.info("Creating role for responsible person...")
            owners_role = await interaction.guild.create_role(
                name=f"Ansvarig - {club_title}"
            )
            logger.info("Role for responsible person created.")
        else:
            logger.info("Role for responsible person specified. Using it...")
        club_data = {
            "title": club_title,
            "description": club_description,
            "id": club_id,
            "emoji": None,
            "role_id": role.id,
            "owners_role_id": owners_role.id,
            "owners": [],
            "subscribers": [],
            "created_at": str(get_now()),
        }
        clubs_data = get_clubs_data()
        clubs_data["clubs"].append(club_data)
        write_clubs_data(clubs_data)
        logger.info("Club created! Sending message...")
        await ctx.send(
            embed=Embed(  # interaction.response.send_message
                title="✅ Klubb skapad!",
                description=f"Klubben har skapats och folk kan nu prenumerera på den. Använd rollen {role.mention} för att skicka ut notiser. Glöm inte att använda kommandot `/add_club_owners` för att lägga till ansvariga för klubben.",
                color=CLUBS_EMBED_COLOR,
            )
        )

    # @nextcord.slash_command(description="Lägg till en användare för att vara ägare för en klubb. Denne får en roll som ansvarig.")
    @commands.command(
        description="Lägg till en användare för att vara ägare för en klubb. Denne får en roll som ansvarig."
    )
    async def add_club_owner(
        self,
        ctx,  # interaction: Interaction,
        club_id: str,  # = SlashOption(name="klubb",
        # description="Den klubb som du vill lägga till användaren i"),
        # choices=club_name_options)
        user: nextcord.Member,
    ):  # = SlashOption(name="anvandare", description="Användaren som ska läggas till som ägare/ansvarig för klubben.")):
        logger.info("Got a request to add a club owner!")
        # Get club
        club_data, club_index = get_club_by_id(club_id, return_index=True)
        # Validate that the club exists
        if club_data is None:
            logger.debug("The club does not exist. Returning error...")
            await ctx.send(
                embed=generate_error_embed(
                    "Klubben du försöker lägga till en användare",
                    "Klubben du försöker lägga till existerar inte. (skriv in klubbens ID, om du är osäker tagga Albin Seijmer TE20A)",
                )
            )
        clubs_data = get_clubs_data()
        # Add user as owner
        club_data["owners"].append(user.id)
        logger.info("Awarding role to new user...")
        owner_role = ctx.guild.get_role(
            club_data["owners_role_id"]
        )  # interaction.guild.get_role
        if owner_role not in user.roles:
            await user.add_roles(owner_role)
            logger.info("Role awarded to user.")
        else:
            logger.info("User already has owner role.")
        clubs_data[club_index] = club_data
        write_clubs_data(clubs_data)
        logger.info("Done!")
        await ctx.send(
            embed=Embed(  # interaction.response.send_message
                title="✅ Ansvarig tillagd!",
                description=f"{user.mention} has lagts till som ansvarig för klubben.",
                color=CLUBS_EMBED_COLOR,
            )
        )

    @subscribe_to_club.on_autocomplete("club_id")
    @unsubcribe_to_club.on_autocomplete("club_id")
    # @add_club_owner.on_autocomplete("club_id") Note: This handler has now been commented out until there is a nice way for permission handling slash commands in nextcord.
    async def autocomplete_club_name(self, interaction: Interaction, club_id: str):
        """Function to autocomplete a club name."""
        logger.debug("Autocompleting club name...")
        club_ids = get_club_ids()
        # Note: This is based on the autocomplete example from https://github.com/nextcord/nextcord/blob/master/examples/application_commands/autocompleted_command.py
        if not club_id:  # If no club ID has been sent, send all of them
            logger.debug("Club name has not been set yet. Providing whole list...")
            await interaction.response.send_autocomplete(club_ids)
        else:  # If a club ID has been set, find the closest ones and return
            logger.debug("Club name has been set. Using closest values...")
            closest_club_ids = [
                available_club_id
                for available_club_id in club_ids
                if club_id.startswith(available_club_id)
            ]
            await interaction.response.send_autocomplete(closest_club_ids)
