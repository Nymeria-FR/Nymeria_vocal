import discord

from config import config
from voice import voic_event_traitment, voice_commande

client = discord.Client()


@client.event
async def on_message(message):
    if message.author.id != client.user.id:
        if message.content.startswith("n!voice"):
            reponse = await voice_commande(message)
            await message.channel.send(reponse)


@client.event
async def on_voice_state_update(member, before, after):
    await voic_event_traitment(member, before, after, client)


@client.event
async def on_ready():
    print("Logged as {}!".format(client.user))

client.run(config.token)
