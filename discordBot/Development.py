import discord
from discord.ext import commands

#everything
from random import choice, shuffle, randint
from asyncio import sleep
import secrets

#Goodbye, Welcome
import json

#invert, blend, triggered, static
from PIL import Image, ImageDraw, ImageOps, ImageChops, ImageFont, ImageFilter
import requests
from io import BytesIO

#giveme
import re
import colour
import os

#cah
from html2text import html2text as h2t

class Development():
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def welcome(self, ctx, * , message = ""):
		'''welcome <message>
- Customise the welcome message for new users
- Use {mention} to mention a new member
- {name} to say their name without a ping
- {servername} for the name of the server
- Type nothing to turn off the welcome message'''

		self.bot.serverInfo[str(ctx.message.guild.id)]['welcome'] = message
		await ctx.send("Welcome message edited!")

		with open('serverInfo.json','w') as fp:
			json.dump(self.bot.serverInfo, fp)

	@commands.command(aliases=['goodbye', 'bye'])
	@commands.has_permissions(administrator=True)
	async def ye(self, ctx, * , message = ""):
		'''b.ye <message>
- Customise the goodbye message for users
- {name} to say their name without a ping
- {servername} for the name of the server
- Type nothing to turn off the welcome message'''

		self.bot.serverInfo[str(ctx.message.guild.id)]['welcome'] = message
		await ctx.send("Goodbye message edited!")

		with open('serverInfo.json','w') as fp:
			json.dump(self.bot.serverInfo, fp)

	@commands.command(pass_context = True)
	async def spoiler(self, ctx, *, text):
		'''spoiler <text>
- Creates a "Hover to see spoiler text" gif'''

		await ctx.message.delete()

		maxWidth = 300
		border = 15

		im = Image.new('RGB', (200, 200), (255,255,255))
		d = ImageDraw.Draw(im)
		output = [""]

		fnt = ImageFont.truetype("calibri.ttf", size = 20)

		text = text.split(" ")

		for word in text:
			w,h =  d.textsize(output[-1] + " " + word, fnt)
			if w < maxWidth:
				output[-1] = output[-1] + " " + word
			else:
				w,h = d.textsize(word, fnt)
				if w > maxWidth:
					if output[-1]:
						output[-1] += "\n"
					for letter in word:
						w,h = d.textsize(output[-1] + letter + "-", fnt)
						if w > maxWidth:
							output[-1] += "-\n"
						output[-1] += letter
				else:
					output.append(word)

		print("\n".join(output))
		w, h = d.textsize("\n".join(output), fnt)

		img = Image.new('RGBA', (2*border+maxWidth,h+2*border), (54, 57, 62))
		d = ImageDraw.Draw(img)
		d.multiline_text((border,border), "\n".join(output), (255,255,255), fnt)
		d.rectangle([(0,0),(2*border+maxWidth-1,h+2*border-1)], outline = (0,0,0))

		hover = Image.new('RGBA', (2*border+maxWidth,h+2*border), (54, 57, 62))
		d = ImageDraw.Draw(hover)
		d.multiline_text((border,border), "[Hover or click for spoiler]", (255,255,255), fnt)
		d.rectangle([(0,0),(2*border+maxWidth-1,h+2*border-1)], outline = (0,0,0))

		hover.save("TempFiles/{}.gif".format(ctx.message.id), save_all = True, append_images = [img], duration = [1, 100000])
		with open("TempFiles/{}.gif".format(ctx.message.id), 'rb') as fp:
			await ctx.message.channel.send(file=discord.File(fp, "spoiler.gif"))
			fp.close()
		os.remove("TempFiles/{}.gif".format(ctx.message.id))

	@commands.command(pass_context = True)
	async def cah(self, ctx, points:int = 5):
		'''cah <point limit>
- Cards Against Humanity!
- 4-10 players, appropriate for ages 1(8) and up!
- Thanks to https://www.crhallberg.com/cah/json/ for providing the CAH json
- Type a number after the command to set a point limit (default is 5)'''

		messageReaction = choice([("Put your 🖐 up if you want to play!", "🖐"), ("🍆s out if you want to play!", "🍆"), ("Touch my 🍆 to play!", "🍆"), ("Push the 🔴 to play!", "🔴")])
		msg = await ctx.send("{} When everyone is in, the host should press the ✅!".format(messageReaction[0]))
		await msg.add_reaction(messageReaction[1])
		await msg.add_reaction("✅")

		while True:
			users = []
			def check(react, user):
				return user == ctx.message.author and react.message.id == msg.id and react.emoji == "✅"

			reactions = (await self.bot.wait_for('reaction_add', check=check))[0].message.reactions
			await msg.remove_reaction("✅", ctx.message.author)
			users = []
			for react in reactions:
				if react.emoji == messageReaction[1]:
					users = await react.users().flatten()

			if ctx.message.author not in users:
				users.append(ctx.message.author)

			for user in users:
				if user.bot:
					users.remove(user)
			if len(users) < 2:
				await ctx.send("You don't have enough players. You need at least 4 to play.")
			elif len(users) > 10:
				await ctx.send("You have too many players. You have to have 10 or less.")
			else:
				checkMsg = await ctx.send(secrets.clean("```Players:\n{}```Is this right?".format("\n".join(list(map(lambda user: user.display_name, users))))))
				await checkMsg.add_reaction("❌")
				await checkMsg.add_reaction("✅")

				def check(react, user):
					return user == ctx.message.author and react.message.id == checkMsg.id and react.emoji in ["✅", "❌"]

				if (await self.bot.wait_for('reaction_add', check = check))[0].emoji == "✅":
					break
				await checkMsg.delete()

		await msg.delete()

		await ctx.send("Welcome players, to Cards Against Humanity. We're shuffling the deck and 10 white cards will shortly be DM'd to you!")

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

		await sleep(1)

		for info in users:
			info['cardMsg'] = await info['user'].send("Here are your cards:\n{}".format("\n".join(list(map(lambda card: numbers[info['cards'].index(card)] + " `{}`".format(h2t(card)), info['cards'])))))

		while True:
			if len(deck['blackCards']) == 0:
				deck['blackCards'] = deck['blackDiscard']
				deck['blackDiscard'] = []
			blackCard = choice(deck['blackCards'])
			deck['blackDiscard'].append(blackCard)
			deck['blackCards'].remove(blackCard)

			users[czar]['picked'] = ["Card Czar"]
			users[czar]['picked'].extend([""]*(blackCard['pick']-1))
			await ctx.send(secrets.clean("{0}, you are the Card Czar this round! The black card is:\n\n```{1} Pick ({2})```\n".format(users[czar]['user'].display_name, blackCard['text'], blackCard['pick'])))

			for info in users:
				await info['cardMsg'].edit(content=secrets.clean("The Black Card for this round is ```{0} Pick ({1})```\n\nHere are your cards:\n{2}".format(blackCard['text'], blackCard['pick'], "\n".join(list(map(lambda card: numbers[info['cards'].index(card)] + " `{}`".format(h2t(card)), info['cards']))))))

			msg = await ctx.send("While the voting sets up, have a look at your cards and decide what you want to play. Remember, no backsies!")

			for emoji in numbers:
				await msg.add_reaction(emoji)

			while True:
				usersLeft = list(filter(lambda info: len(info['picked']) != blackCard['pick'], users))
				text = "```\n{} player(s) left to submit:\n".format(len(usersLeft))

				for info in list(filter(lambda info: len(info['picked']) != 0 and info['picked'][0] != "Card Czar", users)):
					text += "\n" + " ".join(map(lambda index: str(index+1), info['picked'])) + " - " + info['user'].display_name

				text += "\n\nIt might not see your guess, so make sure your name appears on the list.```"

				await msg.edit(content=text)

				usersToPick = list(map(lambda info: info['user'], usersLeft))
				def check(reaction, user):
					return user in usersToPick and reaction.emoji in numbers and numbers.index(reaction.emoji) not in usersLeft[usersToPick.index(user)]['picked'] and reaction.message.id == msg.id
				userReaction = await self.bot.wait_for('reaction_add', check = check)

				usersLeft[usersToPick.index(userReaction[1])]['picked'].append(numbers.index(userReaction[0].emoji))

				if len(list(filter(lambda info: len(info['picked']) != blackCard['pick'], users))) == 0:
					break

			await msg.delete()

			answers = []
			for info in users:
				if info['picked'][0] != 'Card Czar':
					answers.append(info)

			shuffle(answers)

			msg = await ctx.send("Here are the white cards for the prompt:\n```{0}```\n{1}".format(blackCard['text'], "\n".join((numbers[i] + " " + " and ".join(list(map(lambda index: "`{}`".format(h2t(answers[i]['cards'][index])), answers[i]['picked'])))) for i in range(len(answers)))
			))

			msg = await ctx.send("```Okay Card Czar, have a deep think about which one is the best. Or the most disgusting.```")

			for i in range(len(answers)):
				await msg.add_reaction(numbers[i])

			def check(react, user):
				return react.message.id == msg.id and react.emoji in numbers[:len(answers)] and user == users[czar]['user']

			winner = numbers.index((await self.bot.wait_for('reaction_add', check=check))[0].emoji)

			await ctx.send("You chose \n\n{0}\n\n which was played by {1}. Congrats on the point!".format(" and ".join(list(map(lambda index: "`{}`".format(h2t(answers[winner]['cards'][index])), answers[winner]['picked']))), answers[winner]['user'].display_name))

			answers[winner]['points'] += 1

			await ctx.send(secrets.clean("```\nScoreboard:\n{}```".format("\n".join(list(map(lambda info: info['user'].display_name + " - "+ str(info['points']), sorted(users, key = lambda info: info['points'], reverse=True)))))))

			if answers[winner]['points'] == points:
				await ctx.send(secrets.clean("We have a winner! Congratulations {}".format(answers[winner]['user'].display_name)))
				break
			else:
				await sleep(1)
				czar = (czar + 1)%len(users)

				await ctx.send("New round! Don't forget to check out your new card.")

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

			if 'giveme' not in self.bot.serverInfo[str(ctx.message.guild.id)] or not len(self.bot.serverInfo[str(ctx.message.guild.id)]['giveme']):
				await ctx.send("There are no giveme roles in your server. Ask a mod to create some using `b.giveme create <name> <colour>`")
				return

			if name in self.bot.serverInfo[str(ctx.message.guild.id)]['giveme']:
				getRole = None
				for role in ctx.message.guild.roles:
					if role.id == self.bot.serverInfo[str(ctx.message.guild.id)]['giveme'][name]['id']:
						getRole = role

				if getRole:
					await ctx.message.author.add_roles(getRole, reason = 'giveme role!')
					await ctx.send("Added role!")
					return
				del self.bot.serverInfo[str(ctx.message.guild.id)]['giveme'][name]
			await ctx.send("There is no giveme role called `{}`.".format(secrets.clean(name)))

	@giveme.command()
	@commands.has_permissions(manage_roles = True)
	async def create(self, ctx, name = None, *, col = None):
		if not name or not col:
			await ctx.send("Use format `b.create <name> <colour>`")
			return

		if 'giveme' not in self.bot.serverInfo[str(ctx.message.guild.id)]:
			self.bot.serverInfo[str(ctx.message.guild.id)]['giveme'] = {}

		if name.lower() in self.bot.serverInfo[str(ctx.message.guild.id)]['giveme']:
			await ctx.send("There is already a role of that name.")
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
				await ctx.send("`{}` is not a recognised colour".format(secrets.clean(col)))
				return

		newRole = await ctx.message.guild.create_role(name=name, colour = discord.Colour(int(col.hex_l[1:],16)), reason = "Created giveme role!")
		await ctx.send("Created role!")
		self.bot.serverInfo[str(ctx.message.guild.id)]['giveme'][name.lower()] = {'id':newRole.id, 'name':name, 'colour':"%s"%col}
		with open('serverInfo.json','w') as fp:
			json.dump(self.bot.serverInfo, fp)

	@giveme.command()
	@commands.has_permissions(manage_roles = True)
	async def edit(self, ctx, name = None, *, col = None):
		if not name or not col:
			await ctx.send("Use format `b.edit <name> <colour>`")
			return
		name = name.lower()
		if 'giveme' not in self.bot.serverInfo[str(ctx.message.guild.id)] or len(self.bot.serverInfo[str(ctx.message.guild.id)]['giveme']) == 0:
			await ctx.send("There are no giveme roles in your server. Try using `b.giveme create <name> <colour>`")
			return

		getRole = None
		for role in ctx.message.guild.roles:
			if role.id == self.bot.serverInfo[str(ctx.message.guild.id)]['giveme'][name]['id']:
				getRole = role
		if not getRole:
			await ctx.send("There is no giveme role called {} in your server.".format(name))

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
				await ctx.send("`{}` is not a recognised colour".format(col))
				return

		await getRole.edit(colour = discord.Colour(int(col.hex_l[1:],16)))
		await ctx.send("Edited role!")
		self.bot.serverInfo[str(ctx.message.guild.id)]['giveme'][name]['colour'] = "%s"%col
		with open('serverInfo.json','w') as fp:
			json.dump(self.bot.serverInfo, fp)


	@giveme.command(name = "list")
	async def list(self, ctx):
		lis = []

		if 'giveme' in self.bot.serverInfo[str(ctx.message.guild.id)] and self.bot.serverInfo[ctx.message.guild.id]['giveme']:
			for role in self.bot.serverInfo[str(ctx.message.guild.id)]['giveme']:
				lis.append(self.bot.serverInfo[str(ctx.message.guild.id)]['giveme'][role]['name'] + "\n\t- " + self.bot.serverInfo[str(ctx.message.guild.id)]['giveme'][role]['colour'])
			await ctx.send("```\n{}```".format("\n".join(lis)))
		else:
			await ctx.send("There are no roles available for `giveme`. Create one using `giveme create 'name' 'colour'`")


	@giveme.command()
	async def remove(self, ctx, *, name):
		name = name.lower()
		if 'giveme' in self.bot.serverInfo[str(ctx.message.guild.id)] and name in self.bot.serverInfo[str(ctx.message.guild.id)]['giveme']:
			getRole = None
			for role in ctx.message.guild.roles:
				if role.id == self.bot.serverInfo[str(ctx.message.guild.id)]['giveme'][name]['id']:
					getRole = role
			if getRole:
				if getRole in ctx.message.author.roles:
					await ctx.message.author.remove_roles(getRole)
					await ctx.send("Role removed!")
				else:
					await ctx.send("You don't have that role.")
				return
		await ctx.send("There is no role by that name.")

	@giveme.command()
	@commands.has_permissions(manage_roles = True)
	async def delete(self, ctx, *, name):
		if 'giveme' in self.bot.serverInfo[str(ctx.message.guild.id)] and name in self.bot.serverInfo[str(ctx.message.guild.id)]['giveme']:
			getRole = None
			for role in ctx.message.guild.roles:
				if role.id == self.bot.serverInfo[str(ctx.message.guild.id)]['giveme'][name]['id']:
					getRole = role
					del self.bot.serverInfo[str(ctx.message.guild.id)]['giveme'][name]
			if getRole:
				await getRole.delete(reason = "giveme delete!")
			await ctx.send("Role deleted!")
		else:
			await ctx.send("There is no role by that name.")

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
	##TTT
	@commands.command(pass_context = True)
	async def ttt(self, ctx, challenger:discord.Member = None):
		'''ttt <user>
Plays a game of Tic Tac Toe'''
		if not challenger:
			await ctx.send("Mention a user!")
			return

		host = ctx.message.author

		board = ["1", "2", "3",
				"4", "5", "6",
				"7", "8", "9"]

		numbers = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣"]

		msg = await ctx.send("```{}```".format("\n-----\n".join(["|".join(board[0:3]),"|".join(board[3:6]),"|".join(board[6:9])])))

		for emoji in numbers:
			await msg.add_reaction(emoji)

		current = choice([host,challenger])

		xo = "O"

		def check(react, user):
			return react.message.id == msg.id and user == current and react.emoji in numbers and board[numbers.index(react.emoji)] not in ["X", "O"]

		def checkttt(board):
			boardWin = [[1,2,3], [4,5,6], [7,8,9],
						[1,4,7], [2,5,8], [3,6,9],
						[1,5,9], [3,5,7]]
			winList = []
			for win in boardWin:
				if board[win[0]-1][0] == board[win[1]-1][0] and board[win[2]-1][0] == board[win[1]-1][0]:
					return win
			return None

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

		count = 0
		while not checkttt(board) or count == 9:
			xo = "O" if xo == "X" else "X"
			current = host if current == challenger else challenger

			await msg.edit(content = "```It's {0}'s turn!\n\n{1}```".format(secrets.clean(current.display_name), "\n-----\n".join(["|".join(board[0:3]),"|".join(board[3:6]),"|".join(board[6:9])])))

			move = (await self.bot.wait_for('reaction_add', check = check))[0].emoji

			await msg.remove_reaction(move, current)
			await msg.remove_reaction(move, self.bot.user)

			board[numbers.index(move)] = xo
			count += 1

		await msg.clear_reactions()

		if count != 9:
			winList = checkttt(board)
			running = False
			await msg.edit(content = msg.content + "\nWe have a winner! {0} wins, with 3 {1}s across {2}".format(secrets.clean(current.display_name), xo, " ".join(map(str,winList))))
		else:
			await msg.edit(content = msg.content + "\nThe game ends in a tie... You're both too good!")

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

		async with ctx.message.channel.typing():
			response = requests.get(user.avatar_url_as(format='png'))
			im = Image.open(BytesIO(response.content)).convert('RGBA').resize((200,200))

			response = requests.get(user2.avatar_url_as(format='png'))
			im2 = Image.open(BytesIO(response.content)).convert('RGBA').resize((200,200))

			im = Image.blend(im, im2, 0.5)

			im.save("TempFiles/{}.png".format(ctx.message.id))
			with open("TempFiles/{}.png".format(ctx.message.id), 'rb') as fp:
				await ctx.message.channel.send(file=discord.File(fp, "blend.png"))
				fp.close()
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

		async with ctx.message.channel.typing():
			response = requests.get(user.avatar_url_as(format='png'))
			im = ImageOps.invert(Image.open(BytesIO(response.content)).convert('RGB')).resize((200,200))

			im.save("TempFiles/{}.png".format(ctx.message.id))
			with open("TempFiles/{}.png".format(ctx.message.id), 'rb') as fp:
				await ctx.message.channel.send(file=discord.File(fp, "invert.png"))
				fp.close()
			os.remove("TempFiles/{}.png".format(ctx.message.id))


	#Fun
	#Trigger
	@commands.command(aliases = ["triggered"])
	async def trigger(self, ctx, user:discord.User = None):
		'''trigger [<user>]
- *triggered* '''
		if not user:
			user = ctx.message.author

		link = user.avatar_url_as(format = 'png')

		async with ctx.message.channel.typing():
			fnt = ImageFont.truetype("impact.ttf", size = 40)
			response = requests.get(link)
			im = Image.open(BytesIO(response.content)).convert('RGB').resize((230,230))
			im = ImageOps.crop(im, 15)
			redImage = Image.new('RGB', (200, 200), (100,0,0))
			d = ImageDraw.Draw(redImage)
			d.multiline_text((5,140), "TRIGGERED", fill = (255,20,30,0), font = fnt, align = "center")
			redImage = redImage.filter(ImageFilter.BLUR)
			frames = []
			for i in range(10):
				frames.append(Image.blend(ImageChops.offset(im, randint(-10,10), randint(-10,10)), ImageChops.offset(redImage, randint(0,20), randint(-10,10)), 0.5))
				await sleep(0.1)

			frames[0].save("TempFiles/{}.gif".format(ctx.message.id), save_all=True, append_images = frames[1:], loop = 8)
			with open("TempFiles/{}.gif".format(ctx.message.id), 'rb') as fp:
				await ctx.message.channel.send(file=discord.File(fp, "trigger.gif"))
				fp.close()
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


		async with ctx.message.channel.typing():
			link = user.avatar_url_as(format = 'png')

			response = requests.get(link)
			im = Image.open(BytesIO(response.content)).convert('RGB').resize((200,200))

			im = ImageOps.equalize(im)

			im.save("TempFiles/{}.png".format(ctx.message.id))
			with open("TempFiles/{}.png".format(ctx.message.id), 'rb') as fp:
				await ctx.message.channel.send(file=discord.File(fp, "static.png"))
				fp.close()
			os.remove("TempFiles/{}.png".format(ctx.message.id))

def setup(bot):
	bot.add_cog(Development(bot))
