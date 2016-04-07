import lib.utility as utility
from lib.interpreters.command import Command
from lib.interpreters.constants import Position, Range
from comm import Yell
import lib.combat as combat


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


class Flee(Command):
	def __init__(self, game):
		super(Flee, self).__init__(game, 'flee')
		self.minPosition = Position.fighting
		self.useInCombat = True

	def execute(self, args, config):
		sender = config['sender']
		aggro = sender.combat

		sender.setLag(3)
		sender.combat = None
		sender.position = Position.standing
		if aggro.combat == sender:
			aggro.combat = None
			aggro.position = Position.standing

		aggro.sendToClient('{name} has fled!'.format(name=sender.getName(aggro)))
		sender.sendToClient('You flee from combat!')


class Kill(Command):
	def __init__(self, game):
		super(Kill, self).__init__(game, 'kill')

	def execute(self, args, config):
		sender = config['sender']

		targets = [ mobile for mobile in self.game.mobiles if mobile.room == sender.room and utility.match( args[0], mobile.getName() ) ]
		if not targets:
			sender.sendToClient('You can\'t find them.')
			return
		else:
			target = targets[0]

		if target == sender:
			sender.sendToClient('Suicide is a mortal sin.')
			return

		sender.combat = target
		sender.position = Position.fighting
		sender.setLag(3)
		if target.combat is None:
			target.combat = sender
			target.position = Position.fighting
			# if target.client:
			yell = Yell(self.game)
			yell.execute(['Help! I am being attacked by {sender}!'.format(sender=sender.getName())], {'sender': target})
			# sender does one full round against target
			combatBuffer = {}
			combatBuffer = combat.doSingleRound(sender.game, sender, combatBuffer=combatBuffer)
			combat.appendConditionsToCombatBuffer(combatBuffer)
			combat.sendCombatBuffer(self.game, combatBuffer)


class North(Command):
	def __init__(self, game):
		super(North, self).__init__(game, 'north')

	def execute(self, args, config):
		sender = config['sender']

		move(self.game, 'north', sender)


class South(Command):
	def __init__(self, game):
		super(South, self).__init__(game, 'south')

	def execute(self, args, config):
		sender = config['sender']

		move(self.game, 'south', sender)


class East(Command):
	def __init__(self, game):
		super(East, self).__init__(game, 'east')

	def execute(self, args, config):
		sender = config['sender']

		move(self.game, 'east', sender)


class West(Command):
	def __init__(self, game):
		super(West, self).__init__(game, 'west')

	def execute(self, args, config):
		sender = config['sender']

		move(self.game, 'west', sender)


class Up(Command):
	def __init__(self, game):
		super(Up, self).__init__(game, 'up')

	def execute(self, args, config):
		sender = config['sender']

		move(self.game, 'up', sender)


class Down(Command):
	def __init__(self, game):
		super(Down, self).__init__(game, 'up')

	def execute(self, args, config):
		sender = config['sender']

		move(self.game, 'down', sender)


def move(game, direction, sender):
	newRoom = next((exit.destination for exit in sender.room.exits if exit.key == direction), None)
	if newRoom:
		oldRoom = sender.room
		sender.room = newRoom
		if not sender.isAffectedBy('sneak'):
			game.sendCondition(
				(lambda a: a.room == oldRoom and a is not sender), '{{0}} leaves {direction}.'.format(direction=direction), [sender])
		buf = 'You leave {direction}.'.format(name=sender.name, oldRoom=sender.room.name, newRoom=newRoom.name, direction=direction)
		sender.sendToClient(buf)
		if not sender.isAffectedBy('sneak'):
			game.sendCondition((lambda a: a.room == newRoom and a is not sender), '{0} has arrived.', [sender])
		sender.setLag(1)
	else:
		sender.sendToClient('You can\'t go that way.'.format(name=sender.name, oldRoom=sender.room.name, direction=direction))

commandList = [North, South, East, West, Up, Down, Kill, Flee]
