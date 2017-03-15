import discord
from discord.ext import commands
import checks

#Bang, hang,
from random import random, choice

#Hang
import re
from os import path

#Bang
import json
import secrets

#boom
from boom import *

class Games():
	def __init__(self, bot):
		self.bot = bot
		self.bot.bangStats = {}
		self.bot.bangCheck = {}

		with open('ang (copy).json','r') as fp:
			self.bot.bangStats = json.load(fp)
			fp.close()

		self.bot.hangCheck = {}
		self.bot.wordLists = {}
		wordTypes = ["short", "medium", "long"]
		for wordType in wordTypes:
			file_path = path.relpath("wordTxt/10000{0}.txt".format(wordType))
			self.bot.wordLists[wordType] = []
			wordList = open(file_path)
			for line in wordList:
				line = line.strip()
				if len(line) > 0:
					self.bot.wordLists[wordType].append(line)
			wordList.close()

	#b.ang
	#Game
	@commands.group(pass_context = True)
	async def ang(self, ctx):
		'''b.ang ["stats" [<user>]|"leaderboard"]
- Russian Roulette
- Use the "stats" command to see how well you or another user has played
	- Name a user to see how they've played
- Use the "leaderboard" command to see the current highscores'''
		if ctx.invoked_subcommand:
			return

		user = str(ctx.message.author)
		userid = str(ctx.message.author.id)

		#Creates a new user profile in bangStats
		if userid not in self.bot.bangStats:
			self.bot.bangStats[userid] = {'play':0,'kill':0,'lStreak':0,'cStreak':0}

		#If the user has already triggered this but the bot hasn't posted the message (being rate-limited) exit
		##This might accidentally stop people whose message was lost because of connection issues
		if userid in self.bot.bangCheck and self.bot.bangCheck[userid]:
			return
		self.bot.bangCheck[userid] = True

		#Pulls the trigger
		if random() > 1/6:
			#You're alive!
			txt = ":relieved::gun:\nPhew, you survived, `{0}`".format(user)
			self.bot.bangStats[userid]['cStreak'] += 1
			#Checks whether this is your longest streak
			if self.bot.bangStats[userid]['cStreak'] > self.bot.bangStats[userid]['lStreak']:
				self.bot.bangStats[userid]['lStreak'] = self.bot.bangStats[userid]['cStreak']
				txt += "\nYou beat your longest streak! You are now at `{0}`!".format(str(self.bot.bangStats[userid]['cStreak']))

				#checks whether you can go on the leaderboard
				if self.bot.bangStats[userid]['lStreak'] > bangStats["leaderboard"][-1][1]:
					i = 0
					while i < len(self.bot.bangStats["leaderboard"]):
						if self.bot.bangStats["leaderboard"][i][1] > self.bot.bangStats[userid]['lStreak']:
							i += 1
						else:
							break
					for user in self.bot.bangStats["leaderboard"]:
						if user[0] == userid:
							self.bot.bangStats["leaderboard"].pop(bangStats["leaderboard"].index(user))

					self.bot.bangStats["leaderboard"].insert(i,(userid, bangStats[userid]['lStreak']))
		else:
			#You're dead...
			txt = ":dizzy_face::boom::gun:\nOh dear. You're dead, `{0}`. Your streak was: `{1}`!".format(user, str(self.bot.bangStats[userid]['cStreak']))
			self.bot.bangStats[userid]['kill'] += 1
			self.bot.bangStats[userid]['cStreak'] = 0
		self.bot.bangStats[userid]['play'] += 1
		msg = await self.bot.say(txt)
		self.bot.bangCheck[userid] = False

		#Saves the results
		with open('ang (copy).json','w') as fp:
			json.dump(self.bot.bangStats, fp)

	#Bang stats
	@ang.command(name='stats', pass_context = True)
	async def bangstats(self, ctx, *, user:discord.User = None):
		if not user:
			user = ctx.message.author
		userid = str(user.id)
		user = str(user)
		if userid in self.bot.bangStats:
				txt = "Stats for `" + str(user) + "`\nTimes Played: `" + str(self.bot.bangStats[userid]['play']) + "`\nTimes Killed: `" + str(self.bot.bangStats[userid]["kill"]) + "`"
				if self.bot.bangStats[userid]["kill"] != 0:
					txt += "\nW/L Ratio: `" + str(round((self.bot.bangStats[userid]["play"]-self.bot.bangStats[userid]["kill"])/self.bot.bangStats[userid]["kill"],2)) + "`:`1`"
				else:
					txt += "\nW/L Ratio: `∞:∞`"
				txt += "\nLongest Streak: `" + str(self.bot.bangStats[userid]["lStreak"]) + "`\nCurrent Streak: `" + str(self.bot.bangStats[userid]["cStreak"]) + "`"
				await self.bot.say(txt)
		else:
			await self.bot.say("No profile for " + str(user) + "! Play the game to get one.")

	#Bang leaderboard
	@ang.command(name='leaderboard')
	async def bangleaderboard(self):

		msg = await self.bot.say("`Getting leaderboard...`")

		txt = "```"
		i = 0
		#the reason this take so long is that the bot is retrieving the info of everyone on the list
		#This is highly rate-limited but useful in case someone changes their name
		while i < 10:
			place = self.bot.bangStats["leaderboard"][i]
			user = await self.bot.get_user_info(place[0])
			txt += str(i+1) + ": " + str(user) + " " + str(place[1]) + "\n"
			i += 1
		txt += "```"

		await self.bot.edit_message(msg,txt)


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

		#Checks whether a game is already playing
		if ctx.message.channel in self.bot.hangCheck:
			await self.bot.say("Game already running in this channel! (it expires in less than 5 minutes)")
			return

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
			await self.bot.say("Error, Commands not found: `{0}`".format("`, `".join(list(map(lambda command: secrets.clean(command), sub))))) #invisible space here
			return

		self.bot.hangCheck[ctx.message.channel] = True

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
			await self.bot.say("`" + "`\n`".join(commands) + "`")
		await self.bot.say('''```{0}
 O
/|\\
/ \\
You have to help me before they finish the construction of the gallows!\n```'''.format(choice(secrets.hangReasons)))
		while divider in wordGuess and guesses < 10:
			if tellMsg is not None:
				hangStr = ('''```Guess using letters or words within "''' + sep + '''" i.e. ''' + sep + "e" + sep +
				'''. Type quit to exit the game. ''' +
				secrets.hangedmen[guesses] + ''.join(wordGuess) + '\n' +
str(10 - guesses) + ' guesses remaining.\n' +
"Correct Guesses: " + ", ".join(correct) + "\n" +
"Incorrect Guesses: " + ", ".join(incorrect) + "```")
				if tellMsg != False:
					hangStr += "\n`" + tellMsg + "`"
				await self.bot.say(hangStr)

			def check(msg):
				return not msg.author.bot
			if not coop:
				msg = await self.bot.wait_for_message(timeout = 300, author = player, channel = ctx.message.channel)
			else:
				msg = await self.bot.wait_for_message(timeout = 300, channel = ctx.message.channel, check = check)

			if not msg:
				await self.bot.say("Error: Hangman game timed out.")
				del self.bot.hangCheck[ctx.message.channel]
				return
			m = re.search(sep +"([a-zA-Z]*)" + sep,msg.content)
			if m:
				guess = m.group(1).lower()
				if not guess.isalpha():
					await self.bot.say("Alphabetic characters only!")
				elif len(guess) == 1:
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
				await self.bot.say("Quitting game")
				del self.bot.hangCheck[ctx.message.channel]
				return
			else:
				tellMsg = None
		if guesses == 10:
			x = "Ran out of guesses! Justice is served. The word was " + originalWord
			stick = secrets.hangedmen[10]
		else:
			x = "Congratulations, you saved the life of a dangerous criminal! But at least you won right?"
			stick = '''\\O/
 |
/ \\
'''
		await self.bot.say("```" + stick + ''.join(wordGuess) + '\n' +
"Correct Guesses: " + ", ".join(correct) + "\n" +
"Incorrect Guesses: " + ", ".join(incorrect) + "```" + "\n`" + x + "`")

		del self.bot.hangCheck[ctx.message.channel]

	@commands.command(pass_context = True, aliases=["mine","minesweeper","ms"])
	async def oom(self, ctx):
		'''b.oom
- Plays a classic game of Minesweeper
- Warning, this game requires reactions'''

		size = 9
		mineNum = 12

		#This is from my class imported from boom.py
		field = minefield(size, mineNum)

		msg = await self.bot.say("Setting Up Game!")

		emojiList = ["left2","left","right","right2","up2","up","down","down2", "spades", "flag", "stop"]

		emojiDict = {"left2":"\u23EA","left":"\u25C0","right":"\u25B6","right2":"\u23E9",
		"up":"\U0001F53C","up2":"\u23EB","down":"\U0001F53D","down2":"\u23EC",
		"spades":"\U0001F5A4", "flag":"\U0001F3F3", "square":"\u2B1B", "stop":"\U0001F6D1",
		"0":"0⃣", "1":"1⃣", "2":"2⃣", "3":"3⃣", "4":"4⃣", "5":"5⃣", "6":"6⃣", "7":"7⃣", "8":"8⃣",
		"F":"\U0001F3F3", "B":"\u2B1B", "M":"💥", "selectSquare":"\U0001F533", "selectFlag":"🚩", "stopButton":"⏹"}

		for emoji in emojiList:
			await self.bot.add_reaction(msg, emojiDict[emoji])

		embed = discord.Embed(title = str(ctx.message.author) + "'s Minesweeper Game.")
		cood = [4,4]
		printField = field.simpleField()
		printField[cood[0]][cood[1]] = "selectSquare" if printField[cood[0]][cood[1]] == "B" else ("selectFlag" if printField[cood[0]][cood[1]] == "F" else "stopButton")
		embed.add_field(name = "​", value = "\n".join(list(map(lambda row: "".join(list(map(lambda space: emojiDict[space], row))), printField))))

		playing = True
		while field.checkGame() == "playing":

			await self.bot.edit_message(msg, new_content = " ", embed = embed)

			reaction = (await self.bot.wait_for_reaction(list(map(lambda emoji: emojiDict[emoji], emojiList)), timeout = 100, user = ctx.message.author, message=msg))

			if not reaction:
				await self.bot.edit_message(new_content = "Error: Minesweeper game timed out.")
				return
			reaction = reaction.reaction.emoji

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
			cood = list(map(lambda co: 0 if co < 0 else size-1 if co > size-1 else co , cood))

			await self.bot.remove_reaction(msg, reaction, ctx.message.author)

			printField = field.simpleField()
			printField[cood[0]][cood[1]] = "selectSquare" if printField[cood[0]][cood[1]] == "B" else ("selectFlag" if printField[cood[0]][cood[1]] == "F" else "stopButton")
			embed.set_field_at(0, name = "​", value = "\n".join(list(map(lambda row: "".join(list(map(lambda space: emojiDict[space], row))), printField))))

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
	bot.add_cog(Games(bot))
