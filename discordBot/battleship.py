from random import random, shuffle
from math import floor
from copy import deepcopy
from functools import reduce

class battleShipBoard:
	#N = Nothing
	#A = Aircraft Carriers
	#B = Battle ships
	#S = Submarines
	#C = Cruisers
	#D = Destroyers
	#P = Pins
	#E = Exploded
	#M = Miss

	def __init__(self, difficulty=None):
		self.difficulty = difficulty
		self.board = list(map(lambda row: list(map(lambda space: "N", range(10))), range(10)))
		self.enemyBoard = list(map(lambda row: list(map(lambda space: "N", range(10))), range(10)))
		self.shipDict = {'A':4,'B':5,'S':2,'C':3,'D':3}
		self.shipsLeft = []
		self.enemyShipsLeft = ['A', 'B', 'C', 'D', 'S']
		self.pureBoard = deepcopy(self.board)
		self.backboard = deepcopy(self.board)
		self.confirm = None

	def placeShip(self, ship, coord, direction):
		if ship not in self.shipsLeft:
			self.undoPlacement()
			coord = coord[::-1]
			row = coord[1]
			col = coord[0]
			if direction == "S":
				if row < 11-self.shipDict[ship]:
					for a in range(0,self.shipDict[ship]):
						if self.board[row+a][col] != 'N':
							return "Error: Collision with other fleet."
					for a in range(0,self.shipDict[ship]):
						self.board[row+a][col] = ship
					return None
				else:
					return "Error: Too close to wall."

			if direction == "N":
				if row > self.shipDict[ship]-2:
					for a in range(0,self.shipDict[ship]):
						if self.board[row-a][col] != 'N':
							return "Error: Collision with other fleet."
					for a in range(0,self.shipDict[ship]):
						self.board[row-a][col] = ship
					return None
				else:
					return "Error: Too close to wall."

			if direction == "E":
				if col < 11-self.shipDict[ship]:
					for a in range(0,self.shipDict[ship]):
						if self.board[row][col+a] != 'N':
							return "Error: Collision with other fleet."
					for a in range(0,self.shipDict[ship]):
						self.board[row][col+a] = ship
					return None
				else:
					return "Error: Too close to wall."

			if direction == "W":
				if col > self.shipDict[ship]-2:
					for a in range(0,self.shipDict[ship]):
						if self.board[row][col-a] != 'N':
							return "Error: Collision with other fleet."
					for a in range(0,self.shipDict[ship]):
						self.board[row][col-a] = ship
					return None
				else:
					return "Error: Too close to wall."

	def confirmPlacement(self):
		if self.confirm:
			self.backboard = deepcopy(self.board)
			shipsLeft.append(self.confirm)

	def startGame(self):
		self.pureBoard = deepcopy(self.board)

	def resetBoard(self):
		self.board = deepcopy(self.pureBoard)

	def undoPlacement(self):
		self.board = deepcopy(self.backboard)

	def randomBoard(self):
		direct = ['N','S','W','E']
		for ship in self.shipDict:
			while True:
				pos = (floor(random()*10),floor(random()*10))
				shuffle(direct)
				final = None
				for compass in direct:
					test = True

					check = self.placeShip(ship, pos, compass)
					if not check:
						break
				if not check:
					self.confirmPlacement()
					break

	def pinEnemy(self, cood):
		if not self.checkRange(cood):
			return "Error: Out of Range"
		cood = cood[::-1]
		if self.enemyBoard[cood[0]][cood[1]] != "E":
			if self.enemyBoard[cood[0]][cood[1]] == "P":
				self.enemyBoard[cood[0]][cood[1]] = "N"
				return "Unpinned"
			else:
				self.enemyBoard[cood[0]][cood[1]] = "P"
				return "Pinned"
		return "No Pin"

	def textBoard(self):
		return "\n".join(list(map(lambda row: "".join(row),self.board)))

	def enemyTextBoard(self):
		return "\n".join(list(map(lambda row: "".join(row),self.enemyBoard)))

	def checkRange(self,cood):
		return cood[0] <= 9 and cood[0] >= 0 and cood[1] <= 9 and cood[1] >= 0

	def shootSpace(self, cood):
		if not self.checkRange(cood):
			return ["Error: Out of Range"]
		cood = cood[::-1]
		if self.board[cood[0]][cood[1]] == "M" or self.board[cood[0]][cood[1]] == "E":
			return ["Error: Already shot at."]
		elif self.board[cood[0]][cood[1]] == "N":
			self.board[cood[0]][cood[1]] = "M"
			return ["Miss!", cood]
		else:
			self.board[cood[0]][cood[1]] = "E"
			sunkCoord = self.checkSunk()
			if len(self.shipsLeft) == 0:
				return ["Win!", cood, sunkCoord]
			else:
				return ["Hit!", cood, sunkCoord]

	def checkSunk(self):
		sunkShip = None
		text = self.textBoard()
		for ship in self.shipDict:
			if ship not in text and ship in self.shipsLeft:
				sunkShip = ship
				self.shipsLeft.pop(self.shipsLeft.index(ship))
				break
		if sunkShip:
			sunkCoord = []
			for row in range(0,10):
				for col in range(0,10):
					if self.pureBoard[row][col] == sunkShip:
						sunkCoord.append((col,row))
			return [sunkShip, sunkCoord]
		return sunkShip


	def updateEnemy(self, shot):
		if shot[0] == "Hit!" or shot[0] == "Win!":
			self.enemyBoard[shot[1][0]][shot[1][1]] = "E"
			if shot[2]:
				for coord in shot[2][1]:
					self.enemyBoard[coord[1]][coord[0]] = shot[2][0]
				self.enemyShipsLeft.pop(self.enemyShipsLeft.index(shot[2][0]))
			return "Lose." if shot[0] == "Win!" else "Hit!"
		elif shot[0] == "Miss!":
			self.enemyBoard[shot[1][0]][shot[1][1]] = "M"
			return "Missed"


	def AIshoot(self):
		return self.prob()[::-1]

	def prob(self):
		default = 1
		prob = list(map(lambda row: list(map(lambda space: 0, range(10))), range(10)))
		for row in range(0,10):
			for col in range(0,10):
				if self.enemyBoard[row][col] in ['N','E']:
					for ship in self.enemyShipsLeft:
						if row < 11-self.shipDict[ship]: #down
							test = True
							value = default
							for a in range(0,self.shipDict[ship]):
								if self.enemyBoard[row+a][col] not in ['N','E']:
									test = False
								if self.enemyBoard[row+a][col] == "E":
									value += 653
							if test:
								for a in range(0,self.shipDict[ship]):
									if self.enemyBoard[row+a][col] != "E":
										prob[row+a][col] += value
						if col < 11-self.shipDict[ship]: #right
							test = True
							value = default
							for a in range(0,self.shipDict[ship]):
								if self.enemyBoard[row][col+a] not in ['N','E']:
									test = False
								if self.enemyBoard[row][col+a] == "E":
									value += 653
							if test:
								for a in range(0,self.shipDict[ship]):
									if self.enemyBoard[row][col+a] != "E":
										prob[row][col+a] += value


		highest = 0
		possible = []
		maxV = 0
		for row in range(0,10):
			for space in range(0,10):
				if prob[row][space] > maxV:
					maxV = prob[row][space]
					possible = [(row,space)]
				elif prob[row][space] == maxV:
					possible.append((row,space))

		shuffle(possible)
		return possible[0]


# board = battleShipBoard(None)
# board2 = battleShipBoard(None)
#
# board2.randomBoard()
#
# board.startGame()
# board2.startGame()
#
# counter = 0
# ave = []
# amount = 500
# for i in range(0,amount):
#	 while True:
#		 counter += 1
#	 ##	print(board2.textBoard())
#	 ##	print()
#	 ##	print(board.enemyTextBoard())
#	 ##	print()
#		 if board.updateEnemy(board2.shootSpace(board.AIshoot())) == "Lose.":
#			 board = battleShipBoard(None)
#			 board2 = battleShipBoard(None)
#
#			 board2.randomBoard()
#
#			 board.startGame()
#			 board2.startGame()
#			 break
#
#	 #print(counter)
#	 ave.append(counter)
#	 counter = 0
#	 if i%(amount/100) == 0 and i != 0:
#		 print(100*i/amount,"%")
#
# ave.sort()
# print(ave[floor(amount/2)], "!!!")
