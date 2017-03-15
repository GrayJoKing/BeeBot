def start():
	msg = input('''You stand at the entrance of an enormous pyramid. How could no-one have ever found this place before?! You need to report this to the Institute of Archeology immediately. In front of you, you see a stone block out of place. Behind you is your jeep.

[`R`]eturn in your jeep.
[`E`]nter the pyramid.''')
	if msg.lower() == "r":
		jeep()
	elif msg.lower() == "e":
		startRoom()

def jeep():
	if time == 12:00:
	
		msg = input('''You return to your jeep with the intent to drive back to the nearest town with news of your discovery. To your dismay, when you try to start the engine it coughs and dies. You activate your emergency beacon and prepare to wait in the shade of your jeep.

[`S`]earch your jeep
[`E`]nter the pyramid.
[`W`]ait patiently for your rescuers''')
	elif time == 13:
		msg = input('''You wait an hour, but nothing happens.
[`S`]earch your jeep
[`E`]nter the pyramid.
[`W`]ait longer.
[`''')

	if msg.lower() == 's':
		jeepSearch()
	elif msg.lower() == 'e':
		startRoom('start')
	elif msg.lower() == 'w':
		hour += 1
		jeep()

def startRoom(entrance):
	if entrance == "start":
		sendMessage = '''You enter the pyramid through the hole in the side. In the dim light you see a hallway ahead of you. To your left you see a dim portrait of a golden beetle of some kind. ***BANG*** You spin around and find that a stone block has fallen behind you, sealing off your only exit!

Travel [`f`]orward blindly.
Feel around for the [`b`]eetle.
'''
		if "torch" in inventory:	
			sendMessage += '''Light your [`t`]orch.'''
		
		msg = input(sendMessage)
		if msg.lower() == 'f':
			hallway()
		elif msg.lower() == 'b':
			beetlePress()
		elif msg.lower() == 't' and "torch" in inventory:
			startRoom("turnTorchOn")
	elif entrance == "torchTurnOn":
		msg = input('''You turn on the torch and it illuminates the small room. You see a darkened hallway leading forward. To your left, you see a detailed image of a golden beetle. To your right, almost hidden behind a broken tile is what looks like a rough inscription of an ant.
		
Travel [`f`]orward.
Inspect the [`b`]eetle.
Inspect the[`a`]nt.
Turn [`t`]orch off''')
		if msg.lower() == 'f':
			hallway()
		elif msg.lower() == 'b':
			beetlePress()
		elif msg.lower() == 'a':
			antPress()
		elif msg.lower() == 't' and "torch" in inventory:
			startRoom("turnTorchOff")
		
	elif entrance == "torchTurnOff":
		msg = input('''You turn off the torch the room goes dark. You know there is a hallway ahead, a detailed image of a golden beetle to your left and a rough inscription of an ant to your right.

Travel [`f`]orward blindly.
Feel around for the [`b`]eetle.
Feel around for the [`a`]nt.
Turn the [`t`]orch back on.''')
		if msg.lower() == 'f':
			hallway()
		elif msg.lower() == 'b':
			beetlePress()
		elif msg.lower() == 'a':
			antPress()
		elif msg.lower() == 't' and "torch" in inventory:
			startRoom("turnTorchOff")





inventory = []
time = 12
jeepContent = ['Torch','Bottle of water']
beetleButton = False
antButton = False
torch = "unowned"

start()
