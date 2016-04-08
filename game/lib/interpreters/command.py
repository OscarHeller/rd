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

	class TargetNotFoundException(CommandException):
		pass

	class NoExitsException(CommandException):
		pass

	class SkillFailedException(CommandException):
		pass

	class NoArgumentsException(CommandException):
		pass

	class AffectException(CommandException):
		pass

	class IllegalCombatTargetException(CommandException):
		pass

	class SelfTargetableException(CommandException):
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

	def checkPosition(self, sender, allowedPositions):
		if sender.position not in allowedPositions:
			if sender.position == Position.sleeping:
				self.appendToCommandBuffer(sender, 'In your dreams, or what?')
			elif sender.position == Position.resting:
				self.appendToCommandBuffer(sender, 'You are too relaxed.')
			elif sender.position == Position.fighting:
				self.appendToCommandBuffer(sender, 'You can\'t do that in combat.')
			elif sender.position == Position.standing:
				self.appendToCommandBuffer(sender, 'You aren\'t fighting anyone.')
			raise self.CommandException()

	def getTargetFromListByName(self, needle, haystack):
		if not haystack:
			raise self.TargetNotFoundException()
		for candidate in haystack:
			if utility.matchList(needle, candidate.keywords):
				return candidate
		raise self.TargetNotFoundException()

	def areThereAnyExits(self, room):
		if len(room.exits) == 0:
			raise self.NoExitsException()

	def simpleSuccessCheck(self, percentage):
		if random.randint(0,100) >= percentage:
			raise self.SkillFailedException()

	def hasAtLeastOneArgument(self, args):
		if not args:
			raise self.NoArgumentsException()

	def notAffectedBy(self, target, affects):
		for affect in affects:
			if affect in target.affects:
				raise AffectException()

	def isLegalCombatTarget(self, target):
		if target.isAffectedBy('just died'):
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