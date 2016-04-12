from lib.interpreters import move, comm, item, saveload, status, crafting, rogue, test, admin
import lib.utility
from lib.interpreters.constants import Range, Position


class CommandInterpreter:
	def __init__(self, game, mobile):
		self.game = game
		self.mobile = mobile

		self.lag = 0
		self.commandQueue = []

		self.commandInterpreters = []

		# Import all the generic interpreters
		self.commandInterpreters.extend(move.commandList)
		self.commandInterpreters.extend(comm.commandList)
		self.commandInterpreters.extend(item.commandList)
		self.commandInterpreters.extend(saveload.commandList)
		self.commandInterpreters.extend(status.commandList)
		self.commandInterpreters.extend(crafting.commandList)
		self.commandInterpreters.extend(test.commandList)
		self.commandInterpreters.extend(admin.commandList)

		# Import the appropriate class interpreter


	def processCommand(self, command):
		print 'inside CommandInterpreter: ' + command

		if len(command) <= 0:
			return

		verb = command.split()[0]
		args = command.split()[1:]

		if verb == 'linkdead':  # FIX ME: a player could type linkdead and it would do it. Need to be able to send admin commands separately.
			self.mobile.goLinkdead()
			return

		success = False

		for commandObject in self.getCommandInterpreters():
			potentialCommand = commandObject(self.game)  # FIX ME: rework to search a dictionary and only use an object if necessary? Static object?
			if lib.utility.match(verb, potentialCommand.key):
				self.executeCommand(potentialCommand, args)
				success = True
				break

		if not success:
			self.mobile.sendToClient('Huh?')

	def getCommandInterpreters(self):
		return self.commandInterpreters + self.mobile.getCommandInterpreters()

	def executeCommand(self, commandObject, args):
		sender = self.mobile

		try:
			commandObject.prepare()
			commandObject.execute(args, sender)
			commandObject.output()
		except commandObject.CommandException as e:
			sender.sendToClient(str(e))

