import discord

def is_owner(user):
	return user.id == '142173740296306688'


async def has_perms(bot, msg, perms):
	warnings = []
	userPerms = msg.author.permissions_in(msg.channel)
	botPerms = msg.server.me.permissions_in(msg.channel)
	for perm in perms:
		if not getattr(userPerms, perm):
			warnings.append("User doesn't have the `" + perm + "` permission")
		if not getattr(botPerms, perm):
			warnings.append("Bot doesn't have the `"  + perm + "` permission")
	if len(warnings) != 0:
		await bot.say("\n".join(warnings))
		return False
	else:
		return True

async def is_online(bot, user):
	if user.status != discord.Status.online:
		await bot.say("Member has to be online")
		return False
	return True
