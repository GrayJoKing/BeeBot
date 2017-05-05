from math import floor

def runBounce(code, inp):
    if "_" not in code:
        return "error", {"reason":"No starting point.", "line":None, "instruction":None, "pointer":None}
    elif code.count("_") != 1:
        return "error", {"reason":"Too many starting points found.", "line":None, "instruction":None, "pointer":None}

    code = code.split("\n")

    code = list(map(lambda line: list(line), code))

    for line in range(len(code)):
        for instruction in range(len(code[line])):
            if code[line][instruction] == "_":
                row = line
                pointer = instruction

    inp = list(inp)[::-1]
    executed = 0
    bounces = 2
    direction = 1
    output = ""
    stack = []

    #quote:
    #False = ', True = "
    quote = None

    while executed < 10000:
        pointer += direction
        executed += 1
        if pointer < 0 or pointer >= len(code[row]):
            return "error", {"reason":"Pointer escaped!", "line":row, "instruction":"None", "pointer":pointer}

        inst = code[row][pointer]
        
        if quote:
            if inst == '"':
                quote = None
            else:
                stack.append(ord(inst))
        
        elif inst == "^":
            return "success", {"output":output, "executed":executed, "bounces":bounces}

        #Obstacles
        elif inst in "|><@":
            if inst == "|":
                direction = -direction
            elif inst == ">":
                direction = 1
            elif inst == "<":
                direction = -1
            elif inst == "@":
                pointer += direction
            bounces += 1
        elif inst in "[]":
            if (inst == "[" and direction == -1) or (inst == "]" and direction == 1):
                opp = {"[":"]", "]":"["}
                coods = []
                for line in range(len(code)):
                    for instruction in range(len(code[line])):
                        if code[line][instruction] == opp[inst]:
                            coods.append([line, instruction])
                if len(coods) == 0:
                    return "error", {"reason":"Pointer entered a teleporter but was never seen again.", "line":row, "instruction":inst, "pointer":pointer}
                closest = []
                num = 1
                minDist = -1
                for cood in coods:
                    dist = abs(row-cood[0]) + abs(pointer-cood[1])
                    if dist < minDist or minDist == -1:
                        minDist = dist
                        closest = cood
                        num = 1
                    elif dist == minDist:
                        num += 1
                if num != 1:
                    return "error", {"reason":"Pointer tried to exit out more than one teleporter.", "line":row, "instruction":inst, "pointer":pointer}
                row = closest[0]
                pointer = closest[1]


        #Input/Ouput
        elif inst == "." or inst == ":":
            if len(stack) == 0:
                pointer += direction
                bounces += 1
            elif inst == ".":
                output += str(stack[-1])
                stack.pop()
            else:
                output += chr(stack[-1])
                stack.pop()

        elif inst == ",":
            if len(inp) == 0:
                pointer += direction
                bounces += 1
            else:
                try:
                    stack.append(int(inp[-1]))
                    inp.pop()
                except:
                    return "error", {"reason":"Input is not an integer.", "line":row, "instruction":inst, "pointer":pointer}
        elif inst == ";":
            if len(inp) == 0:
                pointer += direction
                bounces += 1
            else:
                stack.append(ord(inp[-1]))
                inp.pop()

        #Comparison
        elif inst == "?":
            if len(stack) == 0:
                pointer += direction
                bounces += 1
        elif inst == "=":
            if len(stack) < 2:
                return "error", {"reason":"Stack has less than 2 items.", "line":row, "instruction":inst, "pointer":pointer}
            else:
                if stack[-1] == stack[-2]:
                    pointer += direction
                    bounces += 1

        #Stack Stuff
        elif inst == "$":
            if len(stack) == 0:
                return "error", {"reason":"Stack is empty.", "line":row, "instruction":inst, "pointer":pointer}
            else:
                stack.append(stack[-1])
        elif inst in "%+-*/":
            if len(stack) < 2:
                pointer += direction
                bounces += 1
            else:
                if inst == "%":
                    temp = stack[-2]
                    stack[-2] = stack[-1]
                    stack[-1] = stack[-2]
                else:
                    if inst == "+":
                        stack[-2] = stack[-2] + stack[-1]
                    elif inst == "-":
                        stack[-2] = stack[-2] - stack[-1]
                    elif inst == "*":
                        stack[-2] = stack[-2] * stack[-1]
                    elif inst == "/":
                        stack[-2] = floor(stack[-2] / stack[-1])
                    stack.pop()
                    
        elif quote == False:
            if inst == "'":
                quote = None
            else:
                stack.append(ord(inst))
        elif inst == '"':
            quote = not quote
        elif inst == "'":
            if quote == None:
                quote = False
            else:
                quote = None
        else:
            executed -= 1

    return "error", {"reason":"Program ran over 10000 instructions. Probable infinite loop.", "line":line, "instruction":inst, "pointer":pointer}            
