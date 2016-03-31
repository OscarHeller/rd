import lib.utility as utility
from lib.interpreters.command import Command
from lib.interpreters.constants import Position

# FIX ME: Helper function to get items? Right now anything getting an item has 'false' as target
# and has to get it from args[0]. Range doesn't do anything.


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


class Get(Command):
	def __init__(self, game):
		super(Get, self).__init__(game, 'get')
		self.useInCombat = True
		self.minPosition = Position.resting

	def execute(self, args, config):
		sender = config['sender']
		items = sender.room.items

		for item in items:
			if utility.matchList(args[0], item.keywords):
				sender.room.items.remove(item)
				sender.inventory.append(item)
				sender.sendToClient('You get {item}.'.format(item=item.getName(sender)))
				sender.game.sendCondition(
					(lambda a: a.room == sender.room and a is not sender), '{0} gets {1}', [sender, item])
				return

		sender.sendToClient('You don\'t see that here.')


class Inventory(Command):
	def __init__(self, game):
		super(Inventory, self).__init__(game, 'inventory')
		self.useInCombat = True
		self.minPosition = Position.sleeping

	def execute(self, args, config):
		sender = config['sender']

		buf = 'Inventory:\n\r'
		for item in sender.inventory:
			buf += item.getName(sender) + '\n\r'

		sender.sendToClient(buf)


class Drop(Command):
	def __init__(self, game):
		super(Drop, self).__init__(game, 'drop')
		self.useInCombat = True
		self.minPosition = Position.resting

	def execute(self, args, config):
		sender = config['sender']
		inventory = sender.inventory

		for item in inventory:
			if utility.matchList(args[0], item.keywords):
				sender.inventory.remove(item)
				sender.room.items.append(item)
				sender.sendToClient('You drop {item}.'.format(item=item.getName(sender)))
				sender.game.sendCondition(
					(lambda a: a.room == sender.room and a is not sender), '{0} drops {1}', [sender, item])
				return
		sender.sendToClient('You don\'t have that.')


class Wear(Command):
	def __init__(self, game):
		super(Wear, self).__init__(game, 'wear')
		self.useInCombat = True
		self.minPosition = Position.resting

	def execute(self, args, config):
		sender = config['sender']

		for item in sender.inventory:
			if utility.matchList(args[0], item.keywords):
				# if item already in eq slot, remove it first
				if not item.wear:
					sender.sendToClient('You can\'t wear that!')
					return
				if item.wear in sender.equipment and sender.equipment[item.wear]:
					sender.inventory.append(sender.equipment[item.wear])
					sender.sendToClient('You stop using {item}.'.format(item=sender.equipment[item.wear].getName(sender)))
				# put item in eq slot, remove from inventory
				sender.equipment[item.wear] = item
				sender.inventory.remove(item)
				sender.sendToClient('You now wear {item}.'.format(item=item.getName(sender)))
				return

		sender.sendToClient('You don\'t have that.')


class Remove(Command):
	def __init__(self, game):
		super(Remove, self).__init__(game, 'remove')

	def execute(self, args, config):
		sender = config['sender']

		for e in sender.equipment:
			if sender.equipment[e] and utility.matchList(args[0], sender.equipment[e].keywords):
				sender.inventory.append(sender.equipment[e])
				buf = 'You remove {item}.'.format(item=sender.equipment[e].getName(sender))
				sender.equipment[e] = None
				sender.sendToClient(buf)
				return
		sender.sendToClient('You aren\'t wearing that.')


class Equipment(Command):
	def __init__(self, game):
		super(Equipment, self).__init__(game, 'equipment')
		self.useInCombat = True
		self.minPosition = Position.sleeping

	def execute(self, args, config):
		sender = config['sender']
		buf = 'You are wearing:\n\r'
		for e in sender.equipment:
			if sender.equipment[e]:
				print e, sender.equipment[e]
				buf += '{slot} : {item}'.format(slot=e, item=sender.equipment[e].getName(sender))
		sender.sendToClient(buf)

commandList = [Wear, Get, Drop, Remove, Inventory, Equipment]
