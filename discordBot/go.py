from copy import deepcopy

class goGame:
	def __init__(self):
		self.board = [[0 for i in range(9)] for i in range(9)]
		self.tempBoard = deepcopy(self.board)
		self.captured = [0,0]

	def add(self, cood, num):

		if self.board[cood[0]][cood[1]] != 0:
			return "Invalid Move: Not empty"

		self.tempBoard[cood[0]][cood[1]] = num

		popChains = self.check()

		if len(popChains) == 1 and cood in popChains[0]:
			self.tempBoard = deepcopy(self.board)
			return "Invalid Move: Suicide"

		self.board[cood[0]][cood[1]] = num
		for chain in popChains:
			if cood not in chain:
				for link in chain:
					self.captured[self.board[link[0]][link[1]]-1] += 1
					self.board[link[0]][link[1]] = 0

		self.tempBoard = deepcopy(self.board)


	def check(self):
		ignore = []
		popChains = []
		for row in range(len(self.tempBoard)):
			for col in range(len(self.tempBoard[row])):
				if self.tempBoard[row][col] != 0 and [row, col] not in ignore:
					chain = self.getLinks([row,col], [])
					for link in chain:
						ignore.append([link[0],link[1]])
					liberties = self.getLiberty(chain)
					if len(liberties) == 0:
						popChains.append(chain)
		return popChains

	def getLinks(self, cood, linkList):
		linkList.append([cood[0], cood[1]])
		for change in [-1,1]:
			if cood[0]+change in range(9) and self.tempBoard[cood[0]][cood[1]] == self.tempBoard[cood[0]+change][cood[1]] and [cood[0]+change, cood[1]] not in linkList:
				linkList = self.getLinks([cood[0]+change, cood[1]], linkList)

			if cood[1]+change in range(9) and self.tempBoard[cood[0]][cood[1]] == self.tempBoard[cood[0]][cood[1]+change] and [cood[0], cood[1]+change] not in linkList:
				linkList = self.getLinks([cood[0], cood[1]+change], linkList)

		return linkList

	def getLiberty(self, chain):
		liberties = []
		for link in chain:
			for change in [-1,1]:
				if link[0]+change in range(9) and self.tempBoard[link[0]+change][link[1]] == 0 and [link[0]+change, link[1]] not in liberties:
					liberties.append([link[0]+change, link[1]])

				if link[1]+change in range(9) and self.tempBoard[link[0]][link[1]+change] == 0 and [link[0], link[1]+change] not in liberties:
					liberties.append([link[0], link[1]+change])

		return liberties

	def getSurround(self, chain):
		player = None
		for link in chain:
			for change in [-1,1]:
				if link[0]+change in range(9) and self.tempBoard[link[0]+change][link[1]] != 0:
					if not player:
						player = self.tempBoard[link[0]+change][link[1]]
					elif player != self.tempBoard[link[0]+change][link[1]]:
						return False

				if link[1]+change in range(9) and self.tempBoard[link[0]][link[1]+change] != 0:
					if not player:
						player = self.tempBoard[link[0]][link[1]+change]
					elif player != self.tempBoard[link[0]][link[1]+change]:
						return False
		return player

	def territoryCheck(self):
		total = [0,0]
		ignore = []
		for row in range(len(self.tempBoard)):
			for col in range(len(self.tempBoard[row])):
				if self.tempBoard[row][col] == 0 and [row, col] not in ignore:
					chain = self.getLinks([row,col], [])
					check = self.getSurround(chain)
					if check:
						total[check-1] += len(chain)
					ignore += chain
		return total

# 
# game = goGame()
# player = 1
#
# while True:
# 	cood = list(map(lambda co: int(co) , input("Player" + str(player) + ": ").split(",")))
#
# 	game.add(cood, player)
#
# 	player = player*(-1)+3
#
# 	print("\n".join(list(map(lambda row: " ".join(list(map(lambda spot: str(spot), row))), game.board))))
# 	territory = game.territoryCheck()
# 	print("Points:", territory[0] + game.captured[1], territory[1] + game.captured[0])
