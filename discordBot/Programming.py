import discord
from discord.ext import commands
import bounce
from bf import *
import secrets
import json

class Programming():
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def source(self):
		'''source
- A link to the source code of this bot'''
		await self.bot.say("This bot was programmed using discordpy. Nearly all the source code can be found at https://github.com/GuyJoKing/BeeBot")


	@commands.command()
	async def changelog(self):
		'''changelog
- The changelog of the bot'''

		embed = discord.Embed(title="ChangeLog")

		with open('changelog.json','r') as fp:
			changeLog = json.load(fp)
			fp.close()

		for change in changeLog['versions']:
			embed.add_field(name="V"+change, value="\n".join(changeLog[change]))

		await self.bot.say(embed=embed)

	#bf
	@commands.command(pass_context = True, aliases = ["brainfuck", "rainfuck", "bf"])
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
			await self.bot.say("bf, more commonly known as brainfuck, is an esotoric programming language designed to be tough to use. Type b.help bf for more information.")
		elif len(list(filter(lambda x: x in ["+","-","<",">",".",",","[","]"], list(inp[0])))) == 0:
			await self.bot.say("Error: No bf code. Type b.help bf for more information")
		else:
			info = await BFinterpreter(list(filter(lambda x: x in ["+","-","<",">",".",",","[","]"], list(inp[0]))), list("".join(inp[1:])))
			if info['instructions'] == info['instructionLimit']:
				await self.bot.say("Sorry, your code went over the 3 million instruction limit. It's likely you had an infinite loop somewhere.")
			else:
				if len(info['out']) < 2000-6:
					channel = ctx.message.channel
					if len(info['out']) == 0:
						await self.bot.say("No output")
					else:
						await self.bot.say('```' + info['out'] + '```')
				else:
					channel = ctx.message.author
					if not ctx.message.channel.is_private:
						await self.bot.say("Your code went over Discord's 2000 character limit, so the output has been DM'd to you.")
					while info['out']:
						if len(info['out']) > 1900:
							await self.bot.send_message(ctx.message.author, "```" + secrets.clean(info['out'][:1900]) + "```")
							info['out'] = info['out'][1900:]
						else:
							await self.bot.send_message(ctx.message.author, "```" + info['out'] + "```")
							info['out'] = ""
				post = "\nInstructions: `" + str(info['instructions']) + "`"
				post += "\nLoops: `" + str(info['loops']) + "`"
				post += "\nTime Taken: `" + str(math.ceil(info['time']*1000)) + "`ms"
				if info['negativeNum']:
					post += "\nWrapping: `True`"
				if info['negativeCell']:
					post += "\nNegative Cells: True"
				await self.bot.send_message(channel, post)


    #Bounce
	@commands.command(aliases = ['bounce'])
	async def ounce(self, *, code):
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
                        await self.bot.say('```Output:\n' + secrets.clean(str(diction["output"]))
                                           + "\n\nInstructions executed: " + str(diction["executed"])
                                           + "\nBounces: " + str(diction["bounces"]) + "```")
                else:
                        await self.bot.say("```Error: " + str(diction['reason'])
                                           + "\nLine: " + str(diction['line'])
                                           + "\nPointer: " + str(diction['pointer']) + "```")

def setup(bot):
	bot.add_cog(Programming(bot))
