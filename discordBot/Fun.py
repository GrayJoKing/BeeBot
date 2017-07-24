import discord
from discord.ext import commands
import random
import secrets
import checks

import requests

#xkcd
import json
import aiohttp
import math

class Fun():
	def __init__(self, bot):
		self.bot = bot


	@commands.command()
	async def xkcd(self, num = None):
		'''xkcd [<number>]
- Gets a random xkcd comic
- If a number is given, that comic is shown'''
		msg = await self.bot.say("Getting xkcd comic!")
		async with aiohttp.get('http://xkcd.com/info.0.json') as r:
			if r.status == 200:
				js = await r.json()
				max = js['num']
			else:
				await self.bot.edit_message(msg, new_content="Error while getting comic.")

		if not num:
			xkcd = math.ceil(random()*max)
		elif num.isnumeric():
			xkcd = int(num)
			if xkcd > max:
				await self.bot.edit_message(msg, "Error: Comic not found")
				return
		else:
			await self.bot.edit_message(msg, "Error: Not a number. (Relevant xkcd maybe coming soon)")
			return

		async with aiohttp.get('https://xkcd.com/{0}/info.0.json'.format(xkcd)) as r:
			if r.status == 200:
				js = await r.json()
				embed = discord.Embed(colour=discord.Colour.gold(), title = js['safe_title'] + " #"+str(xkcd), url = js['img'])
				embed.set_image(url = js['img'])
				embed.add_field(name = 'Date', value = "/".join([js['day'],js['month'],js['year']]), inline = False)
				embed.add_field(name = 'Explanation', value = "http://www.explainxkcd.com/wiki/index.php/" + str(xkcd), inline = False)
				#embed.add_field(name = 'Alt-Text', value = js['alt'])
				embed.set_footer(text = js['alt'])
				await self.bot.edit_message(msg, new_content=" ",embed = embed)
			else:
				await self.bot.edit_message(msg, new_content="Error while getting comic.")

	@commands.command(pass_context = True, aliases = ["ucks","alance","🏦"])
	async def ank(self, ctx, user:discord.User = None):
		'''b.ank [<user>]
Checks how many b.ucks you or someone else has'''
		if not user:
			user = ctx.message.author
			if user.id not in self.bot.money or self.bot.money[user.id] == 0:
				await self.bot.say(str(user) + " has zero b.ucks :( B.orrow some from me?")
			else:
				await self.bot.say(str(user) + " has " + str(self.bot.money[ctx.message.author.id]) + " b.ucks!")
		else:
			if user.id not in self.bot.money or self.bot.money[user.id] == 0:
				await self.bot.say("You have zero b.ucks :( You can b.orrow some from me.")
			else:
				await self.bot.say(str(user) + " has " + str(self.bot.money[user.id]) + " b.ucks!")

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
