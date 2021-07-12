import json
import discord
from config import config


def load():
    f = open(config.json_data_base, "r")
    data = json.load(f)
    return data


def save(data):
    with open(config.json_data_base, "w") as output:
        json.dump(data, output)


async def voic_event_traitment(member, before, after, client):
    data_channel = load()
    for server, data in config.servers.items():
        guild = server
        if member.guild.id == int(data["id"]):
            break
    if str(member.id) not in data_channel:
        data_channel[str(member.id)] = [member.name + "'s chanel",
                                        0,
                                        None,
                                        guild]
    else:
        data_channel[str(member.id)][3] = guild
    ban_channel = config.servers[data_channel[str(
        member.id)][3]]["channels_bloque"].split(' ')
    if after.channel is not None:
        if after.channel.id == int(config.servers[guild]["channel_creation"]):
            category = member.voice.channel.category
            voiceCreate = await member.guild.create_voice_channel(
                data_channel[str(member.id)][0],
                category=category)
            data_channel[str(member.id)][1] = voiceCreate.id
            data_channel[str(member.id)][3] = guild
            await member.move_to(voiceCreate)
            await voiceCreate.edit(user_limit=data_channel[str(member.id)][2])
            await voiceCreate.set_permissions(member,
                                              connect=True,
                                              read_messages=True,
                                              manage_channels=True)
    if before.channel is not None:
        if (str(before.channel.category.id) == config.servers[data_channel[str(member.id)][3]]["cat"] and
                str(before.channel.id) not in ban_channel):
            await before.channel.delete()
            data_channel[str(member.id)][1] = 0
    save(data_channel)


async def voice_commande(message):
    if message.content == "n!voice lock":
        return await lock(message.author)
    elif message.content == "n!voice unlock":
        return await unlock(message.author)
    elif message.content == "n!voice claim":
        return await claim(message.author)
    commande = message.content.split(" ")
    if len(commande) >= 3:
        if commande[1] == "name":
            return await rename(message.author, commande[2])
        elif commande[1] == "limit":
            return await limit(message.author, int(commande[2]))
        elif commande[1] == "permit" and message.mentions is not None:
            return await permit(message.author, message.mentions)
        elif commande[1] == "reject" and message.mentions is not None:
            return await reject(message.author, message.mentions)
    return "Cette commande n'existe pas"


async def lock(member):
    data = load()
    if (str(member.id) in data and
            data[str(member.id)][1] != 0):
        channel = member.guild.get_channel(data[str(member.id)][1])
        await channel.set_permissions(member.guild.default_role,
                                      connect=False,
                                      read_messages=True)
        return "{}\nLe channel a été bloqué 🔒".format(member.mention)
    return "{}\nTu ne possède pas channel".format(member.mention)


async def unlock(member):
    data = load()
    if (str(member.id) in data and
            data[str(member.id)][1] != 0):
        channel = member.guild.get_channel(data[str(member.id)][1])
        await channel.set_permissions(member.guild.default_role,
                                      connect=True,
                                      read_messages=True)
        return "{}\nLe channel a été débloqué 🔓".format(member.mention)
    return "{}\nTu ne possède pas channel".format(member.mention)


async def rename(member, name):
    data = load()
    if (str(member.id) in data and
            data[str(member.id)][1] != 0):
        channel = member.guild.get_channel(data[str(member.id)][1])
        await channel.edit(name=name)
        data[str(member.id)][0] = name
        save(data)
        return f"{member.mention}\nLe nom du channel a été changé en {name}"
    return f"{member.mention}\nTu ne possèdes pas channel"


async def limit(member, limit):
    data = load()
    if (str(member.id) in data and
            data[str(member.id)][1] != 0):
        channel = member.guild.get_channel(data[str(member.id)][1])
        if limit > 0 and limit < 100:
            data[str(member.id)][2] = limit
        else:
            data[str(member.id)][2] = None
        await channel.edit(user_limit=data[str(member.id)][2])
        save(data)
        return "{}\nLa limit du channel a été fixé par {}".format(
            member.mention,
            limit)
    return "{}\nTu ne possède pas channel".format(member.mention)


async def permit(member, mentions):
    data = load()
    if (str(member.id) in data and
            data[str(member.id)][1] != 0):
        channel = member.guild.get_channel(data[str(member.id)][1])
        reponse = "{}\n\n".format(member.mention)
        for mention in mentions:
            await channel.set_permissions(mention,
                                          connect=True,
                                          read_messages=True)
            reponse += "-> {}\n".format(mention.mention)
        reponse += "Vous pouvez rejoindre le channel {}".format(
            data[str(member.id)][0])
        return reponse
    return "{}\nTu ne possède pas channel".format(member.mention)


async def reject(member, mentions):
    data = load()
    if (str(member.id) in data and
            data[str(member.id)][1] != 0):
        channel = member.guild.get_channel(data[str(member.id)][1])
        reponse = "{}\n\n".format(member.mention)
        for mention in mentions:
            if mention in channel.members:
                await mention.move_to(None)
            await channel.set_permissions(mention,
                                          connect=False,
                                          read_messages=True)
            reponse += "-> {}\n".format(mention.mention)
        reponse += "Vous ne pouvez plus rejoindre le channel {}".format(
            data[str(member.id)][0])
        return reponse
    return "{}\nTu ne possède pas channel".format(member.mention)


async def claim(member):
    data = load()
    chan = member.voice
    ban_channel = config.servers[data[str(
        member.id)][3]]["channels_bloque"].split(' ')
    if chan is not None:
        chan = member.voice.channel
        if (chan.category_id == int(config.servers[data[str(member.id)][3]]["cat"]) and
                not(str(chan.id) in ban_channel)):
            if (str(member.id) in data and data[str(member.id)][1] == chan.id):
                for memberkey in data:
                    if data[memberkey][1] == chan.id:
                        reponse = "{}\nCe channel apartient déjà à quelqu'un".format(
                            member.mention)
                        return reponse
                await chan.set_permissions(member,
                                           connect=True,
                                           read_messages=True,
                                           manage_channels=True)
                data[str(member.id)][1] = chan.id
                save(data)
                reponse = "{}\nTu possèdes maintenant".format(
                    member.mention)
                return reponse + " le channel {}".format(
                    chan.name)
            return "{}\nTu possède déjà le channel".format(member.mention)
        return "{}\nTu n'es pas dans un channel créé par nymeria vocal bot".format(
            member.mention)
    return "{}\nTu n'es connecté a aucun channel".format(member.mention)
