from together import Together
from together import error
import requests
import discord
import asyncio
from io import BytesIO
from init import IMGGEN

async def generateImage(prompt: str) -> discord.File:

    client = Together(api_key="c1d2906e5b7e4cf216f64952a44088d561c8150f1d9b7b2d7e64a7a177edd37b")
    try:
        response = client.images.generate(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell-Free",
            steps=10,
            n=1,
            disable_safety_checker=True,
        )
    except error:
        return error
    
    print("image sec")
    res = requests.get(response.data[0].url)
    fileObj = BytesIO(res.content)
    return discord.File(fp=fileObj, filename="image.jpg")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generateImage("computer"))

