import discord
from discord.ext import commands
import checks

class Mod():
	def __init__(self, bot):
		self.bot = bot

	##Mod
	##Prune
	##Prunes a number of messages
	@commands.command(pass_context = True, aliases = ['purge'])
	async def prune(self,ctx, num:int, user:discord.User = None):
		'''prune <num> [<user>]
	- Prunes a number of messages
	- If a user is specified, it will only prune their messages from that group'''
		if not await checks.has_perms(self.bot, ctx.message, ["manage_messages"]):
			return
		def check(msg):
			return user == None or user == msg.author

		if ctx.message.author.permissions_in(ctx.message.channel).manage_messages:
			await self.bot.purge_from(ctx.message.channel, limit=num, before=ctx.message, check=check)
			if user == None:
				await self.bot.say("`" + ctx.message.author.name + "` pruned `" + str(num) + "` messages!")
			else:
				await self.bot.say("`" + ctx.message.author.name + "` pruned all of`" + user.name+ "`'s messages in the last `" + str(num) + "` messages!")
			await self.bot.delete_message(ctx.message)
		else:
			await self.bot.say("User has insufficient privileges!")

	##Mod
	##Kick {user} {reason}
	##Kicks user
	@commands.command(pass_context = True)
	async def kick(self, ctx, member:discord.Member, reason="None"):
		'''kick <user> [<reason>]
	- Kicks a user from the server with an optional reason'''
		if not await checks.has_perms(self.bot, ctx.message, ["kick_members"]):
			return
		await self.bot.kick(member)
		await self.bot.say(str(ctx.message.author.name) + " kicked `" + str(member) + "`!\nReason: " + " ".join(reason))

	##Mod
	##Ban {user} {reason}
	##Bans user
	##Syntax untested
	@commands.command(pass_context=True)
	async def an(self, ctx, member:discord.Member,*, reason="None"):
		'''b.an
- Bans a user with an optional reason'''
		if not await checks.has_perms(self.bot, ctx.message, ["ban_members"]):
			return
		await self.bot.ban(member)
		await self.bot.say(str(ctx.message.author.name) + " banned `" + str(member) + "`!\nReason: " + reason)

	##Mod
	##Warn {user} {reason}
	##Warns user
	@commands.command(pass_context = True)
	async def warn(self, ctx, member:discord.Member = None, *reason ):
		'''b.warn <user> <reason>
- Warns a user for a reason
- Sends them a DM'''
		if not await checks.has_perms(self.bot, ctx.message, ["kick_members","ban_members"]):
			return

		if not member:
			await self.bot.say("Mention a user")
			return
		if member == ctx.message.author:
			await self.bot.say("You can't warn yourself!")
			return

		await self.bot.send_message(member, "You have been warned by `" + str(ctx.message.author) + "` in the server `" + str(ctx.message.server) + "` for `" + " ".join(reason) + "`\n\nThis user can kick or ban you!")
		await self.bot.say("`" + str(ctx.message.author) + "` warned `" + str(member) + "`!\nReason: `" + " ".join(reason) + "`")


def setup(bot):
	bot.add_cog(Mod(bot))
