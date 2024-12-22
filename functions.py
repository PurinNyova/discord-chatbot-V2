from init import logger
import discord
import json
from classes import PersonalityManager
from typing import Union
import requests

def load_model() -> dict:
    with open('models.json') as jsonFile:
        models = json.load(jsonFile)    
    return models

async def send_webhook(ctx: Union[discord.Message, discord.Interaction], full_res: str, name:str) -> None:
    personaHandler = PersonalityManager(ctx.guild.id)
    personaHandler.getPersona(name)
    
    webhooks = await ctx.channel.webhooks()
    webhook = next((wh for wh in webhooks if wh.name == "Kuromi webhook"), None)
    if not webhook:
        logger.info("Webhook disabled")
        return
    webhook_url = webhook.url
    
    # Customizing the webhook's username and avatar
    custom_username = personaHandler.data.name
    custom_avatar_url = personaHandler.data.profilePicture

    # Construct the payload for the webhook
    payload = {
        "content": full_res,
        "username": custom_username,
        "avatar_url": custom_avatar_url
    }

    # Send the POST request using the requests library
    response = requests.post(webhook_url, json=payload)

    # Check for errors
    if response.status_code == 204:
        logger.info("Message sent successfully.")
    else:
        logger.info(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")

def split_message(content, limit=2000) -> list:
    """Split a message into chunks of a specified limit."""
    return [content[i:i+limit] for i in range(0, len(content), limit)]

async def send_large_message(message: discord.Message, content):
    """Send content which may be longer than the discord character limit by splitting it into parts."""
    for chunk in split_message(content):
        await message.reply(chunk)

def getTxt(url: str) -> str:
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.text  # Return the content as a string
        else:
            raise Exception(f"Failed to retrieve the file. Status code: {response.status_code}")
    
    except Exception as e:
        # Handle exceptions (e.g., network issues, invalid URL)
        return str(e)