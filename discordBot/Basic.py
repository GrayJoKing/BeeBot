import discord
from discord.ext import commands

#Uptime, Ping
import time
import math

#Search
from googleapiclient.discovery import build
import secrets

#Youtube
import aiohttp
import urllib

#Calc
import calc

#Info
import re
from difflib import SequenceMatcher
def similar(a,b):
	print(a,b)
	return SequenceMatcher(None,a.lower(),b.lower()).ratio()

#stats
from functools import reduce

def searchUsers(server, name):
	prob = [None,0]
	for user in server.members:
		if similar(name, user.name) > prob[1]:
			prob = (user, similar(name, user.name))
		if user.nick and similar(name, user.nick) > prob[1]:
			prob = (user, similar(name, user.nick))
	return prob[0], prob[1]


class Basic():
	def __init__(self, bot):
		self.bot = bot

	##Uptime
	@commands.command()
	async def uptime(self):
		'''uptime
- Tells you how long the bot has been running for'''
		#Gets the time difference between the start time and the current time
		tim = time.time() - self.bot.startTime
		allTime = []

		#Calculates the amount of days
		days = math.floor(tim/(60*60*24))
		#Calculates the amount of hours
		hours = math.floor(tim/3600)%24
		#Gets the amount of minutes
		minutes = math.floor(tim/60)%60
		#Gets the amount of seconds, rounding up
		seconds = math.ceil(tim%60)
		if days != 0:
			allTime.append("`" + str(days) + "` days")
		if hours != 0:
			allTime.append("`" + str(hours) + "` hours")
		if minutes != 0:
			allTime.append("`" + str(minutes) + "` minutes")
		if seconds != 0:
			allTime.append("`" + str(seconds) + "` seconds")

		await self.bot.say("I have been flying for " + ", ".join(allTime) + "!")

	def getCogList(self,cog):
		helpList = []
		for command in self.bot.commands:
			#Checks if the commands is under the cog, whether it has a docstring, and whether it is an alias of an already listed command
			if self.bot.commands[command].cog_name == cog and self.bot.commands[command].help != None and self.bot.commands[command].short_doc not in helpList:
				#Appends the shortened docstring (i.e. the first line) to the helpList
				helpList.append(self.bot.commands[command].short_doc)
		return "\n".join(helpList)

	##Cmds
	#REMINDER: CHANGE "arrow_back" to a home emoji
	@commands.command(pass_context = True, aliases = ["commands"])
	async def cmds(self, ctx):
		'''cmds
- Shows you an interactive list of commands'''

		#Emoji dictionary
		emojiDict = {"Basic":"\U0001F1E7","Games":"\U0001F1EC","Fun":"\U0001F1EB",
				"Random":"\U0001F1F7","Development":"\U0001F1E9", "Mod":"🇲",
				"home":"🔤", "help":"❓"}
		#This helps define what order the emojis will be reacted in, as well as making wait_for_reaction shorter
		#I don't use the dictionary cause it is in random order
		emojiList = ["home","Basic","Mod","Random","Games","Fun","Development","help"]

		#Checks if the bot is able to clear reactions/remove other people's reactions
		#This will be to provide a better cmds function if it is a DM, but it is not implemented yet
		reactionCheck = await self.bot.clear_reactions(ctx.message) == "Forbidden"

		#Adds a Bee to the message that called it
		await self.bot.add_reaction(ctx.message, "\U0001F41D")

		user = ctx.message.author
		msg = await self.bot.say('''```Remember that you have to prefix commands by "b."
Use reactions to navigate the menu (or if you can't, use b.help <category>):
	- Basic
	- Mod
	- Random
	- Games
	- Fun
	- Development```''')

		#Adds all the reactions in emojiList
		for emoji in emojiList:
			await self.bot.add_reaction(msg, emojiDict[emoji])

		while True:
			#Waits for a reaction from the user from the emojiList
			#Not sure whether to make this open to everyone, as that may provoke unhelpful spamming
			res = await self.bot.wait_for_reaction(list(map(lambda emoji: emojiDict[emoji], emojiList)), timeout=600, message=msg, user=user)
			if not res:
				await self.bot.edit_message(msg, "```Sorry, but this list of commands has timed out. Type b.cmds to get a new one!```")
				return

			res = res.reaction.emoji

			#Removes the reaction the user just made
			await self.bot.remove_reaction(msg, res, user)
			#Checks which emoji it is and displays the appropriate message
			if res == emojiDict["home"]:
				await self.bot.edit_message(msg, '''```Remember that you have to prefix commands by "b."
Use reactions to navigate the menu (or if you can't, use b.help <category>):
	- Basic
	- Mod
	- Random
	- Games
	- Fun
	- Development```''')
			elif res == emojiDict["help"]:
				await self.bot.edit_message(msg, '''```Help:
Note that you do not need to use any of the "" <> [] {} | symbols in the actual command.

"words"     You need to type these words in
<user>      Either a mention of a user (with or without the @) or the nickname of a user
<channel>   A mention of a channel (use a #)
<any word>  Look at the word for a clue to what you need to type

()  A grouping of commands
[]  An optional command
{}  Something that can be repeated 0 or more times
|   This between two or more items means you should type only one of them```''')
			else:
				for emoji in emojiList:
					if res == emojiDict[emoji]:
						#Uses the getCogList function above
						await self.bot.edit_message(msg, "```Make sure to prefix each command with 'b.'\nUse b.help <command> to get more info on a command:\n" + self.getCogList(emoji) + "```")

	##Ping
	@commands.command()
	async def ping(self):
		'''ping
- Replies "Pong!" with the ping of the bot'''
		#Gets the time before the message
		start = time.time()
		#Says the message
		msg = await self.bot.say("Pong!")
		#Gets the time after the message
		end = time.time()
		#Edits the message to say how long it took to post
		await self.bot.edit_message(msg, "Pong! " + str(math.ceil((end-start)*1000)) + "ms")
		##This may be inaccurate if the bot disconnects and reconnects halfway through or it is in the middle of being rate-limited

	#categories
	#Made because of the people who tend to do stuff like "b.random" when told to do b.help random (THERE ARE WAY TOO MANY OF THEM)
	#i don't think this works
	@commands.command(pass_context = True, aliases = ['random','basic','games','game','fun','development'])
	async def asic(self, ctx):
		if ctx.invoked_with == "game":
			ctx.invoked_with = "games"
		elif ctx.invoked_with == "asic":
			ctx.invoked_with = "basic"
		ctx.message.content = "b.help " + ctx.invoked_with
		self.bot.process_commands(ctx.message)

	##Help {command}
	@commands.command()
	async def help(self, *, command = None):
		'''help <command or category>
- Replies with a description of a command or a category'''
		#If there is no command or the command is me, like b.help me, say some useful info
		if not command or command.lower() == "me":
			await self.bot.say('Type a command after b.help or use b.cmds to see a list of commands.')
			return
		#If the command is prefixed by b. (like b.help b.say) remove the b.
		if command[:2] == "b.":
			command = command[2:]

		#Check whether the command is actually a cog
		if command.capitalize() in self.bot.cogs:
			await self.bot.say("```Use b.help <command> to get more info:\n" + self.getCogList(command.capitalize()) + "```")
			return

		#Gets the command object by the command name
		command = self.bot.commands.get(command.lower())
		#If there is no command named that or the commands has no docstring
		if not command or not command.help:
			await self.bot.say('No command or category of that name found')
			return
		#Else, print the command docstring
		await self.bot.say("```" + command.help + "```")


	##Invite
	##REMEMBER: Get invite of support server
	@commands.command()
	async def invite(self):
		'''invite
- Lets you invite Bee to your own server!'''
		#Creates an embed with a linked title as an invite
		perms = discord.Permissions()
		perms.administrator = True
		embed = discord.Embed(title = "Click to invite me to your server!", url = discord.utils.oauth_url(self.bot.user.id, permissions = perms))
		embed.add_field(name = "Info:", value = "BeeBot is a fun bot with a wide range of uses. It has mod tools, basic commands, and most importantly... Games! Play Russian Roulette, Minesweeper, Hangman and more!")
		embed.add_field(name = "Join the support server where you can play with a developmental version or suggest new commands!", value = "discord.gg/Qwgw2N3", inline = False)

		await self.bot.say(embed=embed)

	#Credits
	@commands.command()
	async def credits(self):
		'''credits
	- Returns a list of the credits of this bot'''
		await self.bot.say('''```
DryJoKing#6414 for creating me
Rapptz's discord.py for providing the framework
Jack#0305 for inspiring Jo
MiloDiazzo#4163 for installing the brakes
And you, the user, for inviting me to your server and using me!```''')

	##Search
	##REMEMBER: Find out why some search terms fail consistently ???games??? why???
	@commands.command(aliases = ['google','ing'])
	async def search(self, *, term):
		'''search <term>
- Searches Google for your search term'''
		service = build("customsearch", "v1",
			developerKey = secrets.googleAPIkey)

		#Searches for the term using the google API
		res = service.cse().list(
			q=term,
			cx='018014882124522379482:xpnc40-ziuq',
			).execute()

		#Creates an embed with the title as a link to the website, and a description underneath from the API
		embed = discord.Embed(title=res['items'][0]['title'],
					  url = res['items'][0]['formattedUrl'],
					  description = res['items'][0]['snippet'].replace("\n"," "))
		#Give 2 extra links in case the first wasn't the right one
		embed.add_field(name="See Also:", value = res['items'][1]['formattedUrl'] + "\n" + res['items'][2]['formattedUrl'])

		await self.bot.say(embed=embed)

	#Youtube
	@commands.command(aliases=["youtube","video"], pass_context = True)
	async def yt(self, ctx, *, search=""):
		'''yt [<term>]
- Retrieves a youtube video from the search term
- Or gives you a popular video if no search term is given'''
		#Checks if a search term was given
		if search:
			msg = await self.bot.say("Getting a video for: `" + search.replace("@","@​") + "`") #invisible space
		else:
			msg = await self.bot.say("Getting a popular video!")

		query_string = urllib.parse.urlencode({"search_query" : search})

		async with aiohttp.get("http://www.youtube.com/results?" + query_string) as r:
			if r.status == 200:
				html_content = await r.text()
				url = "https://youtu.be/" + re.findall(r'href=\"\/watch\?v=(.{11})',html_content)[0]
			else:
				await self.bot.edit_message(msg, new_content="Error while getting video.")
				return
		async with aiohttp.get(url) as r:
			if r.status == 200:
				html_content = await r.text()
				title = re.findall('''<span id=\"eow-title\" class=\"watch-title\" dir=\"ltr\" title=\"(.+)\">''',html_content)[0]
				views = re.findall('''<div class="watch-view-count">([,\d]+) views<\/div>''',html_content)[0]
				thumbs = re.findall('''<span class="yt-uix-button-content">([,\d]+)</span>''', html_content)
				likes = thumbs[0]
				dislikes = thumbs[2]

			else:
				await self.bot.edit_message(msg, new_content="Error while getting video.")
				return

		embed = discord.Embed(title = "Info")
		embed.add_field(name = "Views:", value = views, inline = False)
		embed.add_field(name = "Likes:", value = likes).add_field(name = "Dislikes:", value = dislikes)

		#Says the url to get discord to post their embed, as you can't post videos in an embed
		await self.bot.say(url)
		#Then posts the embed with all the info
		await self.bot.say(embed = embed)

		#Deletes the "Getting video" message
		await self.bot.delete_message(msg)

	#info
	@commands.command(pass_context = True)
	async def info(self, ctx, *, item = '' ):
		'''info <command>
- Shows info about a multitude of things
Commands:
- No Command
	- Displays info about BeeBot
- <user>
	- Displays info about the user
- Emoji or <emoji>
	- Displays info about the server's custom emojis or a specific one
	- Shortcut: b.emoji [<emoji>]
- Me
	- Displays info about you
	- Shortcut: b.me
- Server
	- Displays info about this server
	- Shortcut: b.server
- Channel or <channel>
	- Displays info about the channel you are currently on or one specified
	- Shortcut (for this channel only): b.channel [<channel>]'''

		itemType = re.match(r'<(@!?|#|:[a-zA-Z0-9]+:)([0-9]+)>$', item)

		if itemType:
			itemID = itemType.group(2)
			itemType = itemType.group(1)
			print(itemType, itemID)
			if itemType == "@" or itemType == "@!":
				await self.userInfo(ctx.message.server.get_member(itemID))
			elif itemType == "#":
				await self.channelInfo(itemID)
			#Role info. Maybe implemented later
			#elif itemType == "@&":
				#await self.roleInfo(itemID)
			else:
				await self.emojiInfo(ctx.message.server, itemID)
		elif item.lower() == "channel":
			await self.channelInfo(ctx.message.channel.id)
		elif item.lower() == "server":
			await self.serverInfo(ctx.message.server)
		elif item.lower() == "me":
			await self.userInfo(ctx.message.author)
		elif item.lower() == "emoji":
			await self.emojiInfo(ctx.message.server)
		elif item == "":
			await self.beeInfo()
		else:
			user = ctx.message.server.get_member_named(item)
			if not user:
				user, prob = searchUsers(ctx.message.server, item)
				await self.userInfo(user, prob, item)
				return
			await self.userInfo(user)

	#Aliases for the info commands
	@commands.command(pass_context = True)
	async def me(self, ctx):
		await self.userInfo(ctx.message.author)

	@commands.command(pass_context = True)
	async def server(self, ctx):
		await self.serverInfo(ctx.message.server)

	@commands.command(pass_context = True)
	async def channel(self, ctx):
		await self.channelInfo(ctx.message.channel.id)

	@commands.command(pass_context = True)
	async def emoji(self, ctx):
		await self.emojiInfo(ctx.message.server)

	async def serverInfo(self, server):
		embed = discord.Embed(title = str(server), colour = discord.Colour.gold())
		#Sets the thumbnail to that of the server's
		embed.set_thumbnail(url=server.icon_url)
		#ID, creation time, the server region, owner and security level
		embed.add_field(name="ID", value=server.id)
		embed.add_field(name="Created at", value=str(server.created_at)[:-7])
		embed.add_field(name="Server Region", value=str(server.region).capitalize(), inline = False)
		embed.add_field(name="Owner", value=str(server.owner), inline = False)
		embed.add_field(name="Security Level", value=str(server.verification_level).capitalize())

		#Goes through the list of roles and posts those that have administrator, manage_messages, kick_members and/or ban_members permissions and are also displayed seperately
		modRoles = list(map(lambda role: role.mention, list(filter(lambda role: (role.permissions.manage_messages or role.permissions.kick_members or role.permissions.ban_members or role.permissions.administrator) and role.hoist, server.roles))))
		if len(modRoles) != 0:
			embed.add_field(name="Moderator Roles", value=", ".join(modRoles))

		#Gets the status of every member
		memberStatus = {"offline":0, "dnd": 0, "idle":0, "online":0}
		for member in server.members:
			memberStatus[str(member.status)] += 1

		#Posts the number of members as well as the memberStatus
		embed.add_field(name="Number of Members: " + str(server.member_count), value= "\n" + "  ".join(list(map(lambda status: status.capitalize() + ": " + str(memberStatus[status]), memberStatus))), inline = False)
		#Number of text channels
		embed.add_field(name="Number of Text Channels", value=str(len(list(filter(lambda channel: channel.type == discord.ChannelType.text , server.channels)))))
		#Number of voice channels
		embed.add_field(name="Number of Voice Channels", value=str(len(list(filter(lambda channel: channel.type == discord.ChannelType.voice , server.channels)))))

		#All the Custon emojis of the server
		if server.emojis:
			#embed.add_field(name="Custom Emoji", value=", ".join(list(map(lambda emoji: str(emoji), server.emojis))))
			embed.add_field(name="Custom Emoji", value=len(list(map(lambda emoji: str(emoji), server.emojis))))

		await self.bot.say(embed=embed)

	async def userInfo(self, user, prob = None, search = None):
		#Creates the embed, where the title is the user's name+discriminator and the colour is the user's actual displayed role colour
		embed = discord.Embed(title = str(user), color = user.colour)

		#Checks whether the user has a custom avatar and sets it to the embed image and thumbnail
		if user.avatar:
			embed.set_image(url = user.avatar_url).set_thumbnail(url = user.avatar_url)
		#Else use the default
		else:
			embed.set_image(url = user.default_avatar_url).set_thumbnail(url = user.default_avatar_url)

		#Adds ID, Creation date, Server join date, name, nickname in server, highest role in server
		embed.add_field(name="ID:", value=user.id, inline=False)
		embed.add_field(name="Creation Date:", value=str(user.created_at)[:-7])
		embed.add_field(name="Server Join Date:", value=str(user.joined_at)[:-7])
		embed.add_field(name="Name:", value=str(user))
		embed.add_field(name="Nickname:", value=user.nick)
		embed.add_field(name="Highest Role:", value=user.top_role)

		#The user perms in the server
		obj = user.server_permissions
		perms=[]
		if obj.administrator:
			perms.append("Server Administrator")
		else:
			if obj.manage_roles:
				perms.append("Manage Roles")
			if obj.kick_members:
				perms.append("Kick Members")
			if obj.ban_members:
				perms.append("Ban Members")
			if obj.manage_messages:
				perms.append("Manage Messages")
			if obj.manage_nicknames:
				perms.append("Manage Nicknames")

		if len(perms) == 0:
			perms = ["None"]
		embed.add_field(name="Server Permissions:", value=", ".join(perms))

		if not prob:
			await self.bot.say(embed=embed)
		else:
			await self.bot.say('"{0}" matched with {1} with a probability of {2}%'.format(search, user.name, prob*100), embed=embed)


	async def emojiInfo(self, server, id = None):
		if id:
			emoji = list(filter(lambda emoji: emoji.id == id, server.emojis))
			if len(emoji) == 0:
				await self.bot.say("Error: Unknown Emoji")
				return
			else:
				emoji = emoji[0]
			#Creates an embed with the title as the emoji name, linked to a picture of the emoji
			embed = discord.Embed(title = emoji.name, url = emoji.url)
			#Sets the thumbnail and image to the emoji
			embed.set_image(url=emoji.url).set_thumbnail(url=emoji.url)
			#ID, creation date
			embed.add_field(name = "ID", value = emoji.id)
			embed.add_field(name = "Created at", value = emoji.created_at)
			#If the emoji is restricted to certain roles, say so
			if emoji.roles:
				embed.add_field(name = "Restricted to", value = ", ".join(list(map(lambda role: role.mention, emoji.roles))))
		else:
			embed = discord.Embed(title = server.name + "'s Custom Emojis")
			for emoji in server.emojis:
				embed.add_field(name=emoji.name, value = str(emoji))

		await self.bot.say(embed=embed)

	async def channelInfo(self, id):
		#If no channel is mentioned, use this channel
		channel = list(filter(lambda channel: channel.id == id, channel.server.channels))
		if len(channel) == 0:
			await self.bot.say("Error: Unknown Channel")
			return
		else:
			channel = channel[0]

		embed = discord.Embed(title = channel.name, colour = discord.Colour.gold())
		#ID, Creation date, topic if there is one, it's position in the channel list
		embed.add_field(name = "ID", value = channel.id, inline=False)
		embed.add_field(name = "Created at", value = channel.created_at, inline=False)
		embed.add_field(name = "Topic", value = channel.topic if channel.topic else "None", inline=False)
		embed.add_field(name = "Channel List Position", value = str(channel.position), inline=False)

		#Gets all the specific perms of the channel
		#Probably doesn't work
		#Didn't work :(
		# roleOverwrites = []
		# userOverwrites = []
		# for overwrite in channel._permission_overwrites:
		#		 if type(overwrite[0]) == discord.Role:
		#				 roleOverwrites.append(overwrite)
		#		 else:
		#				 userOverwrites.append(overwrite)
				#
		# embed.add_field(name = "Role Permissions", value = "\n\n".join(list(map(lambda overwrite: overwrite[0].mention + ":\n".join(map(lambda pair: pair[0] + ": " + pair[1], iter(overwrite[1])), roleOverwrites)))))
				#
		# embed.add_field(name = "User Permissions", value = "\n\n".join(list(map(lambda overwrite: overwrite[0].mention + ":\n".join(map(lambda pair: pair[0] + ": " + pair[1], iter(overwrite[1])), userOverwrites)))))

		await self.bot.say(embed = embed)

	async def beeInfo(self):
		#edit this
		await self.bot.say("Testing")


	@commands.command()
	async def calc(self, *message):
		'''calc <expression>
- Returns the result from a calculation
- Special characters are:
	- + to add, - to subtract
	- x, * to multiply, / to divide
	- ^ to raise to the power
	- () as grouping
	- sqrt() to get square root of number
	- cbrt() to get cube root of number
	- trig functions, such as sin(), cos(), tan(), csc(), sec(), cot(), asin(), acos(), atan()
	- constants pi and e
WARNING:
There are still some issues with this. Imaginary numbers render weirdly.'''

		#Removes spaces
		msg = "".join(message)

		#Some humorous expressions
		if msg == "1+1":
			await self.bot.say("I think it's...`2`? Umm, maybe `3`? Let me double-check.")
			await asyncio.sleep(3)
			await self.bot.say("Yeah yeah, it's `2`, got it.")
		elif msg == "42":
			await self.bot.say("The question is `six times nine`!")
		elif msg == "69":
			await self.bot.say("lol, it's a `sex thing`.")
		else:
			#Uses my Calc function in calc.py to interpret the calculation and return an answer
			answer = str(calc.calcFunc(msg))
			if "error" in answer:
				#Need to make a better error finder
				await self.bot.say(answer)
			else:
				await self.bot.say("The answer is `" + str(answer) + "`!")

	@commands.command()
	async def ug(self, *, description = ''):
		return
		'''b.ug <description>
Reports bugs to the creator of this bot. Please append a short description of the bug.
This command will also record the contents of the last 10 messages in your channel.
Warning: Anyone who is deemed to be abusing this will be blacklisted from its use.'''

	@commands.command()
	async def stats(self):
		'''stats
Shows stats about the bot'''
		await self.bot.say('''Guilds: {0}
Channels: {1}
Members: {2}'''.format(len(self.bot.servers), reduce(lambda x,y: x+y, list(map(lambda server: len(server.channels), self.bot.servers))), reduce(lambda x,y: x+y, list(map(lambda server: len(server.members), self.bot.servers)))))

def setup(bot):
	bot.add_cog(Basic(bot))
