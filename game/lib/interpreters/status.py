import lib.utility as utility
from lib.interpreters.command import Command
from lib.interpreters.constants import Position, Range


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


class Score(Command):
	def __init__(self, game):
		super(Score, self).__init__(game, 'score')
		self.minPosition = Position.sleeping
		self.useInCombat = True

	def execute(self, args, config):
		sender = config['sender']
		buf = 'Score:'
		buf += '\n\rDatabase ID: {id}'.format(id=sender.id)
		for s in sender.stats:
			if sender.stats[s]:
				buf += '\n\r{statName}: {stat}'.format(statName=s, stat=sender.stats[s])
		sender.sendToClient(buf)


class Commands(Command):
	def __init__(self, game):
		super(Commands, self).__init__(game, 'commands')
		self.minPosition = Position.sleeping
		self.useInCombat = True

	def execute(self, args, config):
		sender = config['sender']
		buf = 'Commands:\n\r'
		for commandObject in sender.commandInterpreter.commandInterpreters:
			buf += commandObject.__name__ + '\n\r'
		sender.sendToClient(buf)


commandList = [Score, Commands]
