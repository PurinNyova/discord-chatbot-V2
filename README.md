
# PurinNyova's Discord Chatbot V2

A chatbot for roleplaying on your discord servers!

![MIT License](https://img.shields.io/badge/License-Apache_2.0-green.svg)

![Static Badge](https://img.shields.io/badge/Python-3.12-yellow)

![Static Badge](https://img.shields.io/badge/Discord.py-2.4.0-blue)

![Static Badge](https://img.shields.io/badge/OpenAI-1.58.1-white)

![Static Badge](https://img.shields.io/badge/SQLAlchemy-2.0.36-darkgreen)
## Features

- Image Generation
- Direct Messages
- Custom Models
- Simultaneous Multi-Character


## Installation

Install the bot with Python

Clone The repo

```bash
  git clone https://github.com/PurinNyova/discord-chatbot-V2
```

Install via Python
```bash
  cd discord-chatbot-V2
  python -m venv .venv
  python -m pip install -r requirements.txt
```

Running
```bash
  .venv\Scripts\activate
  python bot.py
```
    
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`TOKENA` Your discord bot TOKENA

`GEN` Your image generation token

`DISCORD_CLIENT_IDA` Your discord client ID

`MAX_CACHE` Maximum allowed Contextlength

`VISION` Model number specified for vision (example: 2)

also configure the personality.txt for the default personality


## models.json example

```json
{
    "0": {
        "url": "link"
        "api_key": "string"
        "nodel_name": "gpt-4o-mini"
    },
    "1": {
        "url": "link"
        "api_key": "string"
        "nodel_name": "gpt-4o"
    },
    "2": {
        "url": "link"
        "api_key": "string"
        "nodel_name": "mistral-large-latest"
    }
}
```
## Commands

Create, Delete, Update, or Read available Personas in the Server

```bash
/persona Option[Add, Remove, Modify, Show, Show All]
```
Allows Webhook creation for persona usage
```bash
/personasystem Option[Enabled, Disabled]
```
Whether to allow the bot to chat in the channel where the command is invoked.
Contextlength is an integer that decides how far back it should read the chat in n-messages (not tokens!) and is optional, default 12
```bash
/globalchat Option[Enabled, Disabled] contextlength?[integer]
```
Make the bot send a message using a specific persona or the default if blank
```bash
/send Name?[string]
```
Whether you want the bot to be pinged first to send a message or simply send when the user sends a message
```bash
/requirereply Option[Enabled, Disabled]
```

Create an AI Image using Flux Schnell
```bash
/generate Prompt[string]
```

## Example Screenshot

![App Screenshot](https://i.imgur.com/ssfAr8U.png)

