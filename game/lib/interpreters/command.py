from lib.interpreters.constants import Position
import lib.utility as utility
import random


class Command(object):
	def __init__(self, game, key, comm=False):
		self.game = game
		self.key = key
		self.commandBuffer = {}
		self.comm = comm
		self.exceptionOccurred = False

	class CommandException(Exception):
		pass

	def prepare(self):
		self.commandBuffer = {}

	def execute(self, args, sender):
		print ('BUG: This command has no overriding execute function.')

	def output(self):
		for mobile, bufferList in self.commandBuffer.iteritems():
			bufferString = '\n\r'.join( bufferList )

			mobile.sendToClient( bufferString, comm=(self.comm if not self.exceptionOccurred else False) )

	def appendToCommandBuffer(self, key, string):
		if key in self.commandBuffer:
			self.commandBuffer[key].append(string)
		else:
			self.commandBuffer[key] = [string,]

	def checkPosition(self, sender, allowedPositions, override=None):
		if isinstance(allowedPositions, list) and sender.position in allowedPositions:
			return
		elif sender.position == allowedPositions:
			return
		else:
			if sender.position == Position.sleeping:
				msg = 'In your dreams, or what?'
			elif sender.position == Position.resting:
				msg = 'You are too relaxed.'
			elif sender.position == Position.fighting:
				msg = 'You can\'t do that in combat.'
			elif sender.position == Position.standing:
				msg = 'You aren\'t fighting anyone.'

		if override:
			msg = override

		raise self.CommandException(msg)


	def getMobileFromListByName(self, needle, haystack):
		if not haystack:
			raise self.CommandException('You don\'t see them here.')
		for candidate in haystack:
			if utility.matchList(needle, candidate.keywords):
				return candidate
		raise self.CommandException('You don\'t see them here.')


	def getItemFromListByName(self, needle, haystack):
		if not haystack:
			raise self.CommandException('You don\'t see that here.')
		for candidate in haystack:
			if utility.matchList(needle, candidate.keywords):
				return candidate
		raise self.CommandException('You don\'t see that here.')


	def getTargetFromListByName(self, needle, haystack):
		if not haystack:
			raise self.CommandException('DEPRECATED: You don\'t see them here.')
		for candidate in haystack:
			if utility.matchList(needle, candidate.keywords):
				return candidate
		print 'getTargetFromListByName is DEPRECATED, use getMobileFromListByName or getItemFromListByName instead.'
		raise self.CommandException('DEPRECATED: You don\'t see them here.')

	def areThereAnyExits(self, room):
		if len(room.exits) == 0:
			raise self.NoExitsException()

	def simpleSuccessCheck(self, percentage):
		if random.randint(0,100) >= percentage:
			raise self.SkillFailedException()

	def hasAtLeastOneArgument(self, args):
		if not args:
			raise self.CommandException('You need at least one argument to use this command.')

	def notAffectedBy(self, target, affects):
		if isinstance(affects, list):
			for affect in affects:
				if affect in [affect.name for affect in target.affects]:
					raise self.AffectException()
		else:
			if affects in [affect.name for affect in target.affects]:
				raise self.AffectException()

	def isLegalCombatTarget(self, target):
		if target.room.getStat('no_combat'):
			raise self.IllegalCombatTargetException()
		elif target.isAffectedBy('just died'):
			raise self.IllegalCombatTargetException()

	def move(self, sender, direction):
		newRoom = next((exit.destination for exit in sender.room.exits if exit.key == direction), None)
		if newRoom:
			oldRoom = sender.room
			sender.room = newRoom
		else:
			raise self.NoExitsException()

	def notSelfTargetable(self, target, sender):
		if target == sender:
			self.appendToCommandBuffer(sender, 'You can\'t target yourself with this command.')
			raise self.SelfTargetableException()

	def test(self, function, args, override=None):
		if not isinstance(args, tuple):
			args = (args,)
		try:
			returnValue = function( *args )
		except self.CommandException as e:
			if override:
				raise self.CommandException(override)
			else:
				raise

		return returnValue

	def error(self, message):
		raise self.CommandException(message)