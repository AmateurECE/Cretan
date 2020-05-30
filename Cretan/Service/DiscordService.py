###############################################################################
# NAME:             DiscordService.py
#
# AUTHOR:           Ethan D. Twardy <edtwardy@mtu.edu>
#
# DESCRIPTION:      This service uses the Discord API.
#
# CREATED:          05/27/2020
#
# LAST EDITED:      05/30/2020
###

import asyncio
import discord

class DiscordService:
    def __init__(self, token):
        self.client = None
        self.token = token

    async def start(self):
        self.client = discord.Client()
        asyncio.create_task(self.client.start(self.token))
        await self.client.wait_until_ready()

    def getClient(self):
        return self.client

class DiscordStreamHandler:

    def __init__(self, service, guildName, channelName):
        self.channel = None
        ourGuild = None
        for guild in service.getClient().guilds:
            if guild.name == guildName:
                ourGuild = guild
                break
        for channel in ourGuild.channels:
            if channel.name == channelName:
                self.channel = channel
                break

    async def write(self, message):
        await self.channel.send(f'{message["source"]}: {message["message"]}')
        return "+Ok"

###############################################################################
