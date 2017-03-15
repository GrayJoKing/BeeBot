import math
import re

precedence = ["○","Δ","√","!","^","/","x","-","+"]
replace = [
("**","^"),
("*","x"),
("[","("),
("]",")"),
("{","("),
("}",")"),
("√","(2)√"),
("!","!(1)"),

("sqrt(","(2)√("),
("cbrt(","(3)√("),

("rad(","(1)○("),
("deg(","(2)○("),

("asin(","(7)Δ("),
("acos(","(8)Δ("),
("atan(","(9)Δ("),
("sin(","(1)Δ("),
("cos(","(2)Δ("),
("tan(","(3)Δ("),
("csc(","(4)Δ("),
("sec(","(5)Δ("),
("cot(","(6)Δ("),
("pi","(" + str(math.pi) + ")"),
("e","(" + str(math.e) + ")")
]

def calcFunc(msg):
	result = newCalc(msg)
	try:
		result = "{0:g}".format(float(result))
	except:
		pass

	return result

def prepare(msg):
	for i in replace:
		msg = msg.replace(i[0], i[1])

	#Fixing multiple ^ in a row
	i = 0
	while i < len(msg):
		if msg[i] == "^":
			msg = msg[:i+1] + "(" + msg[i+1:]
			brackNum = 0
			j = i
			while j < len(msg):
				if msg[j] == "(":
					brackNum += 1
				elif msg[j] in precedence and precedence.index(msg[j]) > precedence.index("^"):
					if brackNum == 0:
						msg = msg[:j] + ")" + msg[j:]
						break
				elif msg[j] == ")":
					brackNum -= 1
					if brackNum < 0:
						msg = msg[:j] + ")" + msg[j:]
						break
				j += 1
			if j == len(msg):
				msg = msg[:j] + ")" + msg[j:]
		i += 1
	i = 0

	#Fixing - in front of other symbols
	while i < len(msg):
		if msg[i] == "-" and i != 0 and msg[i-1] != ")" and msg[i-1] in precedence:
			msg = msg[:i] + "(0" + msg[i:]
			brackNum = 0
			j = i
			while j < len(msg):
				if msg[j] == "(":
					brackNum += 1
				elif msg[j] in precedence and precedence.index(msg[j]) < precedence.index("-"):
					if brackNum == 0:
						msg = msg[:j] + ")" + msg[j:]
						break
				elif msg[j] == ")":
					brackNum -= 1
					if brackNum < 0:
						msg = msg[:j] + ")" + msg[j:]
						break
				j += 1
			if j == len(msg):
				msg = msg[:j] + ")" + msg[j:]
			i += 2
		i += 1

	return msg


def newCalc(msg):
	msg = prepare(msg)

	msgList = []
	stack = []
	tempNum = ""
	prevChar = ""
	for i in msg:
		if i.isdigit() or i == ".":
			tempNum += i
		else:
			noNum = True
			if tempNum != '':
				msgList.append(tempNum)
				tempNum = ''
				noNum = False
			if i == "(":
				if not noNum or prevChar == ")":
					stack.append('x')
				stack.append(i)
			elif i == ")":
				while stack[-1] != "(":
					msgList.append(stack[-1])
					stack.pop()
				stack.pop()
			elif i in precedence:
				if len(stack) == 0 or stack[-1] == "(":
					if noNum:
						if i == "-":
							msgList.append("0")
					stack.append(i)
				else:
					while len(stack) != 0 and stack[-1] != "(" and precedence.index(i) >= precedence.index(stack[-1]):
						msgList.append(stack[-1])
						stack.pop()

					if noNum:
						if i == "-":
							msgList.append("0")
					stack.append(i)
			else:
				return "error: unknown char: " + i
		prevChar = i

	if tempNum != '':
		msgList.append(tempNum)
	while len(stack) != 0:
		msgList.append(stack[-1])
		stack.pop()

	try:
		i = 2
		while len(msgList) != 1:
			first = float(msgList[i-2])
			second = float(msgList[i-1])
			if msgList[i] in precedence:
				res = []
				if msgList[i] == "x":
					res = [first*second]
				elif msgList[i] == "/":
					res = [first/second]
				elif msgList[i] == "+":
					res = [first + second]
				elif msgList[i] == "^":
					res = [first**second]
				elif msgList[i] == "-":
					res = [first-second]
				elif msgList[i] == "!":
					res = [math.factorial(first)]
				elif msgList[i] == "√":
					res = [second**(1/first)]
				elif msgList[i] == "Δ":
					res = [trigs(first,second)]
				elif msgList[i] == "○":
					if first == 1:
						res = [math.radians(second)]
					elif second == 2:
						res = [math.degrees(second)]
				msgList = msgList[:i-2] + res + msgList[i+1:]
				if len(msgList) != 1:
					i = 2
			else:
				i += 1
	except Exception as e:
		return "error: " + str(e)
	result = msgList[0]
	return result

def trigs(first,second):
	if first == 1:
		return math.sin(second)
	elif first == 2:
		return math.cos(second)
	elif first == 3:
		return math.tan(second)
	elif first == 4:
		return 1/math.sin(second)
	elif first == 5:
		return 1/math.cos(second)
	elif first == 6:
		return 1/math.tan(second)
	elif first == 7:
		return math.asin(second)
	elif first == 8:
		return math.acos(second)
	elif first == 9:
		return math.atan(second)
