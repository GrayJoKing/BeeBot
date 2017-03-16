import discord
from discord.ext import commands
import random
import secrets
import checks

import json
import requests

class Fun():
	def __init__(self, bot):
		self.bot = bot

	#Slap
	@commands.command(pass_context = True)
	async def slap(self, ctx, user:discord.User=None):
		'''slap <user>
- Slaps a user'''
		if user == None:
			await self.bot.say("Specify a user to slap!")
			return
		#:P
		if checks.is_owner(user) or user == self.bot.user:
			user = ctx.message.author
		await self.bot.say(":wave::weary::sparkles: " + user.mention)

	#vote
	@commands.command(pass_context = True)
	async def vote(self, ctx, user:discord.User = None):
		'''vote [<user>]
- Puts \U0001F44Ds and \U0001F44Es on the previous message, or on the last message by the specified user, allowing people to vote on it'''
		async for message in self.bot.logs_from(ctx.message.channel, limit=100, before=ctx.message):
			if user==None or user == message.author:
				await self.bot.add_reaction(message, "\U0001F44D")
				await self.bot.add_reaction(message, "\U0001F44E")
				return

	##LIKE
	##Thumbs up
	@commands.command(pass_context = True)
	async def like(self, ctx, user:discord.User=None):
		'''like [<user>]
- \U0001F44Ds the previous message (or the last message by a specified user)'''
		async for message in self.bot.logs_from(ctx.message.channel, limit=100, before=ctx.message):
			if user==None or user == message.author:
				await self.bot.add_reaction(message, "\U0001F44D")
				return
	##DISLIKE
	##Thumbs up
	@commands.command(pass_context = True, aliases = ['hate'])
	async def dislike(self, ctx, user:discord.User = None):
		'''dislike [<user>]
- \U0001F44Es the previous message (or the last message by a specified user)'''
		async for message in self.bot.logs_from(ctx.message.channel, limit=100, before=ctx.message):
			if user==None or user == message.author:
				await self.bot.add_reaction(message, "\U0001F44E")
				return
	##Yes
	##No
	@commands.command(pass_context = True)
	async def yes(self, ctx):
		'''yes
- No'''
		await self.bot.say("No")
		await self.bot.delete_message(ctx.message)

	##No
	##Yes
	@commands.command(pass_context = True)
	async def no(self, ctx):
		'''no
- Yes'''
		await self.bot.say("Yes")
		await self.bot.delete_message(ctx.message)

	##Say
	@commands.command(pass_context = True, )
	async def say(self, ctx, phrase):
		'''say <phrase>
- Repeats your message'''
		await self.bot.say(":speech_balloon: `" + secrets.clean(phrase) + "`")

	##Reverse
	@commands.command(aliases = ['esrever'], pass_context = True)
	async def reverse(self, ctx, *, msg):
		'''reverse <message>
- Reverses your message'''
		await self.bot.say(":arrows_counterclockwise: `" + ctx.message.clean_content[ctx.message.clean_content.index(" ")+1:][::-1] + "`")

	#Urban
	@commands.command()
	async def urban(self, *search):
		'''urban <term>
	- Defines a term using Urban Dictionary'''
		msg = await self.bot.say("Getting definition...")
		response = requests.get("https://mashape-community-urban-dictionary.p.mashape.com/define?term=" + "%20".join(search),
			headers={
				"X-Mashape-Key": secrets.mashapeKey,
				"Accept": "text/plain"})
		js = json.loads(response.text)
		if len(js['list']) == 0:
			await self.bot.edit_message(msg, "No entries found for `" + " ".join(search) + "`")
			return
		entry = random.choice(js['list'])

		embed = discord.Embed(title = entry['word'], url = entry['permalink'], description = entry['definition'], author = entry['author'])
		embed.add_field(name="Example:", value=entry['example'], inline = False)
		embed.add_field(name="Author:", value=entry['author'], inline = False)
		embed.add_field(name=str(entry['thumbs_up'])+"\U0001F44D", value=secrets.invisibleSpace)
		embed.add_field(name=str(entry['thumbs_down'])+"\U0001F44E", value=secrets.invisibleSpace)

		await self.bot.edit_message(msg,new_content=" ",embed=embed)

def setup(bot):
	bot.add_cog(Fun(bot))
