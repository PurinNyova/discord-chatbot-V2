import discord
from classes import PersonalityManager, CacheManager
from functions import getTxt, load_model
from init import logger, TOKEN, BOT_INVITE_URL, DISCORD_CLIENT_ID, MAX_CACHE
from chatWithAI import chatWithAI, openaiDescribe
from discord.ext import commands
from typing import Optional
from dbtest import read_cache_data
import requests


#Discord Bot Initial Setup
intents = discord.Intents.default()
intents.message_content = True  # This intent is required to read message content
intents.messages = True  # Required for message.reference
intents.invites = True
bot = commands.Bot(command_prefix="s!", intents=intents)  # Using the Client class

@bot.event
async def on_ready():
    logger.info(f"We have logged in as {bot.user.name}. Invite URL: {BOT_INVITE_URL}")
    logger.info(f"Token: {TOKEN}")
    logger.info(f"ID = {DISCORD_CLIENT_ID}")
    await bot.tree.sync()

@bot.tree.command(name="modelpick", description="Pick an AI model")
@discord.app_commands.choices(option=[discord.app_commands.Choice(name=modelsx["model_name"], value=str(i)) for i, modelsx in enumerate(load_model().values())])
@discord.app_commands.describe(option="Available Models")
async def modelpick(interaction: discord.Interaction, option: discord.app_commands.Choice[str]):
    dataHandler = CacheManager(interaction.guild.id)
    models = load_model()
    if option.value == 0:
        logger.info(f"{models["0"]["url"]} selected, attempting connection.")
        try:
            response = requests.get(models["0"]["url"], timeout=5)  # 5 seconds timeout
            if response.status_code == 200:
                dataHandler.data.activeModel = option.value
                dataHandler.change_data()
                await interaction.response.send_message(f"Model {option.value} selected and the {models["0"]["url"]} is online.")
            else:
                await interaction.response.send_message(f"The endpoint returned status code: {response.status_code}. Endpoint may be offline.")
        except requests.exceptions.RequestException as e:
            await interaction.response.send_message(f"The endpoint {models["0"]["url"]} is offline or there was an error: {e}")
    else:
        logger.info(f"{models[option.value]["url"]} selected, attempting connection.")
        try:
            response = requests.get(f"{models[option.value]["url"]}/models",
                                    timeout=5,
                                    headers={"Authorization": f"Bearer {models[option.value]["api_key"]}"})  # 5 seconds timeout
            if response.status_code == 200:
                dataHandler.data.activeModel = option.value
                dataHandler.change_data()
                await interaction.response.send_message(f"Model {option.value} selected and the {models[option.value]["url"]} is online.")
            else:
                await interaction.response.send_message(f"The endpoint returned status code: {response.status_code}. Endpoint may be offline.")
        except requests.exceptions.RequestException as e:
            await interaction.response.send_message(f"The endpoint {models[option.value]["url"]} is offline or there was an error: {e}")

@bot.tree.command(name="persona", description="add a persona")
@discord.app_commands.choices(option=[
    discord.app_commands.Choice(name="Add", value=0),
    discord.app_commands.Choice(name="Remove", value=1),
    discord.app_commands.Choice(name="Modify", value=2),
    discord.app_commands.Choice(name="Show All", value=3)
])
@discord.app_commands.describe(option="Operation", name="Name of persona", profilepicture="Imgur link of Persona (please add .png/.jpg)", personality="Pastebin link for personality", new_name="For modifying persona name, optional")
async def persona(interaction: discord.Interaction, option: discord.app_commands.Choice[int], name: Optional[str], profilepicture: Optional[str], personality: Optional[str], new_name: Optional[str]):
    personaHandler = PersonalityManager(interaction.guild.id)
    names = personaHandler.returnPersonas()
    if option.value != 3 and name is None:
        await interaction.response.send_message("Please input the name")
    if option.value == 0: #Add Persona
        if name in names: #Check if it already exists
            await interaction.response.send_message("Name already exist")
        else:
            personaHandler.addPersonality(
                name=name,
                personality=getTxt(personality),
                profile=profilepicture
            )
            if name not in personaHandler.returnPersonas(): #Checks if it is added
                await interaction.response.send_message("Add fail")
            else:
                await interaction.response.send_message(f"Add success, personality {name} with profile picture [link]({profilepicture})")
    elif option.value == 1: #Delete
        if name not in names:
            await interaction.response.send_message("Persona doesn't exist")
        personaHandler.getPersona(name)
        personaHandler.change_data(delete=True)
        if name in personaHandler.returnPersonas(): #Checks if it is added
            await interaction.response.send_message("Remove fail")
        else:
            await interaction.response.send_message(f"Remove success")
    elif option.value == 2: #Modify
        if name not in names:
            await interaction.response.send_message("Persona doesn't exist")
        personaHandler.getPersona(name)
        personaHandler.modifyPersonality(
            name = new_name if new_name else name,
            personality = getTxt(personality) if personality else personaHandler.data.personality,
            profile = profilepicture if profilepicture else personaHandler.data.profilePicture
        )
        personaHandler.change_data()
        read_cache_data()
        logger.info("Data Modification Warning")
        await interaction.response.send_message(f"Modify done")
    else:
        personas = personaHandler.returnPersonas(personaObject=True)
        if personas is None:
            await interaction.response.send_message("This server does not have any custom persona")
        embeds = [(discord.Embed(title=personaObject.name, description=personaObject.personality)) for personaObject in personas]
        for i, embed in enumerate(embeds):
            embed.set_image(url=str(personas[i].profilePicture))
        await interaction.response.send_message(embeds=embeds)
    

@bot.tree.command(name="personasystem", description="Toggle persona for bot for custom characters in this channel")
@discord.app_commands.choices(option=[
    discord.app_commands.Choice(name="Enabled", value=1),
    discord.app_commands.Choice(name="Disabled", value=0)
])
@discord.app_commands.describe(option="Enable or Disable")
async def personasystem(ctx: discord.Interaction, option: discord.app_commands.Choice[int]):
    webhooks = await ctx.channel.webhooks()
    existing_webhook = None
    for webhook in webhooks:
        if webhook.name == "Kuromi webhook":
            existing_webhook = webhook
            break

    if bool(option.value):    
        if existing_webhook is None:
            webhook = await ctx.channel.create_webhook(name="Kuromi webhook")
            logger.info(f'Webhook created! URL: {webhook.url}')
            await ctx.response.send_message("Persona enabled here")
        else:
            await ctx.response.send_message("Persona already enabled here")
    else:
        # Remove the webhook if it exists
        if existing_webhook is None:
            await ctx.response.send_message("Persona already disabled")
        else:
            await existing_webhook.delete()
            # Optionally, remove it from your stored data
            logger.info(f'Webhook removed! URL: {existing_webhook.url}')
            await ctx.response.send_message("Persona disabled")

@bot.tree.command(name="globalchat", description="Enable respondAll behavior in this channel")
@discord.app_commands.choices(option=[
    discord.app_commands.Choice(name="Enabled", value=1),
    discord.app_commands.Choice(name="Disabled", value=0)
])
@discord.app_commands.describe(option="Enable or Disable", contextlength="Length of memory in messages")
async def globalchat(interaction: discord.Interaction, option: discord.app_commands.Choice[int], contextlength:int = 12):
    dataHandler = CacheManager(interaction.guild.id)
    if bool(option.value):
        logger.info(f"Global chat enabling in {interaction.channel.id}: {contextlength} messages")
        if contextlength > int(MAX_CACHE):
            await interaction.response.send_message(f"Exceeded max cache of {MAX_CACHE}")
        elif interaction.channel.id not in dataHandler.globalChatTask:
            dataHandler.globalChatTask[interaction.channel.id] = contextlength #appends channel id to dict with contextlength
            dataHandler.updateGlobalChatTask() #convert back to strlist. <- obsolete, str endecoder embedded in manager class now.
            logger.info(f"Operation Finished")
        else:
            logger.info("Global chat already active")
    else:
        logger.info(f"Global chat disabling in {interaction.channel.id}")
        if interaction.channel.id in dataHandler.globalChatTask:
            dataHandler.globalChatTask.pop(interaction.channel.id)
            dataHandler.updateGlobalChatTask()
            logger.info(f"Success")
        else:
            logger.info("Global chat already disabled")
    
    await interaction.response.send_message(f"Global chat {'enabled' if option.value else 'disabled'} in this channel{f' with {contextlength} messages context.' if option.value else ''}")

@bot.tree.command(name="send", description="Trigger the bot to send a message")
@discord.app_commands.describe(name="Persona Name")
async def sendpersona(interaction: discord.Interaction, name: str):
    webhooks = await interaction.channel.webhooks()
    existing_webhook = None
    for webhook in webhooks:
        if webhook.name == "Kuromi webhook":
            existing_webhook = webhook
            break

    if existing_webhook is None:
        await interaction.response.send_message("Persona disabled")
    logger.info("Send persona command sent")
    personaHandler = PersonalityManager(interaction.guild.id)
    names = personaHandler.returnPersonas()
    if name not in names:
        await interaction.response.send_message("Persona doesn't exist")
    else:
        await interaction.response.send_message("...")
        await chatWithAI(interaction, name)


@bot.event
async def on_message(ctx:discord.Message):

    logger.info(f"Message detected from: {ctx.author.display_name}")
    reference: discord.Message = await ctx.channel.fetch_message(ctx.reference.message_id) if ctx.reference is not None else None
    webhookDetect = reference.webhook_id if reference and reference.webhook_id else None
    kuromiPing = reference.author if reference and reference.author is bot.user else None
    if webhookDetect:
        logger.info(f"webhook reference {webhookDetect}")
    if kuromiPing:
        logger.info(f"Main bot reference {kuromiPing}")

    if ctx.author.id == ctx.guild.me.id or ctx.webhook_id is not None:
        return
    if not webhookDetect and not kuromiPing and bot.user not in ctx.mentions:
        return 
    
    
    dataHandler = CacheManager(ctx.guild.id) #create object to handle db interaction
    logger.info(dataHandler.globalChatTask)
    if ctx.channel.id not in dataHandler.globalChatTask:
        return
    
    if ctx.attachments:
        # Find the first image attachment
        image_attachment = next((att for att in ctx.attachments if att.content_type and "image" in att.content_type), None)
        
        if image_attachment:
            # Call the openaiDescribe function to get the image description
            image_description = await openaiDescribe(ctx, image_attachment.url)
            
            # Prepend the image description in parentheses to the message content
            ctx.content = f"({image_description}) {ctx.content}"

    channelContextLength = int(dataHandler.globalChatTask[ctx.channel.id])
    logger.info(f"Continuing conversation with user: {ctx.author.display_name} (ID: {ctx.author.id}) at at {channelContextLength} context")

    await chatWithAI(ctx, cache=int(channelContextLength)) if not webhookDetect else await chatWithAI(ctx, name=reference.author.display_name, cache=int(channelContextLength))




bot.run(TOKEN)