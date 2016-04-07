from lib.interpreters import move, comm, item, saveload, status, crafting, rogue, test
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

		# Import the appropriate class interpreter


	def processCommand(self, command):
		print 'inside CommandInterpreter: ' + command
		if self.lag > 0:
			self.commandQueue.append(command)
			return
		elif len(command) <= 0:
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
		config = {}
		config['sender'] = self.mobile

		sender = self.mobile

		# Check for minimum position.
		currentPosition = sender.position

		if currentPosition < commandObject.minPosition:
			if currentPosition == Position.sleeping:
				sender.sendToClient('In your dreams, or what?')
			elif currentPosition == Position.resting:
				sender.sendToClient('You are too relaxed.')
			elif currentPosition == Position.standing:
				sender.sendToClient('You aren\'t fighting anyone.')
			return

		# Check for nervous
		if sender.isAffectedBy('just died') and not commandObject.useWhileJustDied:
			sender.sendToClient('You died too recently to do that.')
			return

		# Check if it can be used in combat
		if sender.combat and not commandObject.useInCombat:
			sender.sendToClient('You can\'t use that in combat.')
			return

		# Do target checks here.
		if commandObject.canTarget:
			if len(args) <= 0:
				# No target was supplied.
				if commandObject.requireTarget:
					if commandObject.aggro and sender.combat:
						# It's an aggressive spell and you're in combat. Target the enemy.
						target = sender.combat
					elif not commandObject.aggro:
						# It's a beneficial spell. You're the default target.
						target = sender
					else:
						# It's an aggressive spell that requires a target and you're not in combat.
						sender.sendToClient('You need a target.')
						return
				else:
					# It doesn't require a target.
					pass
			else:
				# A target was supplied. Find it by name.
				targetName = args[0]

				# Look for a target in the world
				# FIX ME: add ability to target items
				target = self.game.getTargetMobile(sender, targetName, commandObject.range)

				if not target:
					sender.sendToClient('You can\'t find them.')
					return

				if target == sender and not commandObject.targetSelf:
					sender.sendToClient('You can\'t target yourself with that.')
					return

			# Now we have a target
			config['target'] = target

		commandObject.execute(args, config)

		# If it's an aggressive command, start combat if necessary
		if commandObject.aggro:
			sender.becomeNervous(sender)
			target.becomeNervous(sender)
			if not sender.combat:
				sender.combat = target
				sender.position = Position.fighting
			if not target.combat:
				target.combat = sender
				target.position = Position.fighting
