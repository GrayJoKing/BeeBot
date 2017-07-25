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
import asyncio

#Info
import re
from difflib import SequenceMatcher
def similar(a,b):
	print(a,b)
	return SequenceMatcher(None,a.lower(),b.lower()).ratio()

#stats
from functools import reduce

def searchUsers(guild, name):
	prob = [None,0]
	for user in guild.members:
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
	async def uptime(self, ctx):
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

		await ctx.send("I have been flying for " + ", ".join(allTime) + "!")

	def getCogList(self,cog):
		helpList = []
		for command in self.bot.get_cog_commands(cog):
			#Checks if the commands is under the cog, whether it has a docstring, and whether it is an alias of an already listed command
			if command.help:
				#Appends the shortened docstring (i.e. the first line) to the helpList
				helpList.append(command.short_doc)
		return "\n".join(helpList)

	##Cmds
	#REMINDER: CHANGE "arrow_back" to a home emoji
	@commands.command(aliases = ["commands"])
	async def cmds(self, ctx):
		'''cmds
- Shows you an interactive list of commands'''

		#Emoji dictionary
		emojiDict = {"Basic":"\U0001F1E7","Games":"\U0001F1EC","Fun":"\U0001F1EB",
				"Random":"\U0001F1F7","Development":"\U0001F1E9", "Mod":"🇲", "Programming":"🇵",
				"home":"🔤", "help":"❓"}
		#This helps define what order the emojis will be reacted in, as well as making wait_for_reaction shorter
		#I don't use the dictionary cause it is in random order
		emojiList = ["home","Basic","Mod","Random","Games","Fun","Programming","Development","help"]

		#Checks if the bot is able to clear reactions/remove other people's reactions
		#This will be to provide a better cmds function if it is a DM, but it is not implemented yet
		reactionCheck = await ctx.message.clear_reactions()

		#Adds a Bee to the message that called it
		await ctx.message.add_reaction("\U0001F41D")

		user = ctx.message.author
		msg = await ctx.send('''```Remember that you have to prefix commands by "b."
Use reactions to navigate the menu (or if you can't, use b.help <category>):
	- Basic
	- Mod
	- Random
	- Games
	- Fun
	- Programming
	- Development```''')

		#Adds all the reactions in emojiList
		for emoji in emojiList:
			await msg.add_reaction(emojiDict[emoji])

		while True:
			#Waits for a reaction from the user from the emojiList
			#Not sure whether to make this open to everyone, as that may provoke unhelpful spamming

			def check(reaction, usr):
				return reaction.message.id == msg.id and usr.id == user.id and reaction.emoji in list(map(lambda emoji: emojiDict[emoji], emojiList))

			reaction = (await self.bot.wait_for('reaction_add', check=check))[0]

			res = reaction.emoji

			#Removes the reaction the user just made
			await msg.remove_reaction(res, user)
			#Checks which emoji it is and displays the appropriate message
			if res == emojiDict["home"]:
				await msg.edit(content = '''```Remember that you have to prefix commands by "b."
Use reactions to navigate the menu (or if you can't, use b.help <category>):
	- Basic
	- Mod
	- Random
	- Games
	- Fun
	- Programming
	- Development```''')
			elif res == emojiDict["help"]:
				await msg.edit(content = '''```Help:
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
						await msg.edit(content = "```{0}:\nMake sure to prefix each command with 'b.'\nUse b.help <command> to get more info on a command:\n\n{1}```".format(emoji, self.getCogList(emoji)))

	##Ping
	@commands.command()
	async def ping(self, ctx):
		'''ping
- Replies "Pong!" with the ping of the bot'''
		#Gets the time before the message
		start = time.time()
		#Says the message
		msg = await ctx.send("Pong!")
		#Gets the time after the message
		end = time.time()
		#Edits the message to say how long it took to post
		await msg.edit(content="Pong! {}ms".format(str(math.ceil((end-start)*1000))))
		##This may be inaccurate if the bot disconnects and reconnects halfway through or it is in the middle of being rate-limited

	##Help {command}
	@commands.command()
	async def help(self, ctx, *, command = None):
		'''help <command or category>
- Replies with a description of a command or a category'''
		#If there is no command or the command is me, like b.help me, say some useful info
		if not command:
			await ctx.send('Type a command after b.help or use b.cmds to see a list of commands.')
			return
		#If the command is prefixed by b. (like b.help b.say) remove the b.
		if command[:2] == "b.":
			command = command[2:]

		#Check whether the command is actually a cog
		if self.bot.get_cog(command.capitalize()):
			await ctx.send("```Use b.help <command> to get more info:\n\n{}```".format(self.getCogList(command.capitalize())))
			return

		#Gets the command object by the command name
		command = self.bot.get_command(command.lower())
		#If there is no command named that or the commands has no docstring
		if not command or not command.help:
			await ctx.send('No command or category of that name found')
			return
		#Else, print the command docstring
		await ctx.send("```{}```".format(command.help))


	##Invite
	##REMEMBER: Get invite of support guild
	@commands.command()
	async def invite(self, ctx):
		'''invite
- Lets you invite Bee to your own guild!'''
		#Creates an embed with a linked title as an invite
		perms = discord.Permissions()
		perms.administrator = True
		embed = discord.Embed(title = "Click to invite me to your guild!", url = discord.utils.oauth_url(self.bot.user.id, permissions = perms), colour=discord.Colour.gold())
		embed.add_field(name = "Info:", value = "BeeBot is a fun bot with a wide range of uses. It has mod tools, basic commands, and most importantly... games! Play Cards Against Humanity, Russian Roulette, Minesweeper, Hangman and more!\n\nWarning: BeeBot is in a beta stage and may not work all the time. Any commands in the Development section are being tested and may not work properly. Also, the bot may not be up 100% of the time due to being hosted on an old laptop.")
		embed.add_field(name = "Join the support guild where you can play with a commands in development or suggest new commands!", value = "discord.gg/Qwgw2N3", inline = False)

		await ctx.send(embed=embed)

	#Credits
	@commands.command()
	async def credits(self, ctx):
		'''credits
	- Returns a list of the credits of this bot'''
		await ctx.send('''```
DryJoKing#6414 for creating me
Rapptz's discord.py for providing the framework
Jack#0305 for inspiring Jo
MiloDiazzo#4163 for installing the brakes
And you, the user, for inviting me to your guild and using me!```''')

	##Search
	##REMEMBER: Find out why some search terms fail consistently ???games??? why???
	@commands.command(aliases = ['google','ing'])
	async def search(self, ctx, *, term):
		'''search <term>
- Searches Google for your search term'''
		service = build("customsearch", "v1",
			developerKey = secrets.googleAPIkey)

		#Searches for the term using the google API
		res = service.cse().list(
			q=term,
			cx='018014882124522379482:xpnc40-ziuq', #probably shouldn't have this here
			).execute()

		#Creates an embed with the title as a link to the website, and a description underneath from the API
		embed = discord.Embed(title=res['items'][0]['title'],
					  url = res['items'][0]['formattedUrl'],
					  description = res['items'][0]['snippet'].replace("\n"," "))
		#Give 2 extra links in case the first wasn't the right one
		embed.add_field(name="See Also:", value = res['items'][1]['formattedUrl'] + "\n" + res['items'][2]['formattedUrl'])

		await ctx.send(embed=embed)

	#Youtube
	@commands.command(aliases=["youtube","video"])
	async def yt(self, ctx, *, search=""):
		'''yt [<term>]
- Retrieves a youtube video from the search term
- Or gives you a popular video if no search term is given'''
		#Checks if a search term was given
		if search:
			msg = await ctx.send("Getting a video for: `" + secrets.clean(search) + "`")
		else:
			msg = await ctx.send("Getting a popular video!")

		query_string = urllib.parse.urlencode({"search_query" : search})

		async with aiohttp.get("http://www.youtube.com/results?" + query_string) as r:
			if r.status == 200:
				html_content = await r.text()
				vids = re.findall(r'href=\"\/watch\?v=(.{11})',html_content)
				if not vids:
					await msg.edit(content ="No videos were found.")
					return
				url = "https://youtu.be/" + vids[0]
			else:
				await msg.edit(content="Error while getting video.")
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
				await msg.edit(content="Error while getting video.")
				return

		embed = discord.Embed(title = "Info")
		embed.add_field(name = "Views:", value = views, inline = False)
		embed.add_field(name = "👍", value = likes).add_field(name = "👎", value = dislikes)

		#Says the url to get discord to post their embed, as you can't post videos in an embed
		await ctx.send(url)
		#Then posts the embed with all the info
		await ctx.send(embed = embed)

		#Deletes the "Getting video" message
		await msg.delete()

	#info
	@commands.command()
	async def info(self, ctx, *, item = '' ):
		'''info [<user>|<emoji>|"me"|"guild"|<channel>]
- Shows info about a multitude of things
Commands:
- No Command
	- Displays info about BeeBot
- <user>
	- Displays info about the user
	- The search function on this is a bit wonky
- Emoji or <emoji>
	- Displays info about the guild's custom emojis or a specific one
	- Shortcut: b.emoji [<emoji>]
- Me
	- Displays info about you
	- Shortcut: b.me
- guild
	- Displays info about this server
	- Shortcut: b.server
- Channel or <channel>
	- Displays info about the channel you are currently on or one specified
	- Shortcut: b.channel [<channel>]'''

		itemType = re.match(r'<(@!?|#|:[a-zA-Z0-9]+:)([0-9]+)>$', item)

		if itemType:
			itemID = itemType.group(2)
			itemType = itemType.group(1)
			print(itemType, itemID)
			if itemType == "@" or itemType == "@!":
				await self.userInfo(ctx.message.guild.get_member(itemID))
			elif itemType == "#":
				await self.channelInfo(itemID)
			else:
				await self.emojiInfo(ctx.message.guild, itemID)
		elif item.lower() == "channel":
			ctx.invoke(command="channel")
		elif item.lower() == "server":
			ctx.invoke(command="server")
		elif item.lower() == "me":
			ctx.invoke(command="me")
		elif item.lower() == "emoji":
			ctx.invoke(command="emoji")
		elif item == "":
			ctx.invoke(command="invite")
		else:
			user = ctx.message.guild.get_member_named(item)
			if not user:
				user, prob = searchUsers(ctx.message.guild, item)
				await self.userInfo(ctx, user, prob, item)
				return
			ctx.invoke(command="user", user=user)

	#Aliases for the info commands
	@commands.command()
	async def me(self, ctx):
		ctx.invoke(command="userInfo")

	@commands.command()
	async def server(self, ctx):
		guild = ctx.message.guild
		embed = discord.Embed(title = guild.name, colour = discord.Colour.gold())
		#Sets the thumbnail to that of the guild's
		if guild.icon_url:
			embed.set_thumbnail(url=guild.icon_url)
		#ID, creation time, the guild region, owner and security level
		embed.add_field(name="ID", value=guild.id)
		embed.add_field(name="Created at", value=str(guild.created_at)[:-7])
		embed.add_field(name="Server Region", value=str(guild.region).capitalize(), inline = False)
		embed.add_field(name="Owner", value=str(guild.owner.display_name), inline = False)
		embed.add_field(name="Security Level", value=str(guild.verification_level).capitalize())

		#Goes through the list of roles and posts those that have administrator, manage_messages, kick_members and/or ban_members permissions and are also displayed seperately
		modRoles = list(map(lambda role: role.mention, list(filter(lambda role: (role.permissions.manage_messages or role.permissions.kick_members or role.permissions.ban_members or role.permissions.administrator) and role.hoist, guild.roles))))
		if len(modRoles) != 0:
			embed.add_field(name="Moderator Roles", value=", ".join(modRoles))

		#Gets the status of every member
		memberStatus = {"offline":0, "dnd": 0, "idle":0, "online":0}
		for member in guild.members:
			memberStatus[str(member.status)] += 1

		#Posts the number of members as well as the memberStatus
		embed.add_field(name="Number of Members: " + str(guild.member_count), value= "\n" + "  ".join(list(map(lambda status: status.capitalize() + ": " + str(memberStatus[status]), memberStatus))), inline = False)
		#Number of text channels
		embed.add_field(name="Number of Text Channels", value=str(len(guild.text_channels)))
		#Number of voice channels
		embed.add_field(name="Number of Voice Channels", value=str(len(guild.voice_channels)))

		#All the Custon emojis of the guild
		if guild.emojis:
			#embed.add_field(name="Custom Emoji", value=", ".join(list(map(lambda emoji: str(emoji), guild.emojis))))
			embed.add_field(name="Custom Emoji", value=len(list(map(str, guild.emojis))))

		await ctx.send(embed=embed)

	@commands.command()
	async def channel(self, ctx, channel:discord.TextChannel = None):
		if not channel:
			channel = ctx.message.channel

		#If no channel is mentioned, use this channel

		embed = discord.Embed(title = channel.name, colour = discord.Colour.gold())
		#ID, Creation date, topic if there is one, it's position in the channel list
		embed.add_field(name = "ID", value = channel.id, inline=False)
		embed.add_field(name = "Created at", value = channel.created_at, inline=False)
		embed.add_field(name = "Topic", value = channel.topic if channel.topic else "None", inline=False)
		embed.add_field(name = "Channel List Position", value = str(channel.position), inline=False)

		await ctx.send(embed=embed)

	@commands.command()
	async def emoji(self, ctx):
		guild = ctx.message.guild

		if id and False:
			emoji = list(filter(lambda emoji: emoji.id == id, guild.emojis))
			if len(emoji) == 0:
				await ctx.send("Error: Unknown Emoji")
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
			embed = discord.Embed(title = guild.name + "'s Custom Emojis")
			for emoji in guild.emojis:
				embed.add_field(name=emoji.name, value = str(emoji))

		await ctx.send(embed=embed)

	@commands.command()
	async def userinfo(self, ctx, user:discord.Member=None):
		if not user:
			user = ctx.message.author

		#Creates the embed, where the title is the user's name+discriminator and the colour is the user's actual displayed role colour
		embed = discord.Embed(title = str(user), color = user.colour)

		#Checks whether the user has a custom avatar and sets it to the embed image and thumbnail
		if user.avatar:
			embed.set_image(url = user.avatar_url).set_thumbnail(url = user.avatar_url)
		#Else use the default
		else:
			embed.set_image(url = user.default_avatar_url).set_thumbnail(url = user.default_avatar_url)

		#Adds ID, Creation date, guild join date, name, nickname in guild, highest role in guild
		embed.add_field(name="ID:", value=user.id, inline=False)
		embed.add_field(name="Creation Date:", value=str(user.created_at)[:-7])
		embed.add_field(name="Server Join Date:", value=str(user.joined_at)[:-7])
		embed.add_field(name="Name:", value=str(user))
		embed.add_field(name="Nickname:", value=user.nick)
		embed.add_field(name="Highest Role:", value=user.top_role)

		#The user perms in the guild
		obj = user.guild_permissions
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

		await ctx.send(embed=embed)

	@commands.command()
	async def calc(self, ctx, *message):
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
			await ctx.send("I think it's...`2`? Umm, maybe `3`? Let me double-check.")
			await asyncio.sleep(3)
			await ctx.send("Yeah yeah, it's `2`, got it.")
		elif msg == "42":
			await ctx.send("The question is `six times nine`!")
		elif msg == "69":
			await ctx.send("lol, it's a `sex thing`.")
		else:
			#Uses my Calc function in calc.py to interpret the calculation and return an answer
			answer = str(calc.calcFunc(msg))
			if "error" in answer:
				#Need to make a better error finder
				await ctx.send(answer)
			else:
				await ctx.send("The answer is `" + str(answer) + "`!")

	@commands.command(pass_context = True, aliases = ['bug'])
	async def ug(self, ctx):
		'''b.ug
Reports bugs to the creator of this bot. Please append a short description of the bug.
This command will also send an invite to the developer to inspect the bug.
Warning: Anyone who is deemed to be abusing this will be blacklisted from its use.'''

		await ctx.send("Please write a comprehensive description of the bug. Type `Cancel` to cancel this. If the bug is in this bug reporting feature or something similar, please visit the support guild at `{}`".format(secrets.noPreview(secrets.supportServerInvite)))


		def check(msg):
			return msg.author == ctx.message.author and msg.channel == ctx.message.channel

		msg = await self.bot.wait_for('message', check=check)

		if msg.content.lower() == "cancel":
			await ctx.send("Bug report cancelled.")
			return
		description = msg.content

		await self.bot.get_channel(secrets.bugChannelID).send(secrets.noPreview(secrets.clean(
'''```USER:{0}
guild: {1}
CHANNEL: {2}
DESCRIPTION: {3}
INVITE: {4}
```'''.format(ctx.message.author, ctx.message.guild, ctx.message.channel, description, (await ctx.message.channel.create_invite(reason="A bug was reported in your server")).url))))

		await ctx.send("Thank you for your report!")


	@commands.command()
	async def stats(self, ctx):
		'''stats
Shows stats about the bot'''
		embed = discord.Embed(title="Stats")
		embed.add_field(name="guilds:", value = str(len(self.bot.guilds)-1))
		embed.add_field(name="Channels:", value = str(reduce(lambda x,y: x+y, list(map(lambda guild: len(guild.channels), self.bot.guilds)))))
		embed.add_field(name="Members:", value = str(reduce(lambda x,y: x+y, list(map(lambda guild: len(guild.members), self.bot.guilds)))))
		await ctx.send(embed=embed)

	##Image
	##REMEMBER: Find out why some search terms fail consistently ???games??? why???
	@commands.command()
	async def image(self, ctx, *, term):
		'''image <term>
- Searches Google images for your search term'''
		service = build("customsearch", "v1",
			developerKey = secrets.googleAPIkey)

		#Searches for the term using the google API
		res = service.cse().list(
			q=term,
			cx='018014882124522379482:xpnc40-ziuq',
			searchType = "image",
			safe = "high"
			).execute()

		await ctx.send(res['items'][0]['link'])
		return

		#Creates an embed with the title as a link to the website, and a description underneath from the API
		embed = discord.Embed(title=res['items'][0]['title'],
					  url = res['items'][0]['formattedUrl'],
					  description = res['items'][0]['snippet'].replace("\n"," "))
		#Give 2 extra links in case the first wasn't the right one
		embed.add_field(name="See Also:", value = res['items'][1]['formattedUrl'] + "\n" + res['items'][2]['formattedUrl'])

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Basic(bot))
