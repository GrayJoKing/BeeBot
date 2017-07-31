

import sqlite3
import json

con = sqlite3.connect('database.db')

with open('gameData/bang.json','r') as fp:
	bangStats = json.load(fp)
	fp.close()

with open('gameData/money.json','r') as fp:
	money = json.load(fp)
	fp.close()

c = con.cursor()

c.execute("CREATE TABLE if not exists bangstats (id, name, plays, deaths, record, current, money)")

for user in bangStats:
	print("Inserting {}".format(user))
	temp = (user,
			bangStats[user]['play'],
			bangStats[user]['kill'],
			bangStats[user]['lStreak'],
			bangStats[user]['cStreak'],
			0 if user not in money else money[user])
	c.execute("INSERT INTO bangstats VALUES (?,'',?,?,?,?,?)", temp)

c.execute("CREATE TABLE if not exists serverinfo (id, name, byeChannel, hiChannel, modChannel, botChannel, hiMessage, byeMessage)")

c.execute("CREATE TABLE if not exists giveme (serverid, roleid, name, colour)")

con.commit()
