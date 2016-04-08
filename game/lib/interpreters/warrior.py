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
				raise self.TargetNotFoundException()

			# Target checks
			self.isLegalCombatTarget(target)
			self.notAffectedBy(target, ['dirtkick','blind'])

			self.simpleSuccessCheck(50)

			sender.setLag(2)
			sender.startCombatWith(target)

			affect.Affect.factory('DirtKick', sender, target, 2)
		except self.SkillFailedException as e:
			msg = 'Your clumsy kicked dirt misses {target}.'.format(target=target.getName(sender))
			self.appendToCommandBuffer(sender, msg)

			msg = '{sender}\'s clumsy kicked dirt misses you.'.format(sender=sender.getName(target))
			self.appendToCommandBuffer(target, msg)

			for mobile in [mobile for mobile in self.game.mobiles if mobile.room == target.room and mobile != sender and mobile != target]:
				msg = '{sender}\'s clumsy kicked dirt misses {target}.'.format(sender=sender.getName(mobile),target=target.getName(mobile))
				self.appendToCommandBuffer(mobile, msg)

			sender.setLag(2)
			sender.startCombatWith(target)
		except self.AffectException as e:
			msg = 'They are already blinded.'
			self.appendToCommandBuffer(sender, msg)
			self.exceptionOccurred = True
		except self.TargetNotFoundException as e:
			msg = 'Dirt kick whom?'
			self.appendToCommandBuffer(sender, msg)
			self.exceptionOccurred = True
		except self.CommandException as e:
			self.exceptionOccurred = True


class Trip(Command):
	def __init__(self, game):
		super(Trip, self).__init__(game, 'trip')
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
			senderBuf = 'You trip {target} and they go down.'.format(target=target.getName(sender))
			targetBuf = '{sender} trips you and you go down.'.format(sender=sender.getName(target))
			roomBuf = '{0} trips {1} and they go down.'

			affect.Affect.factory('Stun', sender, target, 1)
		else:
			senderBuf = 'Your clumsy trip misses {target}.'.format(target=target.getName(sender))
			targetBuf = '{sender}\'s clumsy trip misses you.'.format(sender=sender.getName(target))
			roomBuf = '{0}\'s clumsy trip misses {1}.'

		sender.sendToClient(senderBuf)
		target.sendToClient(targetBuf)
		sender.game.sendCondition((lambda a: a.room == sender.room and a is not sender and a is not target), roomBuf, [sender, target])


class Berserk(Command):
	def __init__(self, game):
		super(Berserk, self).__init__(game, 'berserk')
		self.useInCombat = True
		self.useWhileJustDied = False

	def execute(self, args, config):
		sender = config['sender']

		if sender.isAffectedBy('berserk'):
			sender.sendToClient('You can\'t get any angrier!')
			return

		# success = True if random.randint(0, 99) > 24 else False
		success = True
		if success:
			sender.heal(25)
			affect.Affect.factory('Berserk', sender, sender, 5)
		else:
			sender.sendToClient('You fail to get mad.')


class Disarm(Command):
	def __init__(self, game):
		super(Disarm, self).__init__(game, 'disarm')
		self.canTarget = True
		self.requireTarget = True
		self.aggro = True
		self.useInCombat = True
		self.useWhileJustDied = False
		self.targetSelf = False

	def execute(self, args, config):
		sender = config['sender']
		target = config['target']

		if not target.equipment['weapon']:
			sender.sendToClient('They aren\'t wielding a weapon.')
			return

		success = True if random.randint(0, 99) > 24 else False
		if success:
			senderBuf = 'You disarm {target}!'.format(target=target.getName(sender))
			targetBuf = '{sender} disarms you!'.format(sender=sender.getName(target))
			roomBuf = '{0} disarms {1}!'

			target.inventory.append(target.equipment['weapon'])
			target.equipment['weapon'] = None
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
