import discord
import secrets

async def is_online(bot, user):
	if user.status != discord.Status.online:
		await bot.say("Member has to be online")
		return False
	return True
