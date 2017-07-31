import discord
from discord.ext import commands

import secrets

class Mod():
	def __init__(self, bot):
		self.bot = bot

	##Mod
	##Prune
	##Prunes a number of messages
	@commands.command(aliases = ['purge'])
	@commands.has_permissions(manage_messages=True)
	async def prune(self,ctx, num:int, user:discord.User = None):
		'''prune <num> [<user>]
	- Prunes a number of messages
	- If a user is specified, it will only prune their messages from that group'''
		def check(msg):
			return user == None or user == msg.author

		await ctx.message.channel.purge(limit=num, before=ctx.message, check=check)
		if user == None:
			await ctx.send("`{0}` pruned `{1}` messages!".format(secrets.clean(ctx.message.author.name), num))
		else:
			await ctx.send("`{0}` pruned all of`{1}`'s messages in the last `{2}` messages!".format(ctx.message.author.name, user.name, num))
		await ctx.message.delete()

	##Mod
	##Kick {user} {reason}
	##Kicks user
	@commands.command(pass_context = True)
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, member:discord.Member, *, reason="None"):
		'''kick <user> [<reason>]
	- Kicks a user from the server with an optional reason'''
		await member.kick()
		await ctx.send(secrets.clean("`{0}` kicked `{1}`!\n\nReason: `{2}`".format(ctx.message.author.name, member.name, reason)))

	##Mod
	##Ban {user} {reason}
	##Bans user
	##Syntax untested
	@commands.command(pass_context=True, aliases=["ban"])
	@commands.has_permissions(ban_members=True)
	async def an(self, ctx, member:discord.Member,*, reason="None"):
		'''b.an
- Bans a user with an optional reason'''
		await member.ban()
		await ctx.send(secrets.clean("`{0}` banned `{1}`\n\nReason: {2}".format(ctx.message.author.name, str(member), reason)))

	##Mod
	##Warn {user} {reason}
	##Warns user
	@commands.command(pass_context = True)
	@commands.has_permissions(kick_members=True)
	async def warn(self, ctx, member:discord.Member = None, *, reason ):
		'''b.warn <user> <reason>
- Warns a user for a reason
- Sends them a DM'''
		if not member:
			await ctx.send("Mention a user")
			return
		if member == ctx.message.author:
			await ctx.send("You can't warn yourself!")
			return

		await member.send("You have been warned by `{0}` in the server `{1}`.\nReason: `{2}`. \n\nWarning! This user can kick or ban you!".format(str(ctx.message.author), str(ctx.message.guild), reason))
		await ctx.send(secrets.clean("`{0}` warned `{1}`!\n\n Reason: `{2}`".format(str(ctx.message.author), str(member), reason)))


def setup(bot):
	bot.add_cog(Mod(bot))
