import discord
from discord.ext import commands
import bounce
from bf import *
import secrets
import json
from math import ceil

class Programming():
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def source(self, ctx):
		'''source
- A link to the source code of this bot'''
		await ctx.send("This bot was programmed using discordpy. Nearly all the source code can be found at https://github.com/GuyJoKing/BeeBot")

	@commands.command()
	async def changelog(self, ctx):
		'''changelog
- The changelog of the bot'''

		embed = discord.Embed(title="ChangeLog")

		with open('changelog.json','r') as fp:
			changeLog = json.load(fp)
			fp.close()

		for change in changeLog['versions']:
			embed.add_field(name="V"+change, value="\n".join(changeLog[change]))

		await ctx.send(embed=embed)

	#bf
	@commands.command(aliases = ["brainfuck", "rainfuck", "bf"])
	async def f(self, ctx, *, inp):
		'''b.f <code>!<input>
- Runs a segment of brainfuck code
- Brainfuck is an esotoric programming language with only 8 characters
	- Imagine a line of 0s stretching into the distance
	- And an arrow pointing to one of those 0s
	- `>` will move the arrow one space to the left
	- `<` will move it to the right
	- `+` will add one to the current number
	- `-` will subtract one from the number
	- `,` will take input from the user
	- `.` will print out the current number in ASCII format
	- `[` If the current cell is a 0, skip forward to the matching `]`
	- `]` if the current cell is not a 0 skip backwards to the matching `[`
- And that's it!
- Technically, this language can simulate everything possible, given enough memory and time'''

		inp = inp.split("!")
		if len(inp) == 0:
			await ctx.send("bf, more commonly known as brainfuck, is an esotoric programming language designed to be tough to use. Type b.help bf for more information.")
		elif len(list(filter(lambda x: x in ["+","-","<",">",".",",","[","]"], list(inp[0])))) == 0:
			await ctx.send("Error: No bf code. Type b.help bf for more information")
		else:
			info = await BFinterpreter(list(filter(lambda x: x in ["+","-","<",">",".",",","[","]"], list(inp[0]))), list("".join(inp[1:])))
			if info['instructions'] == info['instructionLimit']:
				await ctx.send("Sorry, your code went over the 3 million instruction limit. It's likely you had an infinite loop somewhere.")
			else:
				if len(info['out']) < 2000-6:
					channel = ctx.message.channel
					if len(info['out']) == 0:
						await ctx.send("No output")
					else:
						await ctx.send('```' + info['out'] + '```')
				else:
					channel = ctx.message.author.dm_channel
					if not isinstance(ctx.message.channel, discord.DMChannel):
						await ctx.send("Your code went over Discord's 2000 character limit, so the output has been DM'd to you.")
					while info['out']:
						if len(info['out']) > 1900:
							await channel.send("```{}```".format(secrets.clean(info['out'][:1900])))
							info['out'] = info['out'][1900:]
						else:
							await channel.send("```{}```".format(info['out']))
							info['out'] = ""
				post = "\nInstructions: `{}`".format(info['instructions'])
				post += "\nLoops: `{}`".format(info['loops'])
				post += "\nTime Taken: `{}`".format(ceil(info['time']*1000))
				if info['negativeNum']:
					post += "\nWrapping: `True`"
				if info['negativeCell']:
					post += "\nNegative Cells: `True`"
				await channel.send(post)


    #Bounce
	@commands.command(aliases = ['bounce'])
	async def ounce(self, *, code):
		return
		'''b.ounce <`code`> <input>
- Codes with an esotoric programming language I invented!
'''
		test = code.split("```")
		if len(test) == 1:
			test = code.split("`")
			code = test[1]
		if len(test) > 2:
			inp = test[2]
		else:
			inp = ''
		output, diction = bounce.runBounce(code, inp)
		if output == "success":
			await ctx.send('```Output:\n' + secrets.clean(str(diction["output"]))
							+ "\n\nInstructions executed: " + str(diction["executed"])
							+ "\nBounces: " + str(diction["bounces"]) + "```")
		else:
			await ctx.send("```Error: " + str(diction['reason'])
							+ "\nLine: " + str(diction['line'])
							+ "\nPointer: " + str(diction['pointer']) + "```")

def setup(bot):
	bot.add_cog(Programming(bot))
