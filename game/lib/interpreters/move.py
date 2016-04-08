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


class Flee(Command):
	def __init__(self, game):
		super(Flee, self).__init__(game, 'flee')

	def execute(self, args, sender):
		try:
			# Preliminary checks
			self.checkPosition(sender, [Position.fighting,])

			aggro = sender.combat
			exits = sender.room.exits

			# Complex checks
			self.areThereAnyExits(sender.room)
			self.simpleSuccessCheck(25)

			exit = random.choice(exits)
			newRoom = exit.destination
			oldRoom = sender.room
			direction = exit.key

			combat.endCombatForPlayersByTarget(self.game, sender)

			sender.setLag(3)
			sender.combat = None
			sender.position = Position.standing
			sender.room = newRoom

			msg = 'You flee from combat!'
			self.appendToCommandBuffer(sender, msg)

			for mobile in [ mobile for mobile in self.game.mobiles if mobile.room == oldRoom and mobile != sender ]:
				msg = '{name} has fled!\n\r{name} leaves {direction}.'.format(name=sender.getName(mobile),direction=direction)
				self.appendToCommandBuffer(mobile, msg)
			for mobile in [ mobile for mobile in self.game.mobiles if mobile.room == newRoom and mobile != sender ]:
				msg = '{name} has arrived.'.format(name=sender.getName(mobile))
				self.appendToCommandBuffer(mobile, msg)
		except (self.SkillFailedException, self.NoExitsException) as e:
			msg = 'PANIC! You can\'t escape!'
			self.appendToCommandBuffer(sender, msg)

			sender.setLag(1)

			for mobile in [ mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender ]:
				msg = '{sender} tries to flee, but fails.'.format(sender=sender.getName(mobile))
				self.appendToCommandBuffer(mobile, msg)
		except self.CommandException as e:
			self.exceptionOccurred = True




class Kill(Command):
	def __init__(self, game):
		super(Kill, self).__init__(game, 'kill')

	def execute(self, args, sender):
		try:
			# Preliminary checks
			self.checkPosition(sender, [Position.standing,])
			self.hasAtLeastOneArgument(args)

			# Automatic targeting
			target = self.getTargetFromListByName(args[0], [mobile for mobile in self.game.mobiles if mobile.room == sender.room])

			if target == sender:
				msg = 'Suicide is a mortal sin.'
				self.appendToCommandBuffer(sender, msg)
				return

			if target.isAffectedBy('just died'):
				msg = 'They died too recently to attack them.'
				self.appendToCommandBuffer(sender, msg)
				return

			sender.setLag(3)			
			sender.startCombatWith(target)

			# sender does one full round against target
			combatBuffer = {}
			combatBuffer = combat.doSingleRound(sender.game, sender, combatBuffer=combatBuffer)
			combat.appendConditionsToCombatBuffer(combatBuffer)
			combat.sendCombatBuffer(self.game, combatBuffer)
		except self.TargetNotFoundException as e:
			msg = 'You can\'t find them.'
			self.appendToCommandBuffer(sender, msg)
			self.exceptionOccurred = True
		except self.NoArgumentsException as e:
			msg = 'Kill whom?'
			self.appendToCommandBuffer(sender, msg)
			self.exceptionOccurred = True
		except self.CommandException as e:
			self.exceptionOccurred = True


class North(Command):
	def __init__(self, game):
		super(North, self).__init__(game, 'north')

	def execute(self, args, sender):
		try:
			oldRoom = sender.room

			self.move(sender, 'north')

			msg = 'You leave north.'
			self.appendToCommandBuffer(sender, msg)

			if not sender.isAffectedBy('sneak'):
				for mobile in [mobile for mobile in self.game.mobiles if mobile.room == oldRoom]:
					msg = '{sender} leaves north.'.format(sender=sender)
					self.appendToCommandBuffer(mobile, msg)

				for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]:
					msg = '{sender} has arrived.'.format(sender=sender)
					self.appendToCommandBuffer(mobile, msg)

			sender.setLag(1)
		except self.NoExitsException as e:
			msg = 'You can\'t go that way.'
			self.exceptionOccurred = True
			self.appendToCommandBuffer(sender, msg)
		except self.CommandException as e:
			self.exceptionOccurred = True


class South(Command):
	def __init__(self, game):
		super(South, self).__init__(game, 'south')

	def execute(self, args, sender):
		try:
			oldRoom = sender.room

			self.move(sender, 'south')

			msg = 'You leave south.'
			self.appendToCommandBuffer(sender, msg)

			if not sender.isAffectedBy('sneak'):
				for mobile in [mobile for mobile in self.game.mobiles if mobile.room == oldRoom]:
					msg = '{sender} leaves south.'.format(sender=sender)
					self.appendToCommandBuffer(mobile, msg)

				for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]:
					msg = '{sender} has arrived.'.format(sender=sender)
					self.appendToCommandBuffer(mobile, msg)

			sender.setLag(1)
		except self.NoExitsException as e:
			msg = 'You can\'t go that way.'
			self.exceptionOccurred = True
			self.appendToCommandBuffer(sender, msg)
		except self.CommandException as e:
			self.exceptionOccurred = True


class East(Command):
	def __init__(self, game):
		super(East, self).__init__(game, 'east')

	def execute(self, args, sender):
		try:
			oldRoom = sender.room

			self.move(sender, 'east')

			msg = 'You leave east.'
			self.appendToCommandBuffer(sender, msg)

			if not sender.isAffectedBy('sneak'):
				for mobile in [mobile for mobile in self.game.mobiles if mobile.room == oldRoom]:
					msg = '{sender} leaves east.'.format(sender=sender)
					self.appendToCommandBuffer(mobile, msg)

				for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]:
					msg = '{sender} has arrived.'.format(sender=sender)
					self.appendToCommandBuffer(mobile, msg)

			sender.setLag(1)
		except self.NoExitsException as e:
			msg = 'You can\'t go that way.'
			self.exceptionOccurred = True
			self.appendToCommandBuffer(sender, msg)
		except self.CommandException as e:
			self.exceptionOccurred = True


class West(Command):
	def __init__(self, game):
		super(West, self).__init__(game, 'west')

	def execute(self, args, sender):
		try:
			oldRoom = sender.room

			self.move(sender, 'west')

			msg = 'You leave west.'
			self.appendToCommandBuffer(sender, msg)

			if not sender.isAffectedBy('sneak'):
				for mobile in [mobile for mobile in self.game.mobiles if mobile.room == oldRoom]:
					msg = '{sender} leaves west.'.format(sender=sender)
					self.appendToCommandBuffer(mobile, msg)

				for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]:
					msg = '{sender} has arrived.'.format(sender=sender)
					self.appendToCommandBuffer(mobile, msg)

			sender.setLag(1)
		except self.NoExitsException as e:
			msg = 'You can\'t go that way.'
			self.exceptionOccurred = True
			self.appendToCommandBuffer(sender, msg)
		except self.CommandException as e:
			self.exceptionOccurred = True


class Up(Command):
	def __init__(self, game):
		super(Up, self).__init__(game, 'up')

	def execute(self, args, sender):
		try:
			oldRoom = sender.room

			self.move(sender, 'up')

			msg = 'You leave up.'
			self.appendToCommandBuffer(sender, msg)

			if not sender.isAffectedBy('sneak'):
				for mobile in [mobile for mobile in self.game.mobiles if mobile.room == oldRoom]:
					msg = '{sender} leaves up.'.format(sender=sender)
					self.appendToCommandBuffer(mobile, msg)

				for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]:
					msg = '{sender} has arrived.'.format(sender=sender)
					self.appendToCommandBuffer(mobile, msg)

			sender.setLag(1)
		except self.NoExitsException as e:
			msg = 'You can\'t go that way.'
			self.appendToCommandBuffer(sender, msg)
			self.exceptionOccurred = True
		except self.CommandException as e:
			self.exceptionOccurred = True


class Down(Command):
	def __init__(self, game):
		super(Down, self).__init__(game, 'down')

	def execute(self, args, sender):
		try:
			oldRoom = sender.room

			self.move(sender, 'down')

			msg = 'You leave down.'
			self.appendToCommandBuffer(sender, msg)

			if not sender.isAffectedBy('sneak'):
				for mobile in [mobile for mobile in self.game.mobiles if mobile.room == oldRoom]:
					msg = '{sender} leaves down.'.format(sender=sender)
					self.appendToCommandBuffer(mobile, msg)

				for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]:
					msg = '{sender} has arrived.'.format(sender=sender)
					self.appendToCommandBuffer(mobile, msg)

			sender.setLag(1)
		except self.NoExitsException as e:
			msg = 'You can\'t go that way.'
			self.appendToCommandBuffer(sender, msg)
			self.exceptionOccurred = True
		except self.CommandException as e:
			self.exceptionOccurred = True

commandList = [North, South, East, West, Up, Down, Kill, Flee]
