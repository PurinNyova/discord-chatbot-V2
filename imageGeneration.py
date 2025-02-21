from together import Together
from together import error
import requests
import discord
import asyncio
from io import BytesIO
from init import IMGGEN

async def generateImage(prompt: str) -> discord.File:

    client = Together(api_key=IMGGEN)
    try:
        response = client.images.generate(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell-Free",#"stabilityai/stable-diffusion-xl-base-1.0"
            steps=4,
            n=1,
            disable_safety_checker=True,
        )
    except error:
        return error
    
    print("image sec")
    res = requests.get(response.data[0].url)
    fileObj = BytesIO(res.content)
    if __name__ == "__main__":
        print(response.data[0].url)
        return
    else:
        return discord.File(fp=fileObj, filename="image.jpg")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generateImage(input("Prompt: ")))

