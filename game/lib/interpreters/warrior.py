import random

import lib.combat as combat
import lib.affect as affect
from lib.interpreters.command import Command
from lib.interpreters.constants import Position


class DirtKick(Command):
	def __init__(self, game):
		super(DirtKick, self).__init__(game, 'dirtkick')

	def execute(self, args, sender):
		try:
			# Simple checks
			self.checkPosition(sender, [Position.standing,Position.fighting])

			if args:
				target = self.getTargetFromListByName(args[0], [mobile for mobile in self.game.mobiles if mobile.room == sender.room])
			elif sender.combat:
				target = sender.combat
			else:
				raise self.DefaultTargetNotFoundException()

			# Target checks
			self.notSelfTargetable(target, sender)
			self.isLegalCombatTarget(target)
			self.notAffectedBy(target, ['dirtkick','blind'])

			# self.simpleSuccessCheck(50)
			self.simpleSuccessCheck(100)

			# sender.setLag(1)
			sender.setLag(0)
			sender.startCombatWith(target)

			affect.Affect.factory('DirtKick', sender, target, 2)

			self.appendToCommandBuffer(sender, target.getCondition())
			self.appendToCommandBuffer(target, sender.getCondition())
		except self.SkillFailedException as e:
			self.commandBuffer = combat.doDamage(self.game, sender, 0, noun='kicked dirt', target=target, combatBuffer=self.commandBuffer)

			self.appendToCommandBuffer(sender, target.getCondition())
			self.appendToCommandBuffer(target, sender.getCondition())

			sender.setLag(1)
			sender.startCombatWith(target)
		except self.AffectException as e:
			msg = 'They are already blinded.'
			self.appendToCommandBuffer(sender, msg)
			self.exceptionOccurred = True
		except self.TargetNotFoundException as e:
			self.exceptionOccurred = True
		except self.DefaultTargetNotFoundException as e:
			msg = 'Dirt kick who?'
			self.appendToCommandBuffer(sender, msg)
			self.exceptionOccurred = True
		except self.CommandException as e:
			self.exceptionOccurred = True


class Trip(Command):
	def __init__(self, game):
		super(Trip, self).__init__(game, 'trip')

	def execute(self, args, sender):
		try:
			# Simple checks
			self.checkPosition(sender, [Position.standing,Position.fighting])

			if args:
				target = self.getTargetFromListByName(args[0], [mobile for mobile in self.game.mobiles if mobile.room == sender.room])
			elif sender.combat:
				target = sender.combat
			else:
				raise self.TargetNotFoundException()

			# Target checks
			self.notSelfTargetable(target, sender)
			self.isLegalCombatTarget(target)

			self.simpleSuccessCheck(0)

			sender.setLag(2)

			# Messaging
			msg = 'You trip {target} and they go down.'.format(target=target.getName(sender))
			self.appendToCommandBuffer(sender, msg)

			msg = '{sender} trips you and you go down.'.format(sender=sender.getName(target))
			self.appendToCommandBuffer(target, msg)

			for mobile in [mobile for mobile in self.game.mobiles if mobile.room == target.room and mobile != sender and mobile != target]:
				msg = '{sender} trips {target}.'.format(sender=sender.getName(mobile),target=target.getName(mobile))
				self.appendToCommandBuffer(mobile, msg)

			self.commandBuffer = combat.doDamage(self.game, sender, random.randint(1,10), noun='trip', target=target, combatBuffer=self.commandBuffer)

			self.appendToCommandBuffer(sender, target.getCondition())
			self.appendToCommandBuffer(target, sender.getCondition())

			sender.startCombatWith(target)
		except self.SelfTargetableException as e:
			self.exceptionOccurred = True
		except self.SkillFailedException as e:
			self.commandBuffer = combat.doDamage(self.game, sender, 0, noun='trip', target=target, combatBuffer=self.commandBuffer)

			self.appendToCommandBuffer(sender, target.getCondition())
			self.appendToCommandBuffer(target, sender.getCondition())

			sender.setLag(2)
			sender.startCombatWith(target)
		except self.TargetNotFoundException as e:
			msg = 'You trip over your own feet.'
			self.appendToCommandBuffer(sender, msg)
			self.exceptionOccurred = True
		except self.CommandException as e:
			self.appendToCommandBuffer(sender, repr(e))
			self.exceptionOccurred = True


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
		try:
			# Automatic checks
			self.checkPosition(sender, [Position.fighting, Position.standing])

			# Automatic targeting
			if args:
				target = self.getTargetFromListByName(args[0], [mobile for mobile in self.game.mobiles if mobile.room == sender.room])
			elif sender.combat:
				target = sender.combat
			else:
				raise self.TargetNotFoundException()

			# Target checks
			self.notSelfTargetable(target, sender)
			self.isLegalCombatTarget(target)

			# Manual checks
			if 'weapon' not in target.equipment or not target.equipment['weapon']:
				msg = ('They aren\'t wielding a weapon.')
				self.appendToCommandBuffer(sender, msg)
				return

			self.simpleSuccessCheck(0)

			msg = 'You disarm {target}!'.format(target=target.getName(sender))
			self.appendToCommandBuffer(sender, msg)

			msg = '{sender} disarms you!'.format(sender=sender.getName(target))
			self.appendToCommandBuffer(sender, msg)

			for mobile in [mobile for mobile in self.game.mobiles if mobile != sender and mobile != target]:
				msg = '{sender} disarms {target}!'.format(sender=sender.getName(mobile),target=target.getName(mobile))
				self.appendToCommandBuffer(mobile, msg)

			target.removeItem(target.equipment['weapon'])
		except self.DefaultTargetNotFoundException as e:
			msg = 'Dirt kick who?'
			self.appendToCommandBuffer(sender, msg)
			self.exceptionOccurred = True
		except TargetNotFoundException as e:
			self.appendToCommandBuffer()
			self.exceptionOccurred = True
		except self.CommandException as e:
			self.appendToCommandBuffer(sender, repr(e))
			self.exceptionOccurred = True
		else:
			senderBuf = 'You fail to disarm {target}.'.format(target=target.getName(sender))
			targetBuf = '{sender} tries to disarm you, but fails.'.format(sender=sender.getName(target))
			roomBuf = '{0} tries to disarm {1}, but fails.'

		sender.sendToClient(senderBuf)
		target.sendToClient(targetBuf)
		sender.game.sendCondition((lambda a: a.room == sender.room and a is not sender and a is not target), roomBuf, [sender, target])


class Kick(Command):
	def __init__(self, game):
		super(Kick, self).__init__(game, 'kick')
		self.canTarget = True
		self.requireTarget = True
		self.aggro = True
		self.useInCombat = True
		self.useWhileJustDied = False
		self.targetSelf = False

	def execute(self, args, config):
		sender = config['sender']
		target = config['target']

		damage = sender.level + random.randint(1, 10)

		combatBuffer = {}
		combatBuffer = combat.doDamage(self.game, sender, damage, noun='kick', target=target, combatBuffer=combatBuffer)
		combat.appendConditionsToCombatBuffer(combatBuffer)
		combat.sendCombatBuffer(self.game, combatBuffer)

		sender.setLag(3)


class Bash(Command):
	def __init__(self, game):
		super(Bash, self).__init__(game, 'bash')
		self.canTarget = True
		self.requireTarget = True
		self.aggro = True
		self.useInCombat = True
		self.useWhileJustDied = False
		self.targetSelf = False

	def execute(self, args, config):
		sender = config['sender']
		target = config['target']

		success = True if random.randint(0, 99) > 24 else False
		if success:
			senderBuf = 'You send {target} sprawling with a powerful bash!\n\r'.format(target=target.getName(sender))
			targetBuf = '{sender} sends you sprawling with a powerful bash!\n\r'.format(sender=sender.getName(target))
			roomBuf = '{0} sends {1} sprawling with a powerful bash!\n\r'

			damage = random.randint(10, 20)
			buf = combat.doDamage(sender, damage, 'bash', target)

			senderBuf += buf['sender'].format(target=target.getName(sender))
			targetBuf += buf['target'].format(name=sender.getName(target))
			roomBuf += buf['room']
		else:
			senderBuf = 'You fall flat on your face.'
			targetBuf = '{sender} falls flat on their face.'.format(sender=sender.getName(target))
			roomBuf = '{0} falls flat on their face.'

		sender.setLag(6)

		sender.sendToClient(senderBuf)
		target.sendToClient(targetBuf)
		sender.game.sendCondition((lambda a: a.room == sender.room and a is not sender and a is not target), roomBuf, [sender, target])

commandList = [Kick, Bash, DirtKick, Trip, Disarm, Berserk]
