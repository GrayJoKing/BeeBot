import discord
from discord.ext import commands

#All
import random

#Dice
from math import ceil

#Cat
import json

#Dog and Cat
import aiohttp

#Dog
from re import search

#B.ook + clean function
import secrets

#roll
from functools import reduce

class Random():
	def __init__(self, bot):
		self.bot = bot

	##Roll
	##Rolls dice
	@commands.command(aliases=['die','dice'])
	async def roll(self, *, dice):
		'''roll <number>
- Rolls number of dice
	e.g. b.roll 5
	OR
b.roll [<number1>d<number2>]
- Rolls number1 dice with number2 sides
	e.g. b.roll 5d3 6d4 2d7 ...'''
		if len(dice) == 0:
			await self.bot.say("You rolled a ``" + str(ceil(random.random()*6)) + "`")
			return
		dice = dice.split(" ")

		results = []
		if len(dice) == 1:
			try:
				int(dice[0])
				dice = int(dice[0])
				if dice >= 100:
					await self.bot.say("No more than 100 dice please")
					return
				for i in range(0,dice):
					results.append(str(random.randint(1,6)))
				text = "You rolled `" + str(dice) + "` dice. The results were `" + ", ".join(results) + "`"
				await self.bot.say(text)
				return
			except:
				pass

		counter = 0
		for die in dice:
			die = die.split("d")
			if len(die) != 2:
				await self.bot.say("error when processing "+ secrets.clean('d'.join(die)))
				return
			else:
				if die[0] == '':
					die[0] = '1'
				counter += int(die[0])
				if die[0] == '':
					die[0] = 0
				elif not die[0].isnumeric():
					await self.bot.say("error when processing "+ secrets.clean('d'.join(die)))
					return
				elif int(die[0]) > 100 or counter > 100:
					await self.bot.say("No more than 100 dice please")
					return
				elif int(die[1]) > 100:
					await self.bot.say("Dice with values no more than 100 please")
					return
				tmp = []
				for i in range(0,int(die[0])):
					tmp.append(str(random.randint(1,int(die[1]))))
				results.append("You rolled `" + str(die[0]) + "` dice with `" + str(die[1]) + "` sides. The results were `" + ", ".join(tmp) + "` for a total of `" + str(reduce(lambda x,y: int(x)+int(y), tmp)) + "`")

		await self.bot.say('\n'.join(results))

		results = []

	##Choose {phrase} or {phrase} or ...
	@commands.command(pass_context = True, aliases = ['choice'])
	async def choose(self, ctx, *, words):
		'''choose <choice> {"or" <choice>}
- Replies with a random choice from those given
	e.g. b.choose Option 1 or Option 2 or Option 3'''
		await self.bot.say("`{}`".format(secrets.clean(random.choice(words.split(" or ")))))

	##Flip
	##Flips a coin
	@commands.command(aliases = ['coin'])
	async def flip(self, table = None):
		'''flip
- Flips a coin'''
		if table == "table":
			await self.bot.say("(╯:bee:）╯︵ ┻━┻")
			return
		await self.bot.say(random.choice(["Heads","Tails"]))

	##Scramble
	@commands.command()
	async def scramble(self, *, msg):
		'''scramble <message>
- Scrambles your message'''
		await self.bot.say(":twisted_rightwards_arrows: `" + secrets.clean(random.shuffle(msg)) + "`")

	#Dog
	@commands.command(aliases = ["itch", "ark", "ite"], pass_context = True)
	async def dog(self, ctx):
		'''dog
- Gets a picture of a random \U0001F436'''
		msg = await self.bot.say("Getting a \U0001F436 or two!")
		async with aiohttp.get('http://random.dog/woof.json') as r:
			if r.status == 200:
				js = await r.json()
				embed = discord.Embed()
				embed.set_image(url = js['url'])
				print(js['url'])
				await self.bot.edit_message(msg, new_content=" " if ctx.invoked_with == "dog" else random.choice(["Grrr...", "Woof!", "Bark!"]),embed = embed)
			else:
				await self.bot.edit_message(msg, new_content="Error while getting image.")

	#Cat
	@commands.command()
	async def cat(self):
		'''cat
- Gets a picture of a random \U0001F431'''
		msg = await self.bot.say("Getting a \U0001F431 or two!")
		async with aiohttp.get('http://random.cat/meow') as r:
			if r.status == 200:
				js = await r.json()
				embed = discord.Embed()
				embed.set_image(url = js['file'])
				await self.bot.edit_message(msg, new_content=" ",embed = embed)
			else:
				await self.bot.edit_message(msg, new_content="Error while getting image.")

	@commands.command()
	async def acronym(self, acro):
		'''acronym <letters>
- Returns a random matching the letters given'''
		if not acro.isalpha():
			await self.bot.say("Error: Letters only")
			return
		if len(acro) > 10:
			await self.bot.say("Error: Word too long")
			return
		wordList = []
		for letter in acro.lower():
			word = random.choice(list(filter(lambda word: word[0] == letter and word.capitalize() not in wordList, (self.bot.wordLists['long'] + self.bot.wordLists['medium']))))
			wordList.append(word.capitalize())
		await self.bot.say("The acronym " + ".".join(list(acro.upper())) + " means:\n\n`" + ' '.join(wordList) + "`")


def setup(bot):
	bot.add_cog(Random(bot))
