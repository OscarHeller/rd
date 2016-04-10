import lib.utility as utility
from lib.interpreters.command import Command

from lib.interpreters.constants import Position, Range
from lib.affect import Affect


class Sneak(Command):
	def __init__(self, game):
		super(Sneak, self).__init__(game, 'sneak')

	def executeFunction(self, args, sender):
		msg = 'You attempt to move more silently.'
		self.appendToCommandBuffer(sender, msg)
		Affect.factory('Sneak', sender, sender, 60 * sender.level)


commandList = [Sneak]
