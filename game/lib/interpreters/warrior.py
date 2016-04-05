import random

import lib.combat as combat
import lib.affect as affect
from lib.interpreters.command import Command
from lib.interpreters.constants import Position


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


class DirtKick(Command):
	def __init__(self, game):
		super(DirtKick, self).__init__(game, 'dirtkick')
		self.canTarget = True
		self.requireTarget = True
		self.aggro = True
		self.useInCombat = True
		self.useWhileJustDied = False
		self.targetSelf = False

	def execute(self, args, config):
		sender = config['sender']
		target = config['target']

		if target.isAffectedBy('dirtkick') or target.isAffectedBy('blind'):
			sender.sendToClient('They are already blinded.')
			return

		success = True if random.randint(0, 99) > 50 else False
		if success:
			affect.Affect.factory('DirtKick', sender, target, 2)
		else:
			senderBuf = 'Your clumsy kicked dirt misses {target}.'.format(target=target.getName(sender))
			targetBuf = '{sender}\'s clumsy kicked dirt misses you.'.format(sender=sender.getName(sender))
			roomBuf = '{0}\'s clumsy kicked dirt misses {1}.'

			sender.sendToClient(senderBuf)
			target.sendToClient(targetBuf)
			sender.game.sendCondition((lambda a: a.room == sender.room and a is not sender and a is not target), roomBuf, [sender, target])


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
		buf = combat.doDamage(sender, damage, 'kick', target)
		sender.sendToClient(buf['sender'].format(target=target.getName(sender)))
		sender.game.sendCondition(
			(lambda a: a.room == sender.room and a is not sender and a is not target), buf['room'], [sender, target])
		target.sendToClient(buf['target'].format(name=sender.getName(target)))
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
