import lib.utility as utility
from lib.interpreters.command import Command

from lib.interpreters.constants import Position, Range
from lib.affect import Affect


"""
Command Attributes;
attribute (default): description

aggro				(False)				: does it start combat?
canTarget			(False)				: can it take an automatic single target?
requireTarget		(False)				: does it require a target?
useInCombat			(False)				: can you use it in combat?
useWhileJustDied	(True)				: can you use it immediately after dying?
targetSelf			(True)				: can you target yourself?
Range				(Range.room)		: for skills that canTarget, what is the range of potential targets?
minPosition			(Position.standing)	: what is the minimum position as defined in constants.py?
"""


class Sneak(Command):
	def __init__(self, game):
		super(Sneak, self).__init__(game, 'sneak')
		self.useInCombat = False

	def executeFunction(self, args, config):
		sender = config['sender']
		sender.sendToClient('You attempt to move more silently.')
		Affect.factory('Sneak', sender, sender, 60 * sender.level)


commandList = [Sneak]
