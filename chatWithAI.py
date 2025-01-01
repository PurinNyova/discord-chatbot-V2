import discord
from init import logger, MAX_CACHE
import json
from classes import PersonalityManager, CacheManager
from collections import deque
from functions import send_webhook, send_large_message, load_model, imageDescriptionCache
from typing import Union
import openai


async def chatWithAI(ctx: Union[discord.Message, discord.Interaction], name: str=None, cache=int(MAX_CACHE)):

    if name:
        logger.info(f"Name: {name}")
    #Create Personality object and load it with the intended persona
    personaHandler = PersonalityManager(ctx.guild.id)
    personaHandler.getPersona(name)
    if name is None:
        with open('personality.txt', 'r', encoding='utf-8') as file:
            sys_msg = file.read() #loads personality data
    else:
        sys_msg = personaHandler.data.personality

    #loads model info from database and set up OpenAI
    dataHandler = CacheManager(ctx.guild.id)
    models = load_model()
    openai_model = models[dataHandler.data.activeModel]["model_name"]
    client = openai.AsyncOpenAI(api_key=models[dataHandler.data.activeModel]["api_key"],base_url=models[dataHandler.data.activeModel]["url"])

    #webhook checking
    webhooks = await ctx.channel.webhooks()
    webhook = next((wh for wh in webhooks if wh.name == "Kuromi webhook"), None)

    #Grabs recent messages
    user_message_cache = deque(maxlen=cache)
    async for messagex in ctx.channel.history(limit=cache, oldest_first=False): #3/10/2024 limit of 20 is placeholder, change later. 20/12/2024: Finally changed
        logger.info(f"{messagex.author.display_name} {messagex.author.id} {webhook.id if webhook else None} target:{name}")
        logger.info(f"author id is webhook? {messagex.author.id == (webhook.id if webhook else None)}")
        logger.info(f"author name is webhook? {messagex.author.display_name == name}")

        for user in messagex.mentions:
            messagex.content = messagex.content.replace(f'<@{user.id}>', f"@{user.name}")
            messagex.content = messagex.content.replace(f'<@!{user.id}>', f"@{user.name}")

        # Replace role mentions
        for role in messagex.role_mentions:
            messagex.content = messagex.content.replace(f'<@&{role.id}>', f"@{role.name}")

        # Replace channel mentions
        for channel in messagex.channel_mentions:
            messagex.content = messagex.content.replace(f'<#{channel.id}>', f"@{channel.name}")

        #Grabs the message history, differentiates depending if it's a webhook or the bot itself
        if name and messagex.author.id == webhook.id and messagex.author.display_name == name:
                logger.info(f"webhook detect")
                user_message_cache.appendleft(("assistant", messagex.content))
        elif not name and messagex.author.id == ctx.guild.me.id:
                logger.info(f"mainbot detect")
                user_message_cache.appendleft(("assistant", messagex.content))
        else:
            if ctx.channel.id in imageDescriptionCache and messagex.id in imageDescriptionCache[ctx.channel.id]:
                user_message_cache.appendleft(("user", f"({messagex.author.display_name}): {imageDescriptionCache[ctx.channel.id][messagex.id]} {messagex.content}"))
            else:
                user_message_cache.appendleft(("user", f"({messagex.author.display_name}): {messagex.content}"))
    logger.info(f"Cached the last {MAX_CACHE} messages from the channel.")

    async with ctx.channel.typing():
        #build JSON response
        content = [
            {"role": "system", "content": "There are multiple users. Do not mistake one another. Do not speak on behalf of users. Keep it realistic and conversational. Keep your responses short don't make long paragraphs"},
            {"role": "system", "content": "If you don't see yourself in message history simply jump in the conversation naturally"},
            {"role": "system", "content":sys_msg}
        ]
        if isinstance(ctx, discord.Message) and ctx.attachments:
            content.append({"role": "system", "content": ctx.content})

        for role, msg_content in user_message_cache:
            content.append({"role": role, "content": msg_content})
        
        if content[-1]["role"] == "assistant":
            content.append({"role": "user", "content": "."})

        #logs the built JSON    
        logger.info(f"Attempt openai with {client.base_url} {openai_model}")
        logger.info(json.dumps(content, indent=4))
        logger.info(dataHandler.data)

        try:
            stream = await client.chat.completions.create(
                model=openai_model,
                messages=content,
                stream=True,
                max_tokens=1000,
                temperature=1
            )
            full_res = ""
            
            #async def stream_wrapper(sync_iterable):
            #    for item in sync_iterable:
            #        yield item
            
            async for chunk in stream: 
                chunk_message = chunk.choices[0].delta.content
                if chunk_message:
                    full_res += chunk_message
            await send_large_message(ctx, full_res) if name is None else await send_webhook(ctx, full_res, name)

        except openai.AuthenticationError as e:
            await send_large_message(ctx, f"Authentication error occurred: {str(e)}")
        except openai.RateLimitError as e:
            await send_large_message(ctx, f"Rate limiter error occurred: {str(e)}")
        except openai.APIConnectionError as e:
            await send_large_message(ctx, f"OpenAI Connection Error occurred: {str(e)}")
        except openai.BadRequestError as e:
            await send_large_message(ctx, f"Bad Request error occurred: {str(e)}")
        except Exception as e:
        # Optional: Catch any other exceptions
            send_large_message(ctx, f"An unexpected error occurred: {e}")

async def openaiDescribe(ctx: discord.Message, image_url: str) -> str:
    models = load_model()
    openai_model = models["2"]["model_name"]
    client = openai.AsyncOpenAI(api_key=models["2"]["api_key"],base_url=models["2"]["url"])

    async with ctx.channel.typing():
        response = await client.chat.completions.create(
        model=openai_model,
        messages=[
            {
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image? In detail"},
                {
                "type": "image_url",
                "image_url": {
                    "url": f"{image_url}",
                },
                },
            ],
            }
        ],
        max_tokens=300,
        stream=True,
        )
        full_res = ""
        async for chunk in response: 
                chunk_message = chunk.choices[0].delta.content
                if chunk_message:
                    full_res += chunk_message
        return full_res