from lib.interpreters.constants import Position
import lib.utility as utility


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
				sender.appendToCommandBuffer(sender, 'You are too relaxed.')
			elif sender.position == Position.standing:
				sender.appendToCommandBuffer(sender, 'You can\'t do that in combat.')
			elif sender.position == Position.standing:
				sender.appendToCommandBuffer(sender, 'You aren\'t fighting anyone.')
			raise self.CommandException()

	def getTargetFromListByName(self, needle, haystack):
		for candidate in haystack:
			if utility.matchList(needle, candidate.keywords):
				return candidate
		raise self.TargetNotFoundException()
