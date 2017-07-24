import sys
import time
import asyncio

async def BFinterpreter(c, inp):
	#Assumes c is already sanitised and both c and inp are lists of chars

	instructionLimit = 3000000

	instructionLimit = 10000000
	instructions = 0
	loops = 0
	out = ""
	negativeCell = False
	negativeNum = False

	cells = [0]
	cellPointer = 0

	cPointer = 0
	start = time.time()

	while cPointer < len(c) and instructions != instructionLimit:
		if c[cPointer] == "+":
			cells[cellPointer] = (cells[cellPointer] + 1)%256
		elif c[cPointer] == "-":
			if cells[cellPointer] == 0:
				negativeNum = True
			cells[cellPointer] = (cells[cellPointer] - 1)%256
		elif c[cPointer] == ".":
			out += chr(cells[cellPointer])
		elif c[cPointer] == ",":
			if inp:
				cells[cellPointer] = ord(inp[0])%256
				inp = inp[1:]
			else:
				cells[cellPointer] = 0
		elif c[cPointer] == "<":
			if cellPointer == 0:
				cells.insert(0,0)
				negativeCell = True
			else:
				cellPointer -= 1
		elif c[cPointer] == ">":
			cellPointer += 1
			if cellPointer == len(cells):
				cells.append(0)
		else:
			direction = 0
			if c[cPointer] == "[" and not cells[cellPointer]:
				direction = 1
			elif c[cPointer] == "]" and cells[cellPointer]:
				direction = -1
			if direction:
				loops += 1
				total = direction
				while (total and cPointer != 0 and cPointer != len(c)):
					cPointer += direction
					total += (c[cPointer] == "[") - (c[cPointer] == "]")
				if cPointer == 0:
					cPointer = len(c)
		cPointer += 1
		instructions += 1
		if instructions%1000 == 0:
			await asyncio.sleep(0)

	info = {}
	info['instructionLimit'] = instructionLimit
	info['instructions'] = instructions
	info['loops'] = loops
	info['out'] = out
	info['negativeCell'] = negativeCell
	info['negativeNum'] = negativeNum
	info['time'] = time.time()-start
	return info
