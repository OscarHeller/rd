import random

import lib.combat as combat
import lib.affect as affect
from lib.interpreters.command import Command
from lib.interpreters.constants import Position


class DirtKick(Command):
	def __init__(self, game):
		super(DirtKick, self).__init__(game, 'dirtkick')

	def execute(self, args, sender):
		# Simple checks
		self.test(self.checkPosition, (sender, [Position.standing,Position.fighting]))

		target = self.test(self.getCombatTargetByArgs, (sender, args))

		# Target checks
		self.test(self.notSelfTargetable, (target, sender))
		self.test(self.isLegalCombatTarget, (target))
		self.test(self.notAffectedBy, (target, ['dirtkick','blind']), override='They are already blinded.')

		# self.simpleSuccessCheck(50)
		sender.startCombatWith(target)
		self.test(self.simpleSuccessCheck, 100)

		sender.setLag(1)

		affect.Affect.factory('DirtKick', sender, target, 2)


class Trip(Command):
	def __init__(self, game):
		super(Trip, self).__init__(game, 'trip')

	def execute(self, args, sender):
		# Simple checks
		self.test(self.checkPosition, (sender, [Position.standing,Position.fighting]))

		target = self.test(self.getCombatTargetByArgs, (sender, args))

		# Target checks
		self.test(self.notSelfTargetable, (target, sender))
		self.test(self.isLegalCombatTarget, (target))

		try:
			self.test(self.simpleSuccessCheck, 0)
		except self.CommandException as e:
			sender.startCombatWith(target)

			self.commandBuffer = combat.doDamage(self.game, sender, 0, noun='trip', target=target, combatBuffer=self.commandBuffer)
			return

		sender.setLag(2)

		sender.startCombatWith(target)
		# Messaging
		msg = 'You trip {target} and they go down.'.format(target=target.getName(sender))
		self.appendToCommandBuffer(sender, msg)

		msg = '{sender} trips you and you go down.'.format(sender=sender.getName(target))
		self.appendToCommandBuffer(target, msg)

		for mobile in sender.inRoomExcept([sender,target]):
			msg = '{sender} trips {target}.'.format(sender=sender.getName(mobile),target=target.getName(mobile))
			self.appendToCommandBuffer(mobile, msg)

		self.commandBuffer = combat.doDamage(self.game, sender, random.randint(3,5), noun='trip', target=target, combatBuffer=self.commandBuffer)



class Berserk(Command):
	def __init__(self, game):
		super(Berserk, self).__init__(game, 'berserk')

	def execute(self, args, sender):
		self.test(self.checkPosition, (sender, [Position.sleeping, Position.standing]))
		self.test(self.notAffectedBy, (sender, 'berserk'), override='You can\'t get any angrier.')

		sender.heal(25)
		affect.Affect.factory('Berserk', sender, sender, 5)


class Disarm(Command):
	def __init__(self, game):
		super(Disarm, self).__init__(game, 'disarm')

	def execute(self, args, sender):
		# Automatic checks
		self.test(self.checkPosition, (sender, [Position.standing,Position.fighting]))

		target = self.test(self.getCombatTargetByArgs, (sender, args))

		# Target checks
		self.test(self.notSelfTargetable, (target, sender))
		self.test(self.isLegalCombatTarget, (target))

		# Manual checks
		if 'weapon' not in target.equipment or not target.equipment['weapon']:
			self.error('They aren\'t wielding a weapon.')

		try:
			self.test(self.simpleSuccessCheck, 100)
		except self.CommandException as e:
			msg = 'You fail to disarm {target}.'.format(target=target.getName(sender))
			self.appendToCommandBuffer(sender, msg)

			msg = '{sender} tries to disarm you, but fails.'.format(sender=sender.getName(target))
			self.appendToCommandBuffer(target, msg)

			for mobile in sender.inRoomExcept([sender,target]):
				msg = '{0} tries to disarm {1}, but fails.'
				self.appendToCommandBuffer(mobile, msg)

			sender.startCombatWith(target)
			return

		sender.startCombatWith(target)

		msg = 'You disarm {target}!'.format(target=target.getName(sender))
		self.appendToCommandBuffer(sender, msg)

		msg = '{sender} disarms you!'.format(sender=sender.getName(target))
		self.appendToCommandBuffer(target, msg)

		for mobile in sender.inRoomExcept([sender,target]):
			msg = '{sender} disarms {target}!'.format(sender=sender.getName(mobile),target=target.getName(mobile))
			self.appendToCommandBuffer(mobile, msg)
		target.removeItem(target.equipment['weapon'])


class Kick(Command):
	def __init__(self, game):
		super(Kick, self).__init__(game, 'kick')

	def execute(self, args, sender):
		# Automatic checks
		self.test(self.checkPosition, (sender, [Position.standing,Position.fighting]))

		target = self.test(self.getCombatTargetByArgs, (sender, args))

		# Target checks
		self.test(self.notSelfTargetable, (target, sender))
		self.test(self.isLegalCombatTarget, (target))

		damage = random.randint(10,25)

		sender.startCombatWith(target)
		self.commandBuffer = combat.doDamage(self.game, sender, damage, noun='kick', target=target, combatBuffer=self.commandBuffer)

		sender.setLag(1)


class Bash(Command):
	def __init__(self, game):
		super(Bash, self).__init__(game, 'bash')

	def execute(self, args, sender):
		# Automatic checks
		self.test(self.checkPosition, (sender, [Position.standing,Position.fighting]))

		target = self.test(self.getCombatTargetByArgs, (sender, args))

		# Target checks
		self.test(self.notSelfTargetable, (target, sender))
		self.test(self.isLegalCombatTarget, (target))

		try:
			self.test(self.simpleSuccessCheck, 100)
		except self.CommandException as e:
			sender.startCombatWith(target)

			msg = 'You fall flat on your face.'
			self.appendToCommandBuffer(sender, msg)

			for mobile in sender.inRoomExcept(sender):
				msg = '{sender} falls flat on their face.'.format(sender=sender.getName(target))
				self.appendToCommandBuffer(mobile, msg)

			sender.setLag(2)
			return

		sender.startCombatWith(target)
		sender.setLag(2)

		msg = 'You send {target} sprawling with a powerful bash!'.format(target=target.getName(sender))
		self.appendToCommandBuffer(sender, msg)

		msg = '{sender} sends you sprawling with a powerful bash!'.format(sender=sender.getName(target))
		self.appendToCommandBuffer(target, msg)

		for mobile in sender.inRoomExcept([sender,target]):
			msg = '{sender} sends {target} sprawling with a powerful bash!'.format(sender=sender.getName(mobile),target=target.getName(mobile))
			self.appendToCommandBuffer(mobile, msg)

		damage = random.randint(5,10)

		self.combatBuffer = combat.doDamage(self.game, sender, damage, noun='bash', target=target, combatBuffer=self.commandBuffer)

commandList = [Kick, Bash, DirtKick, Trip, Disarm, Berserk]
