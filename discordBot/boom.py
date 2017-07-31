from copy import deepcopy
from random import random
from math import floor

class minefieldSpace:
        def __init__(self):
                self.mine = False
                self.value = 0
                self.revealed = False
                self.flagged = False

class minefield:
        def __init__(self, size, mineNum):
                self.size = size
                self.mineNum = mineNum
                self.minefield = [[minefieldSpace() for x in range(0,size)] for x in range(0,size)]
                self.first = True

        def generateMinefield(self, first):
                if self.mineNum > self.size**2:
                        return "error: too many mines"

                currentMines = self.mineNum
                while currentMines > 0:
                        cood = (floor(random()*self.size),floor(random()*self.size))
                        if not self.minefield[cood[0]][cood[1]].mine and not (cood[0]-first[0] in [-1,0,1] and cood[1]-first[1] in [-1,0,1]):
                                self.minefield[cood[0]][cood[1]].mine = True
                                currentMines -= 1
                                for x in [-1,0,1]:
                                        for y in [-1,0,1]:
                                                try:
                                                        if not self.minefield[cood[0]+x][cood[1]+y].mine and cood[1]+y >= 0 and cood[0]+x >= 0:
                                                                self.minefield[cood[0]+x][cood[1]+y].value += 1
                                                except:
                                                        pass

        def clickSpace(self, cood):
                if cood[0] < 0 or cood[1] < 0 or cood[0] >= self.size or cood[1] >= self.size:
                        return ("error: out of range")
                cood = cood[::-1]
                if self.first == True:
                        self.generateMinefield(cood)
                        self.first = False
                space = self.minefield[cood[0]][cood[1]]
                if space.revealed:
                        return "revealed"
                if not space.mine:
                        self.minefield[cood[0]][cood[1]].revealed = True
                        if space.value == 0:
                                for x in [-1,0,1]:
                                        for y in [-1,0,1]:
                                                self.clickSpace((cood[1]+x,cood[0]+y))

                        return "alive"
                else:
                        self.revealMines()
                        return "dead"


        def revealMines(self):
                def reveal(x):
                        if x.mine:
                                x.revealed = True
                        return x
                self.minefield = list(map(lambda row: (list(map(reveal, row))), self.minefield))

        def checkGame(self):
                if len(list(filter(lambda row: len(list(filter(lambda space: space.mine and space.revealed, row))) != 0,self.minefield))) != 0:
                        return "lose"
                if len(list(filter(lambda row: len(list(filter(lambda space: not (space.mine) and not space.revealed, row))) != 0,self.minefield))) != 0:
                        return "playing"
                else:
                        return "win"

        def simpleField(self):
                return list(map(lambda y: (list(map(lambda x: ("M" if x.mine else str(x.value)) if x.revealed else "F" if x.flagged else "B", y))), self.minefield))
        def printField(self):
                return "\n".join(list(map(lambda row: "".join(row), self.simpleField())))

        def flag(self,cood):
                space = self.minefield[cood[0]][cood[1]]
                if space.revealed:
                        return "revealed"
                self.minefield[cood[0]][cood[1]].flagged = not self.minefield[cood[0]][cood[1]].flagged
                return "flagged"
