import openai
import discord
import asyncio
import base64
from io import BytesIO
from functions import load_model

async def generateImage(prompt: str, model_key: str = "8") -> discord.File:

    models = load_model()
    model = models.get(model_key, models["8"])
    client = openai.AsyncOpenAI(
        api_key=model["api_key"],
        base_url=model["url"]
    )
    
    # Determine modalities based on whether model supports text generation
    is_multimodal = model.get("textgen", False)
    modalities = ["image", "text"] if is_multimodal else ["image"]
    
    try:
        response = await client.chat.completions.create(
            model=model["model_name"],
            messages=[{"role": "user", "content": prompt}],
            extra_body={"modalities": modalities},
        )
    except Exception as e:
        raise RuntimeError(f"Image generation failed: {e}") from e

    print("image sec")

    # Extract image from response - OpenRouter returns images as base64 data URLs
    message = response.choices[0].message
    raw = response.model_dump()
    images = raw["choices"][0]["message"].get("images", [])

    if not images:
        raise RuntimeError("No image was returned by the model")

    image_data_url = images[0]["image_url"]["url"]  # "data:image/png;base64,..."
    # Strip the data URL prefix to get raw base64
    base64_str = image_data_url.split(",", 1)[1]
    image_bytes = base64.b64decode(base64_str)
    fileObj = BytesIO(image_bytes)

    if __name__ == "__main__":
        print("Image generated successfully")
        return
    else:
        return discord.File(fp=fileObj, filename="image.png")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generateImage(input("Prompt: ")))

