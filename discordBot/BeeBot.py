 #Debugging stuff
import argparse
parser = argparse.ArgumentParser(description = "BeeBot")
parser.add_argument('-debug', action = 'store_true', help = "Opens the bot in debug mode")
args = parser.parse_args()
debug = args.debug

#Basic stuff you need
import discord
from discord.ext import commands
import logging
logging.basicConfig(level=logging.INFO)
import asyncio

#Secret stuff like bot tokens
import secrets

#Uptime
import time

#Error event
import traceback
import sys
import math

#profilePics
import random
import os

#serverInfo
import json

#Reminders:
##USE ASCIIDOC FOR NICE COLOURED CODE BLOCK
#Install packages with "python -m pip install"
#	install - pillow, colour

#RandomCog is used as in place of random to avoid conflicts
extensions = ["Basic","Randomcog","Mod","Fun","Games","Development", "Programming","Secret_stuff"]

#A debug mode for testing out new features or improving old ones

if debug:
	beePrefixes = ["."]
	print("DEBUG MODE ACTIVATED.\nPREFIX CHANGED TO .")
	print("RUNNING ON DEBUG TOKEN")
else:
	beePrefixes = ["b.","bee.","\U0001F41D."]

startTime = time.time()

while True:
	try:
		bot = commands.Bot(command_prefix=beePrefixes)
		#Removes the default help command so you can put your own
		bot.remove_command('help')

		##Events
		##On member join
		##Welcomes members to the server
		@bot.event
		async def on_member_join(member):
			if bot.serverInfo['welcome']:
				class SafeDict(dict):
					def __missing__(self, key):
						return '{' + key + '}'
				await bot.send_message(member.server, bot.serverInfo['welcome'].format_map(SafeDict(mention=member.mention, name=member.name, servername=member.server.name)))
			##assign role later

		##On member leave
		##Says goodbye to members
		@bot.event
		async def on_member_remove(member):
			if bot.serverInfo['bye']:
				class SafeDict(dict):
					def __missing__(self, key):
						return '{' + key + '}'
				await bot.send_message(member.server, bot.serverInfo['bye'].format_map(SafeDict(name=member.name, servername=member.server.name)))

		##On bot startup
		##Print stuff to cmd line and changes Playing to the command list command
		@bot.event
		async def on_ready():
			print('Logged in as {}'.format(bot.user.name))
			#Sets the startTimeof the bot (for b.uptime)
			bot.startTime = startTime
			await bot.change_presence(game=discord.Game(name=(bot.command_prefix[0] + "cmds")))
			print("Set Game as {}cmds".format(bot.command_prefix[0]))
			try:
				await bot.edit_profile(None, avatar=open("profilePics\\" + random.choice(os.listdir("profilePics\\")), 'rb').read())
				print("Set random profile pic")
			except Exception as e:
				print("FAILED: Profile Pic\n" + str(e))

			with open('serverInfo.json','r') as fp:
				bot.serverInfo = json.load(fp)
				fp.close()

		##checks messages
		@bot.event
		async def on_message(message):

			if debug:
				print(message.content)

			if message.type == discord.MessageType.pins_add:
				pins = await bot.pins_from(message.channel)
				message = pins[0]
				if len(message.clean_content) < 200:
					abridge = message.clean_content
				else:
					abridge = message.clean_content[:200] + "**...**"
				embed = discord.Embed(title = str(message.author) + "'s pinned message.")
				embed.add_field(name = str(message.timestamp[:-7]), value = abridge)
				await bot.send_message(message.channel, embed = embed)
				#await bot.send_message(message.channel, "A message was pinned to this channel. It was by " + str(message.author) + " and said:\n\n" + abridge)

			#Isn't triggered by other bots or itself
			if message.author.bot:
				return

			#This makes every command case-insensitive. Doesn't work on subcommands
			if " " in message.content:
				message.content = message.content[:message.content.index(" ")].lower() + message.content[message.content.index(" "):]
			else:
				message.content = message.content.lower()

			##THIS IS VERY IMPORTANT
			#If this is not run, this event blocks commands from triggering
			#vvvvvv
			await bot.process_commands(message)
			#^^^^^^

		#Is called when a command encounters an error
		@bot.event
		async def on_command_error(exception, ctx):
			if type(exception) == commands.CommandOnCooldown:
				tim = exception.retry_after
				allTime = []
				#Calculates the amount of days
				days = math.floor(tim/(60*60*24))
				#Calculates the amount of hours
				hours = math.floor(tim/3600)%24
				#Gets the amount of minutes
				minutes = math.floor(tim/60)%60
				#Gets the amount of seconds, rounding up
				seconds = math.ceil(tim%60)
				if not days:
					allTime.append("`" + str(days) + "` days")
				if not hours:
					allTime.append("`" + str(hours) + "` hours")
				if not minutes:
					allTime.append("`" + str(minutes) + "` minutes")
				if not seconds:
					allTime.append("`" + str(seconds) + "` seconds")
				await bot.send_message(ctx.message.channel, 'That command is on cooldown. Try again in {}'.format(", ".join(allTime)))
			elif type(exception) != commands.CommandNotFound:
				await bot.send_message(ctx.message.channel, "Error: " + str(exception))
				print(str(exception))
				traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

		@bot.event
		async def on_server_join(server):
			if not debug:
				await bot.send_message(bot.get_channel(secrets.newsChannelID), ":bee: was added to the server `{0}`, with `{1}` members. Yay!".format(server.name, server.member_count-1))
			if server.id not in bot.serverInfo:
				bot.serverInfo[server.id] = {}

		@bot.event
		async def on_server_remove(server):
			if not debug:
				await bot.send_message(bot.get_channel(secrets.newsChannelID), ":bee: was removed from `{0}` or the server was deleted.".format(server.name))


		#Loads all the extensions
		if __name__ == "__main__":
			for extension in extensions:
				try:
					bot.load_extension(extension)
				except Exception as e:
					print("Failed to load " + extension + " because " + str(e))

		#Runs the bot (from my debug token if needed)
		if debug:
			asyncio.get_event_loop().run_until_complete(bot.start(secrets.debugToken))
		else:
			asyncio.get_event_loop().run_until_complete(bot.start(secrets.botToken))
		print("bot ended")
		bot.close()

	except Exception as e:
		print(e)
		try:
			bot.close()
		except:
			pass
	time.sleep(10)
