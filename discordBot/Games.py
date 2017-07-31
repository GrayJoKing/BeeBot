import discord
from discord.ext import commands

#Bang, hang,
from random import random, choice

#Hang
from re import search

#Bang
import json
import secrets

#Slots
from functools import reduce
from decimal import Decimal
import calc
from math import ceil

#boom
from boom import *

class Games():
	def __init__(self, bot):
		self.bot = bot
		bot.bangCheck = {}
		bot.slotsCheck = {}

	def getLeaderBoard(self):
		scores = []
		for user in self.bot.bangStats:
			scores.append([user, self.bot.bangStats[user]])
		scores.sort(key=lambda x: x[1]["lStreak"], reverse=True)
		return scores

	#b.ang
	#Game
	@commands.group(aliases = ["bang"])
	async def ang(self, ctx):
		'''b.ang ["stats" [<user>]|"leaderboard"]
- Russian Roulette
- Use the "stats" command to see how well you or another user has played
	- Name a user to see how they've played
- Use the "leaderboard" command to see the current highscores'''
		if ctx.invoked_subcommand:
			return

		user = ctx.message.author

		#Creates a new user profile in bangStats
		if user.id not in self.bot.bangStats:
			self.bot.bangStats[user.id] = {'play':0,'kill':0,'lStreak':0,'cStreak':0,'name':user.name}

		#If the user has already triggered this but the bot hasn't posted the message (being rate-limited) exit
		##This might accidentally stop people whose message was lost because of connection issues
		if user.id in self.bot.bangCheck and self.bot.bangCheck[user.id]:
			return
		self.bot.bangCheck[user.id] = True

		#Pulls the trigger
		if random() > 1/6:
			#You're alive!
			txt = ":relieved::gun:\nPhew, you survived, `{}`".format(secrets.clean(user.name))
			self.bot.bangStats[user.id]['cStreak'] += 1
			#Checks whether this is your longest streak
			if self.bot.bangStats[user.id]['cStreak'] > self.bot.bangStats[user.id]['lStreak']:
				self.bot.bangStats[user.id]['lStreak'] = self.bot.bangStats[user.id]['cStreak']
				txt += "\nYou beat your longest streak! You are now at `{}`!".format(self.bot.bangStats[user.id]['cStreak'])

				#checks whether you can go on the leaderboard
				leaderboard = self.getLeaderBoard()
				for place in range(len(leaderboard)):
					if leaderboard[place][0] == user.id:
						txt += "\nYou are on the leaderboard at number `{}`!".format(place+1)

		else:
			#You're dead...
			txt = ":dizzy_face::boom::gun:\nOh dear. You're dead, `{0}`. Your streak was: `{1}`!".format(user.name, str(self.bot.bangStats[user.id]['cStreak']))
			self.bot.bangStats[user.id]['kill'] += 1
			self.bot.bangStats[user.id]['cStreak'] = 0
		self.bot.bangStats[user.id]['play'] += 1
		self.bot.bangStats[user.id]['name'] = user.name
		msg = await ctx.send(secrets.clean(txt))
		self.bot.bangCheck[user.id] = False

		#Saves the results
		with open('gameData/bang.json','w') as fp:
			json.dump(self.bot.bangStats, fp)

	#Bang stats
	@ang.command(name='stats')
	async def bangstats(self, ctx, *, user:discord.User = None):
		if not user:
			user = ctx.message.author

		if user.id in self.bot.bangStats:
				txt = "Stats for `{0}`\nTimes Played: `{1}`\nTimes Killed: `{2}`".format(user.name, self.bot.bangStats[user.id]['play'], self.bot.bangStats[user.id]["kill"])
				if self.bot.bangStats[user.id]["kill"] != 0:
					txt += "\nW/L Ratio: `{}:1`".format(round((self.bot.bangStats[user.id]["play"] - self.bot.bangStats[user.id]["kill"])/self.bot.bangStats[user.id]["kill"], 2))
				else:
					txt += "\nW/L Ratio: `∞:∞`"
				txt += "\nLongest Streak: `{0}`\nCurrent Streak: `{1}`".format(self.bot.bangStats[user.id]["lStreak"], self.bot.bangStats[user.id]["cStreak"])

				leaderboard = self.getLeaderBoard()
				for place in range(len(leaderboard)):
					if leaderboard[place][0] == user.id:
						txt += "\nRank: `{}`".format(place+1)
		else:
			txt = "No profile for `{}`! Play the game to get one.".format(user.name)

		await ctx.send(secrets.clean(txt))

	#Bang leaderboard
	@ang.command(name='leaderboard')
	async def bangleaderboard(self, ctx):
		leaderboard = self.getLeaderBoard()[:10]
		await ctx.send(secrets.clean("```{}```".format("\n".join(list(map(lambda place: "{0}: {1} {2}".format(leaderboard.index(place)+1, place[1]["lStreak"], place[1]['name']) , leaderboard))))))


	##Hang
	##Game of Hangman
	@commands.command(pass_context = True)
	async def hang(self, ctx, *sub):
		'''b.hang ["co-op"] (["long"]|["short"])
- Play a game of hangman
Commands
- Co-op
	- Anyone can play
- Long
	- Only long words are used
- Short
	- Only short words are used'''

		sub = list(sub)
		commands = []
		wordL = []
		coop = False
		sep = ","
		if "co-op" in sub:
			coop = True
			sub.pop(sub.index("co-op"))
			commands.append("Co-op: All players can play!")
		if "long" in sub:
			wordL = self.bot.wordLists["long"]
			sub.pop(sub.index("long"))
			commands.append("Long: Words are very long (Easy!)")
		elif "short" in sub:
			wordL = self.bot.wordLists["short"]
			sub.pop(sub.index("short"))
			commands.append("Short: Words are very short (Hard!)")
		else:
			wordL = self.bot.wordLists["medium"]

		if len(sub) > 0:
			await ctx.send("Error, Commands not found: `{0}`".format("`, `".join(list(map(lambda command: secrets.clean(command), sub))))) #invisible space here
			return

		divider = "?"
		originalWord = choice(wordL)
		word = list(originalWord)

		wordGuess = [divider for _ in range(len(word))]

		correct = []
		incorrect = []
		guesses = 0
		player = ctx.message.author
		channel = ctx.message.channel
		tellMsg = False
		if len(commands) > 0:
			await ctx.send("`{}`".format("`\n`".join(commands)))
		await ctx.send('''```{0}
 O
/|\\
/ \\
You have to help me before they finish the construction of the gallows!\n```'''.format(choice(secrets.hangReasons)))
		while divider in wordGuess and guesses < 10:
			if tellMsg is not None:
				hangStr = '''```Guess using letters or words within {sep} i.e. {sep}e{sep}. Type quit to exit the game. {guesses}
{wordguess}
{guessesLeft} guesses remaining.
Correct Guesses: {correct}
Incorrect Guesses: {incorrect}```'''.format(sep=sep, guesses = secrets.hangedmen[guesses], wordguess=''.join(wordGuess), guessesLeft=10-guesses, correct = ", ".join(correct), incorrect=", ".join(incorrect))
				if tellMsg != False:
					hangStr += "\n`" + tellMsg + "`"
				await ctx.send(hangStr)


			def check(msg):
				if (not coop and msg.author != player) or msg.author.bot or msg.channel != ctx.channel:
					return False

				if msg.content.lower() == "quit":
					return True
				m = search("{sep}([a-zA-Z]*){sep}".format(sep=sep), msg.content)
				if m and m.group(1).isalpha():
					return True
				return False

			if not coop:
				msg = await self.bot.wait_for('message', check=check)

			m = search(sep +"([a-zA-Z]*)" + sep,msg.content)
			if m:
				guess = search("{sep}([a-zA-Z]*){sep}".format(sep=sep), msg.content).group(1).lower()
				if len(guess) == 1:
					ind = []

					for index,value in enumerate(word):
						if value == guess:
							ind.append(index)

					if len(ind) == 0:
						incorrect.append(guess)
						tellMsg = "\n" + guess + " is incorrect!"
						guesses += 1
					else:
						tellMsg = "\n" + guess + " is correct!"
						correct.append(guess)
						for i in ind:
							word[i] = divider
							wordGuess[i] = guess
				else:
					tellMsg = None
					if guess != originalWord:
						guesses += 1
						tellMsg = "\n" + guess + " is not the word!"
						incorrect.append(guess)
					else:
						wordGuess = list(originalWord)
						correct.append(guess)
						break
			elif msg.content.lower() == "quit":
				await ctx.send("Quitting game")
				return
			else:
				tellMsg = None
		if guesses == 10:
			x = "Ran out of guesses! Justice is served. The word was {}".format(originalWord)
			stick = secrets.hangedmen[10]
		else:
			x = "Congratulations, you saved the life of a dangerous criminal! But at least you won right?"
			stick = '''\\O/
 |
/ \\
'''
		await ctx.send("```{stick}\nCorrect Guesses: {correct}\nIncorrect Guesses: {incorrect}```\n`{message}`".format(stick = stick, guess = ''.join(wordGuess), correct = ", ".join(correct), incorrect = ", ".join(incorrect), message = x))


	@commands.command(pass_context = True, aliases=["mine","minesweeper","ms"])
	async def oom(self, ctx):
		'''b.oom
- Plays a classic game of Minesweeper
- Warning, this game requires reactions'''

		size = 9
		mineNum = 12

		#This is from my class imported from boom.py
		field = minefield(size, mineNum)

		msg = await ctx.send("Setting Up Game!")

		emojiList = ["left2","left","right","right2","up2","up","down","down2", "spades", "flag", "stop"]

		emojiDict = {"left2":"\u23EA","left":"\u25C0","right":"\u25B6","right2":"\u23E9",
		"up":"\U0001F53C","up2":"\u23EB","down":"\U0001F53D","down2":"\u23EC",
		"spades":"\U0001F5A4", "flag":"\U0001F3F3", "square":"\u2B1B", "stop":"\U0001F6D1",
		"0":"0⃣", "1":"1⃣", "2":"2⃣", "3":"3⃣", "4":"4⃣", "5":"5⃣", "6":"6⃣", "7":"7⃣", "8":"8⃣",
		"F":"\U0001F3F3", "B":"\u2B1B", "M":"💥", "selectSquare":"\U0001F533", "selectFlag":"🚩", "stopButton":"⏹"}

		for emoji in emojiList:
			await msg.add_reaction(emojiDict[emoji])

		embed = discord.Embed(title = "{}'s Minesweeper Game.".format(ctx.message.author.name))
		cood = [4,4]
		printField = field.simpleField()
		printField[cood[0]][cood[1]] = "selectSquare" if printField[cood[0]][cood[1]] == "B" else ("selectFlag" if printField[cood[0]][cood[1]] == "F" else "stopButton")
		embed.add_field(name = "​", value = "\n".join(list(map(lambda row: "".join(list(map(lambda space: emojiDict[space], row))), printField))))

		playing = True
		while field.checkGame() == "playing":

			await msg.edit(content = None, embed = embed)

			def check(react, user):
				return react.emoji in list(map(lambda emoji: emojiDict[emoji], emojiList)) and react.message == msg, user == ctx.message.author

			reaction = (await self.bot.wait_for('reaction_add', check=check))[0].emoji

			if reaction == emojiDict["flag"]:
				field.flag(cood)
			elif reaction == emojiDict["spades"]:
				if not field.minefield[cood[0]][cood[1]].flagged:
					field.clickSpace(cood[::-1])

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
				break
			cood = list(map(lambda co: 0 if co < 0 else size-1 if co > size-1 else co, cood))

			await msg.remove_reaction(reaction, ctx.message.author)

			printField = field.simpleField()
			printField[cood[0]][cood[1]] = "selectSquare" if printField[cood[0]][cood[1]] == "B" else ("selectFlag" if printField[cood[0]][cood[1]] == "F" else "stopButton")
			embed.set_field_at(0, name = "​", value = "\n".join(list(map(lambda row: "".join(list(map(lambda space: emojiDict[space], row))), printField))))

		await msg.clear_reactions()
		embed.set_field_at(0, name = "​", value = "\n".join(list(map(lambda row: "".join(list(map(lambda space: emojiDict[space], row))), field.simpleField()))), inline=False)
		if field.checkGame() == "win":
			embed.add_field(name = "Game Over:", value = "You Win!")
		elif field.checkGame() == "lose":
			embed.add_field(name = "Game Over:", value = "You Lose!")
		else:
			embed.add_field(name = "Game Canceled.", value = "​")

		await msg.edit(content = None, embed = embed)

	@commands.command(aliases = ['slot', 'spin', 'et', 'bet'])
	async def slots(self, ctx, *, bet = ""):
		'''slots <bet>
- Plays a game of slots
- 50.8% chance of winning
- 48.2% chance of losing
- 1% chance of losing everything'''

		replace = {"k":"*1"+"0"*3, "m":"*1"+"0"*6, "b":"*1"+"0"*9, "t":"*1"+"0"*12, "q":"*1"+"0"*15}

		for j in replace:
			bet = bet.replace(j,replace[j])

		bet = bet.replace(" ", "")
		bet = calc.calcFunc(bet)

		try:
			bet = int(bet)
		except:
			await ctx.send("Incorrect bet. Example of use: `b.slots 100`")
			return

		if bet <= 0:
			await ctx.send("Incorrect bet. Example of use: `b.slots 100`")
			return

		if str(ctx.message.author.id) not in self.bot.money or self.bot.money[str(ctx.message.author.id)] < bet:
			await ctx.send("Not enough money! You should b.orrow some more.")
			return

		if str(ctx.message.author.id) in self.bot.slotsCheck:
			await ctx.send("You are already playing a game of slots!")
			return
		else:
			self.bot.slotsCheck[str(ctx.message.author.id)] = True

		currentMsg = await ctx.send("```Welcome to the Slot Machine!\nYour current bet is {} and your multiplier is only at 1 (for now). Type 'spin' for your chance to increase your multiplier!```".format(bet))

		self.bot.money[str(ctx.message.author.id)] -= bet

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

			def check(msg):
				return msg.channel == ctx.message.channel and msg.author == ctx.message.author and (msg.content.lower() == "cash out" or msg.content.lower() == "spin")

			msg = await self.bot.wait_for('message', check=check)
			if msg.content.lower() == "cash out":
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

				if boardMulti < 0 or ceil(boardMulti*multi*bet) <= 0:
					embed.add_field(name = "Board Multiplier:", value = "Oh no, your multiplier was `{}`! This means you lost everything!".format(boardMulti))
					await ctx.send(embed=embed)
					multi = 0
					played = 10
				else:
					embed.add_field(name = "Your new Multiplier:", value = "`New` x `Old` = `Total`:\n`{0}`x `{1}` = `{2}`".format(round(boardMulti, 2), round(multi,2), round(boardMulti*multi, 2)))
					embed.add_field(name = "Potential Money:", value = "`{} b.ucks`".format(ceil(boardMulti*multi*bet)))
					embed.add_field(name = "Spins Left:", value = "`{}`".format(10-played))
					embed.set_footer(text = "If you want to spin again, type `spin`. If you want to cash out, type `cash out`.")

					multi *= boardMulti
					currentMsg = await ctx.send(embed=embed)

		await ctx.send("{0} cashed out `{1}` b.ucks! Making a {2}".format(secrets.clean(ctx.message.author.name), ceil(bet*multi), "profit of `{}`".format(ceil(bet*multi)-bet) if ceil(bet*multi) >= bet else "loss of `{}`".format(bet-ceil(bet*multi))))
		self.bot.money[str(ctx.message.author.id)] += ceil(bet*multi)

		del self.bot.slotsCheck[str(ctx.message.author.id)]

		with open('money.json','w') as fp:
			json.dump(self.bot.money, fp)

def setup(bot):
	bot.add_cog(Games(bot))
