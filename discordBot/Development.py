import discord
from discord.ext import commands

#TTT, TTTQ
from random import random, choice, shuffle

#image
from googleapiclient.discovery import build
import secrets

#Suggestions
import time

import json
import math
import copy
import secrets
from battleship import *
import checks

#pong, invert
from PIL import Image, ImageDraw, ImageOps, ImageChops, ImageFont, ImageFilter
import asyncio

#invert
import requests
from io import BytesIO

#giveme
import re
import colour
import os

#cah
from html import unescape

##Translate
#from google.cloud import translate

#translate_client = translate.Client()#	googleAPIkey)
#languageList = translate_client.get_languages()

#Borrow, Slots
from functools import reduce
from decimal import Decimal

#go
from go import *

boardWin = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],
[1,4,7],[2,5,8],[0,4,8],[2,4,6]]


def collapse(cyclic,pairs,space, player):
	if type(pairs[space]) == list:
		temp = copy.copy(pairs[space])
		pairs[space] = player
		for j in temp:
			for i in range(0, len(pairs)):
				if j in pairs[i]:
					collapse(cyclic, pairs, i, j)
					i = 0
					while i < len(cyclic):
						if str(space) in cyclic[i]:
							cyclic.pop(i)
						else:
							i += 1


def printBoard(pairs):
	board = copy.deepcopy(pairs)

	pri = ""
	for bigRow in range(0,3):
		for smallRow in range(0,3):
			row = []
			for col in range(0,3):
				if len(board[bigRow*3+col]) > 3:
					row.append(" ".join(board[bigRow*3+col][:3]))
					board[bigRow*3+col] = board[bigRow*3+col][3:]
				else:
					row.append(" ".join(board[bigRow*3+col]) +"  "*(3-len(board[bigRow*3+col])) + " "*(2-len(board[bigRow*3+col])) + " ")
					board[bigRow*3+col] = []
			pri += "|".join(row) + "\n"
		if bigRow != 2:
			pri += "-"*38 + "\n"
	return pri

async def timer(bot, time):
	msg = await bot.say('''TIME LEFT:''' + time)
	startTime = time.time
	second = 0
	while True:
		if (time.time - startTime) > (second + 1)*1000:
			await bot.edit(msg, "TIME LEFT: " + str(time-second))
			second += 1
			if second == time:
				return False


def addSug(ctx, suggestion):
	msg = ' '.join(suggestion)
	doc = open("Suggestions.txt")
	n = doc.read()
	x = n + "\nUSER: " + str(ctx.message.author) + '\nTime: ' + time.strftime("%x") + ' ' + time.strftime("%X") + '\nSuggestion: ' + msg + "\n"
	doc.close()
	doc = open("Suggestions.txt","w")
	doc.write(x)
	doc.close

class Development():
	def __init__(self, bot):
		self.bot = bot
		bot.slotsCheck = []
		with open('money.json','r') as fp:
			bot.money = json.load(fp)
			fp.close()


	@commands.command(pass_context=True)
	async def give(self, ctx, user:discord.User, amount:int):
		'''give <user> <amount>
- Gives a user some money'''

		if ctx.message.author.id in self.bot.money and self.bot.money[ctx.message.author.id] >= amount:
			self.bot.money[ctx.message.author.id] -= amount
			if user.id not in self.bot.money:
				self.bot.money[user.id] = 0

			self.bot.money[user.id] += amount

			await self.bot.say("You gave `{}` bucks to {}".format(amount, secrets.clean(user.display_name)))

			with open('money.json','w') as fp:
				json.dump(self.bot.money, fp)
		else:
			await self.bot.say("You don't have enough money!")



	@commands.command(pass_context=True)
	async def welcome(self, ctx, * , message = ""):
		'''welcome <message>
- Customise the welcome message for new users
- Use {mention} to mention a new member
- {name} to say their name without a ping
- {servername} for the name of the server
- Type nothing to turn off the welcome message'''

		if not await checks.has_perms(self.bot, ctx.message, ["administrator"]):
			return

		self.bot.serverInfo['welcome'] = message
		await self.bot.say("Welome message edited!")

		with open('serverInfo.json','w') as fp:
			json.dump(self.bot.serverInfo, fp)

	@commands.command(pass_context=True, aliases=['goodbye', 'bye'])
	async def ye(self, ctx, * , message = ""):
		'''b.ye <message>
- Customise the goodbye message for users
- {name} to say their name without a ping
- {servername} for the name of the server
- Type nothing to turn off the welcome message'''

		if not await checks.has_perms(self.bot, ctx.message, ["administrator"]):
			return

		self.bot.serverInfo['bye'] = message
		await self.bot.say("Goodbye message edited!")

		with open('serverInfo.json','w') as fp:
			json.dump(self.bot.serverInfo, fp)

	@commands.command(pass_context = True)
	async def spoiler(self, ctx, *, text):
		'''spoiler <text>
- Creates a "Hover to see spoiler text"'''
		await self.bot.delete_message(ctx.message)

		maxWidth = 300
		border = 5

		redImage = Image.new('RGB', (200, 200), (255,255,255))
		d = ImageDraw.Draw(redImage)
		output = [""]

		fnt = ImageFont.truetype("impact.ttf", size = 20)

		text = text.split(" ")

		for word in text:
			w,h =  d.textsize(output[-1] + " " + word, fnt)
			if w < maxWidth:
				output[-1] = output[-1] + " " + word
			else:
				w,h = d.textsize(word, fnt)
				if w > maxWidth:
					output.append("")
					for letter in word:
						w,h = d.textsize(output[-1] + letter + "-", fnt)
						if w > maxWidth:
							output[-1] += "-"
							output.append("")
						output[-1] += letter
				else:
					output.append(word)

		w, h = d.textsize("\n".join(output), fnt)

		img = Image.new('RGB', (maxWidth,h+2*border), (0,0,0))
		d = ImageDraw.Draw(img)
		d.multiline_text((0,border), "\n".join(output), (255,255,255), fnt)

		hover = Image.new('RGB', (2*border+maxWidth,h+3*border), (0,0,0))
		d = ImageDraw.Draw(hover)
		d.multiline_text((border,border), "[Hover for spoiler]", (255,255,255), fnt)

		hover.save("TempFiles/{}.gif".format(ctx.message.id), save_all = True, append_images = [img], duration = [1, 100000])
		await self.bot.send_file(ctx.message.channel, "TempFiles/{}.gif".format(ctx.message.id))
		os.remove("TempFiles/{}.gif".format(ctx.message.id))

	@commands.command(pass_context = True)
	async def cah(self, ctx):
		'''cah
- Cards Against Humanity!
- 4-10 players, appropriate for ages 1(8) and up!
- Thanks to https://www.crhallberg.com/cah/json/ for providing the CAH json'''

		messageReaction = choice([("Put your 🖐 up if you want to play!", "🖐"), ("🍆s out if you want to play!", "🍆"), ("Touch my 🍆 to play!", "🍆"), ("Push the 🔴 to play!", "🔴")])
		msg = await self.bot.say("{} When everyone is in, the host should press the ✅!".format(messageReaction[0]))
		await self.bot.add_reaction(msg, messageReaction[1])
		await self.bot.add_reaction(msg, "✅")

		while True:
			users = []
			react = (await self.bot.wait_for_reaction(emoji="✅", user=ctx.message.author, message=msg)).reaction
			await self.bot.remove_reaction(msg, "✅", ctx.message.author)
			react.emoji = messageReaction[1]
			users = await self.bot.get_reaction_users(react)
			if ctx.message.author not in users:
				users.append(ctx.message.author)

			for user in users:
				if user.bot:
					users.remove(user)
			if len(users) < 2:
				await self.bot.say("You don't have enough players. You need at least 4 to play.")
			elif len(users) > 10:
				await self.bot.say("You have too many players. You have to have 10 or less.")
			else:
				usernames = list(map(lambda user: user.display_name.replace("`", ""), users))
				checkMsg = await self.bot.say("```Players:\n"+"\n".join(usernames) + " ```Is this right?")
				await self.bot.add_reaction(checkMsg, "❌")
				await self.bot.add_reaction(checkMsg, "✅")
				if (await self.bot.wait_for_reaction(emoji=["✅", "❌"], user=ctx.message.author, message=checkMsg)).reaction.emoji == "✅":
					break
				await self.bot.delete_message(checkMsg)

		await self.bot.delete_message(msg)

		await self.bot.say("Welcome players, to Cards Against Humanity. We're shuffling the deck and 10 white cards will shortly be DM'd to you!")

		with open("gameData/cah.json") as fp:
			deck = json.load(fp)
			fp.close()

		deck['whiteDiscard'] = []
		deck['blackDiscard'] = []

		shuffle(users)
		czar = 0
		for i in range(len(users)):
			info = {}
			info['user'] = users[i]
			info['points'] = 0
			info['cards'] = []
			info['picked'] = []
			for x in range(10):
				card = choice(deck['whiteCards'])
				deck['whiteCards'].remove(card)
				info['cards'].append(card)

			users[i] = info

		numbers = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]

		await asyncio.sleep(1)

		for info in users:
			info['cardMsg'] = await self.bot.send_message(info['user'], "Here are your cards:\n{}".format("\n".join(list(map(lambda card: numbers[info['cards'].index(card)] + " `{}`".format(unescape(card)), info['cards'])))))

		while True:
			if len(deck['blackCards']) == 0:
				deck['blackCards'] = deck['blackDiscard']
				deck['blackDiscard'] = []
			blackCard = choice(deck['blackCards'])
			deck['blackDiscard'].append(blackCard)
			deck['blackCards'].remove(blackCard)

			users[czar]['picked'] = ["Card Czar"]
			users[czar]['picked'].extend([""]*(blackCard['pick']-1))
			await self.bot.say("{0}, you are the Card Czar this round! The black card is:\n\n```{1} Pick ({2})```\n".format(users[czar]['user'].mention, blackCard['text'], blackCard['pick']))

			for info in users:
				await self.bot.edit_message(info['cardMsg'], "The Black Card for this round is ```{0} Pick ({1})```\n\nHere are your cards:\n{2}".format(blackCard['text'], blackCard['pick'], "\n".join(list(map(lambda card: numbers[info['cards'].index(card)] + " `{}`".format(unescape(card)), info['cards'])))))

			msg = await self.bot.say("While the voting sets up, have a look at your cards and decide what you want to play. Remember, no backsies!")

			for emoji in numbers:
				await self.bot.add_reaction(msg, emoji)

			while True:
				usersLeft = list(filter(lambda info: len(info['picked']) != blackCard['pick'], users))
				text = "```\n{} player(s) left to submit:\n".format(len(usersLeft))

				for info in list(filter(lambda info: len(info['picked']) != 0 and info['picked'][0] != "Card Czar", users)):
					text += "\n" + " ".join(map(lambda index: str(index+1), info['picked'])) + " - " + info['user'].display_name

				text += "\n\nIt might not see your guess, so make sure your name appears on the list.```"

				await self.bot.edit_message(msg, text)

				usersToPick = list(map(lambda info: info['user'], usersLeft))
				def check(reaction, user):
					return user in usersToPick and numbers.index(reaction.emoji) not in usersLeft[usersToPick.index(user)]['picked']
				userReaction = await self.bot.wait_for_reaction(emoji=numbers, check = check, message=msg)

				usersLeft[usersToPick.index(userReaction.user)]['picked'].append(numbers.index(userReaction.reaction.emoji))

				if len(list(filter(lambda info: len(info['picked']) != blackCard['pick'], users))) == 0:
					break

			await self.bot.delete_message(msg)

			answers = []
			for info in users:
				if info['picked'][0] != 'Card Czar':
					answers.append(info)

			shuffle(answers)

			msg = await self.bot.say("Here are the white cards for the prompt:\n```{0}```\n{1}".format(
			blackCard['text'],
			"\n".join((numbers[i] + " " + " and ".join(list(map(lambda index: "`{}`".format(unescape(answers[i]['cards'][index])), answers[i]['picked'])))) for i in range(len(answers)))
			))

			msg = await self.bot.say("```Okay Card Czar, have a deep think about which one is the best. Or the most disgusting.```")

			for i in range(len(answers)):
				await self.bot.add_reaction(msg, numbers[i])

			userReaction = await self.bot.wait_for_reaction(message=msg, emoji = numbers[:len(answers)], user = users[czar]['user'])

			winner = numbers.index(userReaction.reaction.emoji)

			await self.bot.say("You chose \n\n{0}\n\n which was played by {1}. Congrats on the point!".format(" and ".join(list(map(lambda index: "`{}`".format(unescape(answers[winner]['cards'][index])), answers[winner]['picked']))), answers[winner]['user'].display_name))

			answers[winner]['points'] += 1

			await self.bot.say("```\nScoreboard:\n{}```".format("\n".join(list(map(lambda info: info['user'].display_name + " - "+ str(info['points']), sorted(users, key = lambda info: info['points'], reverse=True))))))

			if answers[winner]['points'] == 5:
				await self.bot.say("We have a winner! Congratulations {}".format(answers[winner]['user'].display_name))
				break
			else:
				await asyncio.sleep(1)
				czar = (czar + 1)%len(users)

				await self.bot.say("New round! Don't forget to check out your new card.")

				for info in users:
					if info['picked'][0] != "Card Czar":
						for index in info['picked']:
							deck['whiteDiscard'].append(info['cards'][index])
							if len(deck['whiteCards']) == 0:
								deck['whiteCards'] = deck['whiteDiscard']
								deck['whiteDiscard'] = []
							card = choice(deck['whiteCards'])
							deck['whiteCards'].remove(card)
							info['cards'][index] = card
					info['picked'] = []

	@commands.group(pass_context = True)
	async def giveme(self, ctx):
		'''giveme (<name>)|('remove' <name>))|('list')|('create' <name> <colour>)|('delete' <name>)
- A custom role colour generator!
- b.giveme 'role'
	- Gives you that role (if it is a giveme type role, so no trying to give yourself mod roles)
- b.giveme remove 'name'
	- Removes the role 'name' from you
- b.giveme list
	- Shows you a list of roles available for give me
- b.giveme create 'name' 'colour'
	- Creates a role called 'name' and in that colour
	- Needs manage_messages permission
	- Colour can be in form:
		- "red", "green", and other common colours
		- rgb format with spaces in-between
		- Hex format like #FF00FF
- b.giveme edit 'name' 'colour'
	- Changes the colour of a role'''

		if ctx.invoked_subcommand is None:
			name = ctx.message.clean_content[len(ctx.prefix+ctx.invoked_with):].strip().lower()

			if 'giveme' not in self.bot.serverInfo[ctx.message.server.id] or not len(self.bot.serverInfo[ctx.message.server.id]['giveme']):
				await self.bot.say("There are no giveme roles in your server. Ask a mod to create some using `b.giveme create <name> <colour>`")
				return

			if name in self.bot.serverInfo[ctx.message.server.id]['giveme']:
				getRole = None
				for role in ctx.message.server.roles:
					if role.id == self.bot.serverInfo[ctx.message.server.id]['giveme'][name]['id']:
						getRole = role

				if getRole:
					await self.bot.add_roles(ctx.message.author, getRole)
					await self.bot.say("Added role!")
					return
				del self.bot.serverInfo[ctx.message.server.id]['giveme'][name]
			await self.bot.say("There is no giveme role called `{}`.".format(secrets.clean(name)))

	@giveme.command(pass_context = True)
	async def create(self, ctx, name = None, *, col = None):
		if not await checks.has_perms(self.bot, ctx.message, ["manage_roles"]):
			return

		if not name or not col:
			await self.bot.say("Use format `b.create <name> <colour>`")
			return

		if 'giveme' not in self.bot.serverInfo[ctx.message.server.id]:
			self.bot.serverInfo[ctx.message.server.id]['giveme'] = {}

		if name.lower() in self.bot.serverInfo[ctx.message.server.id]['giveme']:
			await self.bot.say("There is already a role of that name.")
			return

		hexFormat = re.compile("#?[0-9A-Fa-f]{6}")
		rgbFormat = re.compile("\\d{1,3} \\d{1,3} \\d{1,3}")
		if hexFormat.match(col) is not None:
			if col[0] != "#":
				col = "#" + col
			col = colour.Color(col)
		elif rgbFormat.match(col) is not None:
			col = tuple(map(lambda x: int(x), col.split(" ")))
			col = colour.Color(rgb=col)
		else:
			try:
				col = colour.Color(col)
			except:
				await self.bot.say("`{}` is not a recognised colour".format(secrets.clean(col)))
				return

		newRole = await self.bot.create_role(server=ctx.message.server, name=name, permissions = discord.Permissions(), colour = discord.Colour(int(col.hex_l[1:],16)), hoist = False, mentionable = False)
		await self.bot.say("Created role!")
		self.bot.serverInfo[ctx.message.server.id]['giveme'][name.lower()] = {'id':newRole.id, 'name':name, 'colour':"%s"%col}
		with open('serverInfo.json','w') as fp:
			json.dump(self.bot.serverInfo, fp)

	@giveme.command(pass_context = True)
	async def edit(self, ctx, name = None, *, col = None):
		if not await checks.has_perms(self.bot, ctx.message, ["manage_roles"]):
			return

		if not name or not col:
			await self.bot.say("Use format `b.edit <name> <colour>`")
			return
		name = name.lower()
		if 'giveme' not in self.bot.serverInfo[ctx.message.server.id]['giveme'] or len(self.bot.serverInfo[ctx.message.server.id]['giveme']) == 0:
			await self.bot.say("There are no giveme roles in your server. Try using `b.giveme create <name> <colour>`")
			return

		getRole = None
		for role in ctx.message.server.roles:
			if role.id == self.bot.serverInfo[ctx.message.server.id]['giveme'][name]['id']:
				getRole = role
		if not getRole:
			await self.bot.say("There is no giveme role called {} in your server.".format(name))

		hexFormat = re.compile("#?[0-9A-Fa-f]{6}")
		rgbFormat = re.compile("\\d{1,3} \\d{1,3} \\d{1,3}")
		if hexFormat.match(col) is not None:
			if col[0] != "#":
				col = "#" + col
			col = colour.Color(col)
		elif rgbFormat.match(col) is not None:
			col = col.split(" ")
			col = tuple(map(lambda x: int(x), col))
			col = colour.Color(rgb=col)
		else:
			try:
				col = colour.Color(col)
			except:
				await self.bot.say("`{}` is not a recognised colour".format(col))
				return

		await self.bot.edit_role(server=ctx.message.server, role=getRole, colour = discord.Colour(int(col.hex_l[1:],16)))
		await self.bot.say("Edited role!")
		self.bot.serverInfo[ctx.message.server.id]['giveme'][name]['colour'] = "%s"%col
		with open('serverInfo.json','w') as fp:
			json.dump(self.bot.serverInfo, fp)


	@giveme.command(name = "list", pass_context = True)
	async def list(self, ctx):
		lis = []

		if 'giveme' in self.bot.serverInfo[ctx.message.server.id] in self.bot.serverInfo and self.bot.serverInfo[ctx.message.server.id]['giveme']:
			for role in self.bot.serverInfo[ctx.message.server.id]['giveme']:
				lis.append(self.bot.serverInfo[ctx.message.server.id]['giveme'][role]['name'] + "\n\t- " + self.bot.serverInfo[ctx.message.server.id]['giveme'][role]['colour'])
			await self.bot.say("```\n{}```".format("\n".join(lis)))
		else:
			await self.bot.say("There are no roles available for `giveme`. Create one using `giveme create 'name' 'colour'`")


	@giveme.command(pass_context = True)
	async def remove(self, ctx, *, name):
		name = name.lower()
		if 'giveme' in self.bot.serverInfo[ctx.message.server.id] and name in self.bot.serverInfo[ctx.message.server.id]['giveme']:
			getRole = None
			for role in ctx.message.server.roles:
				if role.id == self.bot.serverInfo[ctx.message.server.id]['giveme'][name]['id']:
					getRole = role
					del self.bot.serverInfo[ctx.message.server.id]['giveme'][name]
			if getRole:
				if getRole in ctx.message.author.roles:
					await self.bot.remove_roles(ctx.message.author, getRole)
					await self.bot.say("Role removed!")
				else:
					await self.bot.say("You don't have that role.")
				return
		await self.bot.say("There is no role by that name.")

	@giveme.command(pass_context = True)
	async def delete(self, ctx, *, name):
		if not await checks.has_perms(self.bot, ctx.message, ["manage_roles"]):
			return

		if 'giveme' in self.bot.serverInfo[ctx.message.server.id] and name in self.bot.serverInfo[ctx.message.server.id]['giveme']:
			getRole = None
			for role in ctx.message.server.roles:
				if role.id == self.bot.serverInfo[ctx.message.server.id]['giveme'][name]['id']:
					getRole = role
					del self.bot.serverInfo[ctx.message.server.id]['giveme'][name]
			if getRole:
				await self.bot.delete_role(ctx.message.server, getRole)
			await self.bot.say("Role deleted!")
		else:
			await self.bot.say("There is no role by that name.")


	#Translate
	@commands.group(pass_context = True)
	async def translate(self, ctx, *, message = None):
		return
		'''translate [to <language>] Phrase
- Dumb google api'''
		return
		if ctx.invoked_subcommand is None:

			if not message:
				await self.bot.say("Use b.help for info on how to use this")
			else:
				await self.bot.say(self.googleTranslate("English",message))


	@translate.command(name = "to", pass_context = True)
	async def translateto(self,ctx,*message):
		return
		tolanguage = message[0]
		if len(message) == 1:
			phrase = self.bot.wait_for_message(author=ctx.message.author, channel = ctx.message.channel)
		else:
			phrase = " ".join(message[1:])

		await self.bot.say(self.googleTranslate(language, phrase))


	def googleTranslate(self, languageto, phrase):
		mostLikely = None
		likelyRatio = 0
		for language in languageList:
			ratio = similar(languageto, language['name'])
			if ratio > likelyRatio:
				likelyRatio = ratio
				mostLikely = language['language']
				languageName = language['name']
		retur = translate_client.translate(phrase, target_language=mostLikely)
		return retur['detectedsourceLanguage'] + " -> " + languageName + "\n" + retur['translatedText']


	#timeout
	#Mod
	@commands.command(pass_context = True)
	async def timeout(self, ctx, user:discord.User):
		return
		'''timeout <user>
- Strips a user of his roles and sends him to timeout until a moderator either bans him or restores him
- Not working'''
		userRoles = user.roles

		emptyperms = discord.permissions.none()

		##Go through each channel and stop read and post
		##Create timeout channel
		timeoutrole = await self.bot.create_role(user.server, name="In timeout")
		user.replace_roles(timeoutrole)
		##Let every role with ban/kick perms in and the timeout role
		##wait for commands b.an, b.kick, b.end
		##do command


	##Game
	##TTTQ
	@commands.command(pass_context = True)
	async def tttq(self, ctx, user:discord.User = None):
		'''tttq <user>
- Plays a game of quantum tic tac toe'''
		if not user:
			await self.bot.say("Mention a user!")
			return

		if not await checks.is_online(self.bot, challenger):
			return

		host = ctx.message.author
		if host == user:
			await self.bot.say("Did you just challenge yourself?")

		pairs = []
		for i in range(0,9):
			pairs.append([])

		await self.bot.say(challenger.mention + ", " + host.name + " has challenged you to a game of...\n*QUANTUM* TIC TAC TOE!")
		current = choice([host,challenger])
		xo = "O"
		await self.bot.say(current.name + " will go first! Say the pair of numbers you want to put your entangled Xs in! (in format number,number)")

		cyclic = []
		running = True
		turn = 0
		player = "X"
		await self.bot.say("```" + printBoard(pairs) + "```")
		while running:
			turn += 1
			get = True
			while get:
				places = await self.bot.wait_for_message(author = current, channel = ctx.message.channel)
				if places == "quit":
					await self.bot.say("Quitting game")
					return
				places = places.content.split(",")
				if len(places) == 2 and len(places[0]) == 1 and len(places[1]) == 1 and places[0].isdigit() and places[1].isdigit() and type(pairs[int(places[0])]) == list and type(pairs[int(places[1])]) == list:
					pairs[int(places[0])].append(player + str(turn))
					pairs[int(places[1])].append(player + str(turn))
					get = False

			cycle = False
			for i in cyclic:
				if i[-1] == places[0]:
					i.append(places[1])
				elif i[-1] == places[1]:
					i.append(places[0])
				if i[-1] == i[0]:
					cycle = True
					break
			cyclic.append(places)
			cyclic.append(places[::-1])
			await self.bot.say("```" + printBoard(pairs) + "```")
			if current == host:
				current = challenger
			else:
				current = host
			if cycle:
				await self.bot.say("Quantum Cycle detected! Choose which of the " + player + str(turn) + " to collapse, the one in " + places[0] + " or " + places[1] +": ")
				get = True
				while get:
					choose = await self.bot.wait_for_message(author = current, channel = ctx.message.channel)
					choose = choose.content
					if len(choose) == 1 and choose.isdigit() and (choose == places[0] or choose == places[1]):
						get = False
					elif choose == "quit":
						await self.bot.say("Quitting Game")
						return
				collapse(cyclic, pairs, int(choose), player + str(turn))
				await self.bot.say("```" + printBoard(pairs) + "```")
				winList = checkttt(pairs)
				#print(winList)
				if len(winList) != 0:
					await self.bot.say("We have a winner!")

			if player == "O":
				player = "X"
			else:
				player = "O"

	##Game
	##TTT
	@commands.command(pass_context = True)
	async def ttt(self, ctx, challenger:discord.Member = None):
		'''ttt <user>
Plays a game of Tic Tac Toe'''
		if not challenger:
			await self.bot.say("Mention a user!")
			return

		if not await checks.is_online(self.bot, challenger):
			return

		host = ctx.message.author

		if host == challenger:
			await self.bot.say("Did you just challenge yourself?")
			return

		def checkttt(board):
			boardWin = [[1,2,3], [4,5,6], [7,8,9],
						[1,4,7], [2,5,8], [3,6,9],
						[1,5,9], [3,5,7]]
			winList = []
			for win in boardWin:
				if board[win[0]-1][0] == board[win[1]-1][0] and board[win[2]-1][0] == board[win[1]-1][0] and (board[win[0]-1][0] == "X" or board[win[0]-1][0] == "O"):
					return board[win[0]-1][0]
			return

		def getBestMove(board, you):
			if checkttt(board):
				return False, None
			else:
				nums = []
				moveProbs = []
				for i in range(len(board)):
					if i.isdigit():
						probs = getBestMove(board[:].pop(i).insert(i, you))[0]
						moveProbs.append((probs.count(True) > probs.count(False)), "X" if you == "O" else "O")
						nums.append(i)
			return list(map(lambda prob: not prob, moveProbs)), nums


		await self.bot.say("{0}, {1} has challenged you to a game of...\nTIC TAC TOE!".format(challenger.mention, host.name))
		current = choice([host,challenger])
		xo = "O"
		await self.bot.say(current.name + " will go first! Say the number you want to put your X in!")
		running = True
		board = ["1", "2", "3",
				"4", "5", "6",
				"7", "8", "9"]
		counter = 0
		def check(msg):
			return msg.author == host or msg.author == challenger
		while running and counter < 9:
			await self.bot.say("```" + "\n-----\n".join(["|".join(board[0:3]),"|".join(board[3:6]),"|".join(board[6:9])]) + "```")
			get = True
			while get:
				msg = await self.bot.wait_for_message(timeout = 300, channel = ctx.message.channel, check = check)
				if not msg:
					await self.bot.say("Error: Tic Tac Toe game timed out")
				if msg.content.isdigit() and len(msg.content) == 1:
					if msg.author == current:
						if msg.content in board:
							if xo == "X":
								xo = "O"
							else:
								xo = "X"
							space = board.index(msg.content)
							board[space] = xo
							counter += 1
							get = False
						else:
							await self.bot.say("Space already taken!")
					else:
						await self.bot.say("It's not your turn!")
				elif msg.content.lower() == "quit":
					await self.bot.say("Quitting game")
					return

			winList = checkttt(board)
			if len(winList) == 1:
				await self.bot.say("```" + "\n-----\n".join(["|".join(board[0:3]),"|".join(board[3:6]),"|".join(board[6:9])]) + "```")
				running = False
				await self.bot.say("We have a winner! " + current.name + " wins, with 3 " + xo + "s across " + str(winList[0][0]) + ", " + str(winList[0][1]) + " and " + str(winList[0][2]) + "!")
				return
			else:
				if current == host:
					current = challenger
				else:
					current = host
		await self.bot.say("```" + "\n-----\n".join(["|".join(board[0:3]),"|".join(board[3:6]),"|".join(board[6:9])]) + "```")
		await self.bot.say("The game ends in a tie... You're both too good!")

	##Game
	##Bomb
	@commands.command(pass_context = True)
	async def bomb(self,ctx,*commands):
		return
		if len(commands) != 0:
			setup = initialise(commands)
		else:
			await self.bot.say('''```Welcome to a game of BOMB DEFUSAL!
Here, 2-4 players will attempt to defuse all the bomb using the power of cooperation! Also, maybe voice chat.```''')
			await self.bot.say("```The host of today's game is " + ctx.message.author + "!```")
			bombMessage = await self.bot.say('''```To defuse your first bomb, answer how many players will be playing today?(Host only please)```''')
			timer(self.bot, 20)
			msg = await self.bot.wait_for_message(timeout = 20, author = ctx.message.author)
			if msg:
				return
			else:
				await self.bot.say("BOOM! (Really? The simplest question?)")


	##Basic
	##Suggest
	##Adds suggestions to a list
	@commands.command(pass_context = True)
	async def suggest(self, ctx, *, suggestion):
		addSug(ctx,suggestion)
		await self.bot.say('Suggestion Received!')

	##Set
	##Sets the channel the bot sends messages to
	@commands.command(pass_context = True)
	async def set(self, ctx):
		return

	##Game
	##Pyramid
	##Starts a pyramid game
	##Escape the pyramid!
	@commands.command()
	async def pyramid(self):
		return
		await self.bot.say(ctx.message.author, "Type [s]tart to begin or [e]xit to end game")
		message = await bot.wait_for_message(timeout=10, author=message.author)
		place = "start"
		running = True
		while running:
			if message == None:
				await bot.send_message(message.channel, "No reply found. Terminating game.")
				return
			elif message.content.lower == "start":
				start = True
				await bot.send_message(message.channel, "Game intialising!")

		while True:
			return "..."


	#Fun
	#Blend
	#Blend two profile pics
	@commands.command(pass_context=True, aliases = ["blend"])
	async def lend(self, ctx, user2:discord.User, user:discord.User = None):
		'''b.lend <user> [<user>]
- Blends your profile pic and another's
- If two users are specified, blend their's'''
		if not user:
			user = ctx.message.author

		link = user.avatar_url
		if not link:
			link = user.default_avatar_url

		response = requests.get(link)
		im = Image.open(BytesIO(response.content))

		link = user2.avatar_url
		if not link:
			link = user2.default_avatar_url

		response = requests.get(link)
		im2 = Image.open(BytesIO(response.content))

		im = Image.blend(im, im2, 0.5)

		im.save("TempFiles/{}.png".format(ctx.message.id))
		await self.bot.send_file(ctx.message.channel, "TempFiles/{}.png".format(ctx.message.id))
		os.remove("TempFiles/{}.png".format(ctx.message.id))

	#Fun
	#Invert
	#Invert a profile pic or an image
	@commands.command(pass_context=True)
	async def invert(self, ctx, user:discord.User = None):
		'''invert [<user>]
- Inverts your own or someone else's profile pic '''
		if not user:
			user = ctx.message.author

		link = user.avatar_url
		if not link:
			link = user.default_avatar_url

		response = requests.get(link)
		im = Image.open(BytesIO(response.content))

		im = ImageOps.invert(im)

		im.save("TempFiles/{}.png".format(ctx.message.id))
		await self.bot.send_file(ctx.message.channel, "TempFiles/{}.png".format(ctx.message.id))
		os.remove("TempFiles/{}.png".format(ctx.message.id))


	#Fun
	#Trigger
	#
	@commands.command(pass_context=True, aliases = ["triggered"])
	async def trigger(self, ctx, user:discord.User = None):
		'''trigger [<user>]
- *triggered* '''
		if not user:
			user = ctx.message.author

		link = user.avatar_url
		if not link:
			link = user.default_avatar_url

		await self.bot.send_typing(ctx.message.channel)

		fnt = ImageFont.truetype("impact.ttf", size = 40)
		response = requests.get(link)
		im = Image.open(BytesIO(response.content)).resize((230,230))
		im = ImageOps.crop(im, 15)
		redImage = Image.new('RGB', (200, 200), (100,0,0))
		d = ImageDraw.Draw(redImage)
		d.multiline_text((5,140), "TRIGGERED", fill = (255,20,30,0), font = fnt, align = "center")
		redImage = redImage.filter(ImageFilter.BLUR)
		frames = []
		for i in range(7):
			frames.append(ImageChops.offset(im, (math.floor(random()*2)*2-1)*math.floor(random()*20), (math.floor(random()*2)*2-1)*math.floor(random()*20)))
			frames[-1] = Image.blend(frames[-1], ImageChops.offset(redImage, math.ceil(random()*20),math.ceil(random()*20)), 0.5)
			await asyncio.sleep(0)

		frames[0].save("TempFiles/{}.gif".format(ctx.message.id), save_all=True, append_images = frames[1:], loop = 8)
		await self.bot.send_file(ctx.message.channel, "TempFiles/{}.gif".format(ctx.message.id))
		os.remove("TempFiles/{}.gif".format(ctx.message.id))

	#Fun
	#Static
	#Equalises a profile pic or an image
	@commands.command(pass_context=True, alias = ["equalize","equalise"])
	async def static(self, ctx, user:discord.User = None):
		'''static [<user>]
- Makes a profile pic look kinda static-y
- Works better with multi-coloured profile pictures'''
		if not user:
			user = ctx.message.author

		link = user.avatar_url
		if not link:
			link = user.default_avatar_url

		response = requests.get(link)
		im = Image.open(BytesIO(response.content))

		im = ImageOps.equalize(im)

		im.save("TempFiles/{}.png".format(ctx.message.id))
		await self.bot.send_file(ctx.message.channel, "TempFiles/{}.png".format(ctx.message.id))
		os.remove("TempFiles/{}.png".format(ctx.message.id))

	#Fun
	#deform
	#Deforms a profile pic or an image
	@commands.command(pass_context=True)
	async def deform(self, ctx, user:discord.User = None):
		return
		'''deform [<user>]
- Deforms your own or someone else's profile pic '''
		if not user:
			user = ctx.message.author

		link = user.avatar_url
		if not link:
			link = user.default_avatar_url

		response = requests.get(link)
		im = Image.open(BytesIO(response.content))

		class Deformer(object):
			def getmesh(self, im):
				x, y = im.size

				lis = [((0,0,x,y),(0,0,0,y,x,y,x,0))]

				for i in range(1):
					x1 = math.floor(random()*x)
					y1 = math.floor(random()*y)
					dx = math.floor(random()*x)
					dy = math.floor(random()*y)
					lis.append(((x1,y1,x1+dx,y1+dy), (x1, y1, x1+dx, y1, x1+dx, y1+dy, x1, y1+dy)))


				return lis

		deformer = Deformer()
		im = ImageOps.deform(im, deformer, 2)

		im.save("test.png")
		await self.bot.send_file(ctx.message.channel, "test.png")


	##Game
	##Pong
	##Play a classic game of pong
	@commands.command(pass_context=True)
	async def pong(self, ctx):
		size = (300, 200)

		positions = (0.5,0.5)
		ball = {"x":0.5, "y":0.5, "dy":-math.pi/2}

		playing = True

		while playing:
			im = Image.new('1', size)

			draw = ImageDraw.Draw(im)
			draw.rectangle([0, 0, size[0], 10], 1, 1)
			draw.rectangle([0, size[1], size[0], size[1]-10], 1, 1)

			im.save("test.png")
			await self.bot.send_file(ctx.message.channel, "test.png")
			playing = False

		return
		##Make game somehow
		##Maybe up and down to move paddle "u" and "d"
		##maybe add difficulty
		##delete message too
		##draw it instead?




	async def getBattleshipBoard(self, user):
		board1 = [["NONE" for y in range(8)] for x in range(8)]
		shipDict = {'A':4,'B':5,'S':2,'C':3,'D':3}
		shipList = ['A', 'B', 'C', 'D', 'S']

		embed = discord.Embed()

		msg = await bot.send_message()


		while len(shipList):
			await self.bot.send_message(user, )

	@commands.command(pass_context = True, aliases=["ship"])
	async def attleship(self, ctx, user:discord.User = None):
		return
		'''b.attleship [<user>]
- Plays a classic game of Battleship'''

		if user:
			await self.bot.say("Waiting for Player 1 ({}) to set their board...".format(ctx.message.author.name))
			board1 = await getBattleshipBoard(self, ctx.message.author)
			board2 = await getBattleshipBoard(self, user)
		else:
			board1 = await getBattleshipBoard(self, ctx.message.author)
			board2 = randomBoard()
		return




		board = battleShipBoard()

		msg = await self.bot.say("Setting Up Game!")


		emojiDict = {"left2":"\u23EA","left":"\u25C0","right":"\u25B6","right2":"\u23E9",
		"up":"\U0001F53C","up2":"\u23EB","down":"\U0001F53D","down2":"\u23EC",
		"spades":"\U0001F5A4", "flag":"\U0001F3F3", "square":"\u2B1B", "stop":"\U0001F6D1",
		"0":"0⃣", "1":"1⃣ ", "2":"2⃣ ", "3":"3⃣ ", "4":"4⃣ ", "5":"5⃣ ", "6":"6⃣ ", "7":"7⃣ ", "8":"8⃣", "9":":nine:",
		"F":"\U0001F3F3", "B":"\u2B1B", "BOOM":"💥", "selectSquare":"\U0001F533", "selectFlag":":triangular_flag_on_post:", "stopButton":":stop_button:",
		"tick":"\u2705", "S":"\u26F5", "D":"\U0001F6E5", "A":"\U0001F6A4", "B":"\u26F4", "C":"\U0001F6A2", "N": "🌊", "cross":"🇽"}

		shipNames = {"S":"Sailboats", "D":"Motorboats", "A":"Speedboats", "B":"Ferries", "C":"Cruisers"}

		emojiList = ["left2","left","right","right2","up2","up","down","down2", "tick", "cross", "stop"]
		for emoji in emojiList:
			await self.bot.add_reaction(msg, emojiDict[emoji])

		embed = discord.Embed(title=str(ctx.message.author) + "'s Battleship Game")
		embed.add_field(name="temp", value = "temp")
		embed.add_field(name="temp", value = "temp")
		shipsLeft = ["S","D","C","A","B"]
		for ship in shipsLeft:
			placing = True
			coord = [5,5]
			selected = False
			placed = False
			while placing:
				#print(ship)

				printField = copy.deepcopy(board.board)
				printField[coord[0]][coord[1]] = ship if printField[coord[0]][coord[1]] == "N" else "cross"
				embed.set_field_at(0, name = "​", value = "\n".join(list(map(lambda row: "".join(list(map(lambda space: emojiDict[space], row))), printField))), inline = False)
				embed.set_field_at(1, name = "Placing a fleet of " + shipNames[ship], value = "This fleet is " + str(board.shipDict[ship]) + " spaces.")

				await self.bot.edit_message(msg, new_content = " ", embed = embed)

				reaction = (await self.bot.wait_for_reaction(list(map(lambda emoji: emojiDict[emoji], emojiList)), user = ctx.message.author, message=msg)).reaction.emoji

				embed.remove_field(2)

				if reaction == emojiDict["up"]:
					if selected:
						#print(ship)
						test = board.placeShip(ship, coord, "N")
						if test:
							embed.add_field(name = test, value = "")
						else:
							placed = True
					else:
						coord[0] -= 1
				elif reaction == emojiDict["up2"]:
					if selected:
						if board.placeShip(selected, coord, "N"):
							embed.add_field(name = board.placeShip(ship, coord, "N"), value = "")
						else:
							board.confirmPlacement()
							placing = True
					else:
						coord[0] -= 4
				elif reaction == emojiDict["down"]:
					if selected:
						if board.placeShip(selected, coord, "S"):
							embed.add_field(name = board.placeShip(ship, coord, "N"), value = "")
						else:
							placed = True
					else:
						coord[0] += 1
				elif reaction == emojiDict["down2"]:
					if selected:
						if board.placeShip(selected, coord, "S"):
							embed.add_field(name = board.placeShip(ship, coord, "N"), value = "")
						else:
							board.confirmPlacement()
							placing = True
					else:
						coord[0] += 4
				elif reaction == emojiDict["left"]:
					if selected:
						if board.placeShip(selected, coord, "E"):
							embed.add_field(name = board.placeShip(ship, coord, "N"), value = "")
						else:
							placed = True
					else:
						coord[1] -= 1
				elif reaction == emojiDict["left2"]:
					if selected:
						if board.placeShip(selected, coord, "E"):
							embed.add_field(name = board.placeShip(ship, coord, "N"), value = "")
						else:
							board.confirmPlacement()
							placing = True
					else:
						coord[1] -= 4
				elif reaction == emojiDict["right"]:
					if selected:
						if board.placeShip(selected, coord, "W"):
							embed.add_field(name = board.placeShip(ship, coord, "N"), value = "")
						else:
							placed = True
					else:
						coord[1] += 1
				elif reaction == emojiDict["right2"]:
					if selected:
						if board.placeShip(selected, coord, "W"):
							embed.add_field(name = board.placeShip(ship, coord, "N"), value = "")
						else:
							board.confirmPlacement()
							placing = True
					else:
						coord[1] += 4
				elif reaction == emojiDict["stop"]:
					break
				elif reaction == emojiDict["tick"]:
					if selected and placed:
						board.undoPlacement()
						placed = False
					else:
						selected = False
				elif reaction == emojiDict["cross"]:
					if selected and placed:
						board.confirmPlacement()
						placing = True
					else:
						selected = True
				elif reaction == emojiDict["stop"]:
					embed.add_field(name="Game Canceled", value = "")
					await self.bot.edit_message(msg, embed = embed)

				coord = list(map(lambda co: 0 if co < 0 else 9 if co > 9 else co , coord))

				await self.bot.remove_reaction(msg, reaction, ctx.message.author)

		board.startGame()

		await self.bot.edit_message(msg, new_content = "Setting up the battlefield!")

		await self.bot.remove_reaction(msg, emojiDict["tick"], self.bot.user)
		await self.bot.remove_reaction(msg, emojiDict["cross"], self.bot.user)
		await self.bot.remove_reaction(msg, emojiDict["stop"], self.bot.user)

		await self.bot.add_reaction(msg, emojiDict["boom"])
		await self.bot.add_reaction(msg, emojiDict["stop"])

		enemyBoard = battleShipBoard()
		enemyBoard.randomBoard()
		enemyBoard.startGame()

		emojiList = emojiList = ["left2","left","right","right2","up2","up","down","down2", "boom", "stop"]
		embed = dicord.Embed(title=str(ctx.message.author) + "'s Battleship Game")
		coord = [4,4]
		AIturn = False
		playing = True
		embed.add_field(name="temp", value = "temp")
		embed.add_field(name="temp", value = "temp")
		while playing:
			embed.set_field_at(0, name="Your Harbour", value = "\n".join(list(map(lambda row: "".join(list(map(lambda space: emojiDict[space], row))), board.board))))
			printEnemy = copy.deepcopy(board.enemyBoard)
			printEnemy[coord[1]][coord[0]] = emjiDict["selectSquare"]
			embed.set_field_at(1, name="Enemy Harbour", value = "\n".join(list(map(lambda row: "".join(list(map(lambda space: emojiDict[space], row))), printEnemy))))
			await self.bot.edit_message(msg, new_content = " ", embed = embed)

			reaction = (await self.bot.wait_for_reaction(list(map(lambda emoji: emojiDict[emoji], emojiList)), user = ctx.message.author, message=msg)).reaction.emoji
			embed.remove_field(3)
			embed.remove_field(2)

			if reaction == emojiDict["boom"]:
				test = board.shootSpace(coord)
				board.updateEnemy(test)
				if "Error" in test[0]:
					embed.add_field(name=test, value = " ")
				elif test[0] == "Win!":
					endGame = "Win"
					break
				else:
					embed.add_field(name="You shot at " + str(coord[0]) + ", " + str(coord[1]), value = test)
					AIturn = True
			elif reaction == emojiDict["up"]:
				cood[0] -= 1
			elif reaction == emojiDict["up2"]:
				cood[0] -= 4
			elif reaction == emojiDict["down"]:
				cood[0] += 1
			elif reaction == emojiDict["down2"]:
				cood[0] += 4
			elif reaction == emojiDict["left"]:
				cood[1] -= 1
			elif reaction == emojiDict["left2"]:
				cood[1] -= 4
			elif reaction == emojiDict["right"]:
				cood[1] += 1
			elif reaction == emojiDict["right2"]:
				cood[1] += 4
			elif reaction == emojiDict["stop"]:
				endGame = "Quit"
				break
			cood = list(map(lambda co: 0 if co < 0 else size-1 if co > size-1 else co , cood))

			if AIturn:
				AIshot = enemyBoard.AIshoot()
				result = board.shootSpace(AIshot)
				enemyBoard.updateEnemy(result)

				embed.add_field(name="The AI shot at " + str(AIshot[0]) + ", " + str(AIshot[1]), value = result)
				if result[0] == "Win!":
					endGame = "Lose"

		embed.set_field_at(0, name="Your Harbour", value = "\n".join(list(map(lambda row: "".join(list(map(lambda space: emojiDict[space], row))), board.board))))
		printEnemy = copy.deepcopy(board.enemyBoard)
		printEnemy[coord[1]][coord[0]] = emjiDict["selectSquare"]
		embed.set_field_at(1, name="Enemy Harbour", value = "\n".join(list(map(lambda row: "".join(list(map(lambda space: emojiDict[space], row))), printEnemy))))

		if endGame == "Quit":
			embed.add_field(name = "Game Canceled.", value = " ")
		elif endGame == "Win":
			embed.add_field(name = "You Win!", value = " ")
		elif endGame == "Lose":
			embed.add_field(name = "You Lose...", value = " ")

		await self.bot.edit_message(msg, new_content = " ", embed = embed)
		await self.bot.clear_reactions(msg)


	@commands.command(pass_context = True, aliases = ['slot', 'spin', 'et', 'bet'])
	async def slots(self, ctx, bet = "wrong"):
		'''slots <bet>
- Plays a game of slots
- 50.8% chance of winning
- 48.2% chance of losing
- 1% chance of losing everything'''

		replace = {"k":"0"*3, "m":"0"*6, "b":"0"*9, "t":"0"*12, "q":"0"*15}

		for j in replace:
			bet = bet.replace(j,replace[j])

		try:
			bet = int(bet)
		except:
			await self.bot.say("Incorrect bet. Example of use: `b.slots 100`")
			return

		if bet <= 0:
			await self.bot.say("Seriously?")
			return

		if ctx.message.author.id not in self.bot.money or self.bot.money[ctx.message.author.id] < bet:
			await self.bot.say("Not enough money! You should b.orrow some more.")
			return

		if ctx.message.author.id in self.bot.slotsCheck:
			await self.bot.say("You are already playing a game of slots!")
			return
		else:
			self.bot.slotsCheck.append(ctx.message.author.id)

		currentMsg = await self.bot.say("```Welcome to the Slot Machine!\nYour current bet is " + str(bet) + " and your multiplier is only at 1 (for now). Type 'spin' for your chance to increase your multiplier!```")

		self.bot.money[ctx.message.author.id] -= bet

		with open('money.json','w') as fp:
			json.dump(self.bot.money, fp)

		multi = 1
		played = 0
		iconList = ["\U0001F4A9", "🚫", u"\U0001F525", u"\u274C", u"\U0001F44E",
		          u"\U0001F44D", "✅", u"\U0001F368", u"\U0001F4B3", u"\U0001F48E"]

		values = {u"\U0001F4A9":Decimal("-0.13"), "🚫":Decimal("-0.10"), u"\U0001F525":Decimal("-0.07"), u"\u274C":Decimal("-0.04"), u"\U0001F44E":Decimal("-0.01"), u"\U0001F44D":Decimal("0.01"), "✅":Decimal("0.04"), u"\U0001F368":Decimal("0.07"), u"\U0001F4B3":Decimal("0.10"), u"\U0001F48E":Decimal("0.13")}

		def generateSlotsBoard():
			return list(map(lambda row: list(map(lambda col: choice(iconList), range(5))), range(3)))

		def getSlotsMulti(board):
			combos = {"down":[], "right":[], "left":[]}
			everyCol = {board[0][0]:[0], board[1][0]:[1], board[2][0]:[2]}
			centerCombo = [1]

			for col in range(5):
				#Three in a horizontal row
				if board[0][col] == board[1][col] == board[2][col]:
					combos["down"].append(col)
				#The diagonals
				if 0 != col != 4:
					if board[0][col-1] == board[2][col+1] == board[1][col]:
						combos["right"].append(col)
					if board[0][col+1] == board[2][col-1] == board[1][col]:
						combos["left"].append(col)

				#Checking for combos in the center row
				if col == 0:
					last = board[1][col]
				else:
					if board[1][col] == last:
						centerCombo[-1] += 1
					else:
						last = board[1][col]
						centerCombo.append(1)
					#Checking for one of a kind in every column
					for pic in everyCol:
						for row in range(3):
							if board[row][col] == pic:
								everyCol[pic].append(row)
								break

			points = list(map(lambda pic: values[pic], board[1]))

			for combo in combos:
				for col in combos[combo]:
					points[col] *= 3
			newPoints = []
			col = -1
			for combo in centerCombo:
				point = 0
				for i in range(combo):
					col += 1
					point += points[col]
				if values[board[1][col]] > 0:
					newPoints.append(point*((combo+1)**(combo-1)))
				else:
					newPoints.append(point*(combo))

			multi = 1 + reduce(lambda x,y: x+y, newPoints)

			for col in range(5):
				multi += values[board[0][col]] + values[board[2][col]]

			for col in everyCol:
				if len(everyCol[col]) == 5:
					multi *= 1+5*values[col]
			return multi

		while played < 10:
			msg = await self.bot.wait_for_message(timeout = 60, channel = ctx.message.channel, author = ctx.message.author)
			if not msg:
				await self.bot.say("Error: Slots game timed out. Cashing out money.")
				break
			elif msg.content.lower() == "cash out":
				break
			elif msg.content.lower() == "spin":
				played += 1
				board = generateSlotsBoard()
				boardMulti = getSlotsMulti(board)

				embed = discord.Embed()
				embed.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url if ctx.message.author.avatar_url else ctx.message.author.default_avatar_url)

				embed.add_field(name = "Board:", value = '''⏸{0}⏸
▶{1}◀
⏸{2}⏸'''.format(" ".join(board[0]), " ".join(board[1]), " ".join(board[2])))

				if boardMulti < 0:
					embed.add_field(name = "Board Multiplier:", value = "Oh no, your multiplier was " + str(boardMulti) + "! This means you lost everything!")
					await self.bot.say(embed=embed)
					multi = 0
					break
				else:
					embed.add_field(name = "Your new Multiplier:", value = "`New` x `Old` = `Total`:\n" + "`" + str(round(boardMulti, 2)) + "` x `" + str(round(multi,2)) + "` = `" + str(round(boardMulti*multi,2)) + "`")
					embed.add_field(name = "Potential Money:", value = "`" + str(math.ceil(boardMulti*multi*bet)) + " b.ucks" + "`")
					embed.add_field(name = "Spins Left:", value = "`" + str(10-played) + "`")
					embed.set_footer(text = "If you want to spin again, type `spin`. If you want to cash out, type `cash out`.")

					multi *= boardMulti
					currentMsg = await self.bot.say(embed=embed)

		await self.bot.say(ctx.message.author.mention + " cashed out `" + str(math.ceil(bet*multi)) + "` b.ucks! " + (("Making a profit of `" + str(math.ceil(bet*multi)-bet) + "`") if math.ceil(bet*multi) >= bet else ("Making a loss of `" + str(bet-math.ceil(bet*multi)) + "`")) )
		self.bot.money[ctx.message.author.id] += math.ceil(bet*multi)
		self.bot.slotsCheck.pop(self.bot.slotsCheck.index(ctx.message.author.id))

		with open('money.json','w') as fp:
			json.dump(self.bot.money, fp)

	@commands.command(pass_context = True, aliases = "🏧")
	@commands.cooldown(1, 60*60, commands.BucketType.user)
	async def orrow(self, ctx):
		'''b.orrow
I'll lend you a few b.ucks ;)'''
		amount = math.ceil(random()*100)+100
		if ctx.message.author.id not in self.bot.money:
			self.bot.money[ctx.message.author.id] = amount
		else:
			self.bot.money[ctx.message.author.id] += amount
		await self.bot.say("Here, have " + str(amount) + " b.ucks")
		with open('money.json','w') as fp:
			json.dump(self.bot.money, fp)

	@commands.command(pass_context = True, aliases = ["go"])
	async def aduk(self, ctx, challenger:discord.Member = None):
		return
		'''go
- Plays a game of Go'''
		if not challenger:
			await self.bot.say("Mention a user!")
			return

		if not await checks.is_online(self.bot, challenger):
			return

		host = ctx.message.author

		if host == challenger:
			await self.bot.say("Did you just challenge yourself?")
			#return

		#choose player (add in later)
		players = [host, challenger]

		#This is from my class imported from go.py
		game = goGame()
		player = 1

		msg = await self.bot.say("Setting Up Game!")

		emojiList = ["left2","left","right","right2","up2","up","down","down2", "flag", "whiteCircle", "blackCircle"]

		emojiDict = {"left2":"\u23EA","left":"\u25C0","right":"\u25B6","right2":"\u23E9",
		"up":"\U0001F53C","up2":"\u23EB","down":"\U0001F53D","down2":"\u23EC",
		"spades":"\U0001F5A4", "flag":"\U0001F3F3", "square":"\u2B1B", "stop":"\U0001F6D1",
		"0":"0⃣", "1":"1⃣", "2":"2⃣", "3":"3⃣", "4":"4⃣", "5":"5⃣", "6":"6⃣", "7":"7⃣", "8":"8⃣",
		"F":"\U0001F3F3", "B":"\u2B1B", "M":"💥", "selectSquare":"\U0001F533", "selectFlag":"🚩", "stopButton":"⏹",

		"empty": "🔵",#"🔴",
		"whiteCircle": "⚪",
		"blackCircle": "⚫",
		"whiteOut": "🔲",
		"blackOut": "🔳",
		"blackIn":"⬛",
		"whiteIn":"⬜",

		}

		for emoji in emojiList[:-1]:
			await self.bot.add_reaction(msg, emojiDict[emoji])

		embed = discord.Embed(title = str(host) + " and " +  str(challenger) + "'s Go Game.")
		cood = [4,4]

		def boardChange(board, cood, player):
			newBoard = ""
			for row in range(len(board)):
				for col in range(len(board[row])):
					spot = board[row][col]
					if cood == [row, col]:
						if player == 1:
							if spot == player or spot == 0:
								newBoard += emojiDict["whiteIn"]
							else:
								newBoard += emojiDict["whiteOut"]
						else:
							if spot == player or spot == 0:
								newBoard += emojiDict["blackIn"]
							else:
								newBoard += emojiDict["blackOut"]
					else:
						if spot == 1:
							newBoard += emojiDict["whiteCircle"]
						elif spot == 2:
							newBoard += emojiDict["blackCircle"]
						else:
							newBoard += emojiDict["empty"]
				newBoard += "\n"
			return newBoard

		embed.add_field(name = "​", value = boardChange(game.board, cood, player))

		playing = True
		surrender = 0
		while True:

			await self.bot.edit_message(msg, new_content = " ", embed = embed)

			reaction = (await self.bot.wait_for_reaction(list(map(lambda emoji: emojiDict[emoji], emojiList)), timeout = 500, user = players[player-1], message=msg))

			if not reaction:
				await self.bot.edit_message(msg, new_content = "Error: Go game timed out.")
				await self.bot.clear_reactions(msg)
				return
			reaction = reaction.reaction.emoji

			if reaction == emojiDict["flag"]:
				game.captured[player-1] += 1
				if surrender == 1:
					break
				else:
					surrender = 1
			else:
				surrender = 0
			if reaction == emojiDict["up"]:
				cood[0] -= 1
			elif reaction == emojiDict["up2"]:
				cood[0] -= 4
			elif reaction == emojiDict["down"]:
				cood[0] += 1
			elif reaction == emojiDict["down2"]:
				cood[0] += 4
			elif reaction == emojiDict["left"]:
				cood[1] -= 1
			elif reaction == emojiDict["left2"]:
				cood[1] -= 4
			elif reaction == emojiDict["right"]:
				cood[1] += 1
			elif reaction == emojiDict["right2"]:
				cood[1] += 4
			if reaction == emojiDict["whiteCircle"] and player == 1:
				invalid = game.add(cood, player)
				if not invalid:
					player = 2
					await self.bot.remove_reaction(msg, emojiDict["whiteCircle"], ctx.message.server.me)
					await self.bot.add_reaction(msg, emojiDict["blackCircle"])

			elif reaction == emojiDict["blackCircle"] and player == 2:
				invalid = game.add(cood, player)
				if not invalid:
					player = 1
					await self.bot.remove_reaction(msg, emojiDict["blackCircle"], ctx.message.server.me)
					await self.bot.add_reaction(msg, emojiDict["whiteCircle"])
			cood = list(map(lambda co: 0 if co < 0 else 9-1 if co > 9-1 else co , cood))

			await self.bot.remove_reaction(msg, reaction, ctx.message.author)

			embed.set_field_at(0, name = "​", value = boardChange(game.board, cood, player))

		await self.bot.clear_reactions(msg)
		embed.set_field_at(0, name = "​", value = "\n".join(list(map(lambda row: "".join(list(map(lambda space: emojiDict[space], row))), field.simpleField()))), inline=False)
		if field.checkGame() == "win":
			embed.add_field(name = "Game Over:", value = "You Win!")
		elif field.checkGame() == "lose":
			embed.add_field(name = "Game Over:", value = "You Lose!")
		else:
			embed.add_field(name = "Game Canceled.", value = "​")

		await self.bot.edit_message(msg, new_content = None, embed = embed)



def setup(bot):
	bot.add_cog(Development(bot))
