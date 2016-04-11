import lib.utility as utility
from lib.interpreters.command import Command
from lib.interpreters.constants import Position, Range
import lib.combat as combat
import random


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

class Recall(Command):
	def __init__(self, game):
		super(Recall, self).__init__(game, 'recall')

	def execute(self, args, sender):
		# Preliminary checks
		self.test(self.checkPosition, (sender, [Position.standing]))
		if sender.room.getStat('no_recall'):
			raise self.CommandException("You can't recall from this room.")
		self.appendToCommandBuffer(sender, "You pray for transportation.")
		for mobile in sender.inRoomExcept(sender):
			self.appendToCommandBuffer(mobile, sender.getName(mobile) + " prays for transportation.")
		self.test(self.simpleSuccessCheck, 65, override='You failed!')

		self.appendToCommandBuffer(sender, "You vanish!")
		for mobile in sender.inRoomExcept(sender):
			self.appendToCommandBuffer(mobile, sender.getName(mobile) + " vanishes!")
		sender.room = self.game.rooms[0] # FIX ME: some way of specifying which room to recall to

class Flee(Command):
	def __init__(self, game):
		super(Flee, self).__init__(game, 'flee')

	def execute(self, args, sender):
		# Preliminary checks
		self.test(self.checkPosition, (sender, [Position.fighting,]))

		aggro = sender.combat
		exits = sender.room.exits

		# Complex checks
		self.test(self.areThereAnyExits, sender.room, override='PANIC! There\'s nowhere to flee!')
		self.test(self.simpleSuccessCheck, 25, override='PANIC! You couldn\'t escape!')

		exit = random.choice(exits)
		newRoom = exit.destination
		oldRoom = sender.room
		direction = exit.key

		combat.endCombatForPlayersByTarget(self.game, sender)

		sender.setLag(3)
		sender.combat = None
		sender.position = Position.standing

		for mobile in sender.inRoomExcept(sender):
			msg = '{name} has fled!\n\r{name} leaves {direction}.'.format(name=sender.getName(mobile),direction=direction)
			self.appendToCommandBuffer(mobile, msg)

		sender.room = newRoom
		msg = 'You flee from combat!'
		self.appendToCommandBuffer(sender, msg)

		for mobile in sender.inRoomExcept(sender):
			msg = '{name} has arrived.'.format(name=sender.getName(mobile))
			self.appendToCommandBuffer(mobile, msg)


class Kill(Command):
	def __init__(self, game):
		super(Kill, self).__init__(game, 'kill')

	def execute(self, args, sender):
		# Preliminary checks
		self.test(self.checkPosition, (sender, [Position.standing,]))
		self.test(self.hasAtLeastOneArgument, args, override='Kill whom?')

		# Automatic targeting
		target = self.test(self.getMobileFromListByName, (args[0], sender.inRoomExcept(sender)))

		self.test(self.notSelfTargetable, (sender, target), override='Suicide is a mortal sin.')
		self.test(self.isLegalCombatTarget, target)

		sender.setLag(3)
		sender.startCombatWith(target)
		if target.is_player:
			target.processCommand('yell Help! I am being attacked by {sender}!'.format(sender=sender.getName(target)))

		# sender does one full round against target
		combatBuffer = {}
		combatBuffer = combat.doSingleRound(sender.game, sender, combatBuffer=combatBuffer)
		combat.appendConditionsToCombatBuffer(combatBuffer)
		combat.sendCombatBuffer(self.game, combatBuffer)


class North(Command):
	def __init__(self, game):
		super(North, self).__init__(game, 'north')

	def execute(self, args, sender):
		self.move(sender, 'north')


class South(Command):
	def __init__(self, game):
		super(South, self).__init__(game, 'south')

	def execute(self, args, sender):
		self.move(sender, 'south')


class East(Command):
	def __init__(self, game):
		super(East, self).__init__(game, 'east')

	def execute(self, args, sender):
		self.move(sender, 'east')


class West(Command):
	def __init__(self, game):
		super(West, self).__init__(game, 'west')

	def execute(self, args, sender):
		self.move(sender, 'west')


class Up(Command):
	def __init__(self, game):
		super(Up, self).__init__(game, 'up')

	def execute(self, args, sender):
		self.move(sender, 'up')


class Down(Command):
	def __init__(self, game):
		super(Down, self).__init__(game, 'down')

	def execute(self, args, sender):
		self.move(sender, 'down')

commandList = [North, South, East, West, Up, Down, Kill, Flee, Recall]
