import discord
from discord.ext import commands
from random import randint, choice
import secrets
import checks

import requests

#xkcd
import json
import aiohttp
import math

from urllib.parse import quote

class Fun():
	def __init__(self, bot):
		self.bot = bot


	@commands.command()
	async def xkcd(self, ctx, num = None):
		'''xkcd [<number>]
- Gets a random xkcd comic
- If a number is given, that comic is shown'''
		msg = await ctx.send("Getting xkcd comic!")
		async with aiohttp.get('http://xkcd.com/info.0.json') as r:
			if r.status == 200:
				js = await r.json()
				total = js['num']
			else:
				await msg.edit(content="Error while getting comic.")

		if not num:
			xkcd = randint(1,total)
		else:
			try:
				xkcd = int(num)
				if xkcd > total:
					await msg.edit(content = "Error: Comic not found")
					return
			except:
				await msg.edit(content = "Error: Not a number.")
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
				await msg.edit(content=" ", embed = embed)
			else:
				await msg.edit(content="Error while getting comic.")

	@commands.command(aliases = ["ucks","alance","🏦"])
	async def ank(self, ctx, user:discord.User = None):
		'''b.ank [<user>]
Checks how many b.ucks you or someone else has'''
		if user:
			if user.id not in self.bot.money or self.bot.money[user.id] == 0:
				await ctx.send("`{}` has zero b.ucks :( Maybe they can b.orrow some from me?".format(secrets.clean(str(user))))
			else:
				await ctx.send("`{0}` has `{1}` b.ucks!".format(str(user), str(self.bot.money[ctx.message.author.id])))
		else:
			user = ctx.message.author
			if user.id not in self.bot.money or self.bot.money[user.id] == 0:
				await ctx.send("You have zero b.ucks :( You can b.orrow some from me.")
			else:
				await ctx.send("You have `{}` b.ucks!".format(str(self.bot.money[ctx.message.author.id])))

	#Slap
	@commands.command()
	async def slap(self, ctx, user:discord.User=None):
		'''slap <user>
- Slaps a user'''
		if user == None:
			await ctx.send("Specify a user to slap!")
			return
		#:P
		if user.id == secrets.owner or user == self.bot.user:
			user = ctx.message.author
		await ctx.send(":wave::weary::sparkles: " + user.mention)

	#vote
	@commands.command()
	async def vote(self, ctx, user:discord.User = None):
		'''vote [<user>]
- Puts \U0001F44Ds and \U0001F44Es on the previous message, or on the last message by the specified user, allowing people to vote on it'''
		async for message in ctx.message.channel.history(limit=100, before=ctx.message):
			if user==None or user == message.author:
				await message.add_reaction("\U0001F44D")
				await message.add_reaction("\U0001F44E")
				return

	##LIKE
	##Thumbs up
	@commands.command()
	async def like(self, ctx, user:discord.User = None):
		'''like [<user>]
- \U0001F44Ds the previous message (or the last message by a specified user)'''
		async for message in ctx.message.channel.history(limit=100, before=ctx.message):
			if user==None or user == message.author:
				await message.add_reaction("\U0001F44D")
				return
	##DISLIKE
	##Thumbs up
	@commands.command(aliases = ['hate'])
	async def dislike(self, ctx, user:discord.User = None):
		'''dislike [<user>]
- \U0001F44Es the previous message (or the last message by a specified user)'''
		async for message in ctx.message.channel.history(limit=100, before=ctx.message):
			if user==None or user == message.author:
				await message.add_reaction("\U0001F44E")
				return
	##Yes
	##No
	@commands.command(aliases = ["sure", "ok", "okay"])
	async def yes(self, ctx):
		'''yes
- No'''
		await ctx.message.delete()
		await ctx.send("No")

	##No
	##Yes
	@commands.command(aliases = ["nah", "nope"])
	async def no(self, ctx):
		'''no
- Yes'''
		await ctx.message.delete()
		await ctx.send("Yes")

	##Say
	@commands.command()
	async def say(self, ctx, *, phrase):
		'''say <phrase>
- Repeats your message'''
		await ctx.send(":speech_balloon: `{}`".format(secrets.clean(phrase)))

	##Reverse
	@commands.command(aliases = ['esrever'])
	async def reverse(self, ctx, *, msg):
		'''reverse <message>
- Reverses your message'''
		await ctx.send(":arrows_counterclockwise: `{}`".format(secrets.clean(msg[::-1])))

	#Urban
	@commands.command()
	async def urban(self, ctx, *, term):
		'''urban <term>
- Defines a term using Urban Dictionary'''
		msg = await ctx.send("Getting definition...")
		response = requests.get("https://mashape-community-urban-dictionary.p.mashape.com/define?term=" + quote(term),
			headers={
				"X-Mashape-Key": secrets.mashapeKey,
				"Accept": "text/plain"})
		js = json.loads(response.text)
		if len(js['list']) == 0:
			await msg.edit(content = "No entries found for `{}".format(term))
			return
		entry = choice(js['list'])

		embed = discord.Embed(title = entry['word'], url = entry['permalink'], description = entry['definition'], author = entry['author'])
		embed.add_field(name="Example:", value=entry['example'], inline = False)
		embed.add_field(name="Author:", value=entry['author'], inline = False)
		embed.add_field(name=str(entry['thumbs_up'])+"\U0001F44D", value=secrets.invisibleSpace)
		embed.add_field(name=str(entry['thumbs_down'])+"\U0001F44E", value=secrets.invisibleSpace)

		await msg.edit(content=None, embed=embed)


def setup(bot):
	bot.add_cog(Fun(bot))
