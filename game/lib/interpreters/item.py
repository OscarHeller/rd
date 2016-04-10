import lib.utility as utility
from lib.interpreters.command import Command
from lib.interpreters.constants import Position


class Get(Command):
	def __init__(self, game):
		super(Get, self).__init__(game, 'get')

	def execute(self, args, sender):
		# Preliminary checks
		self.test(self.checkPosition, (sender, [Position.standing, Position.resting, Position.fighting]))
		self.test(self.hasAtLeastOneArgument, args, override='Get what?')

		# Automatic targeting
		item = self.test(self.getItemFromListByName, (args[0], sender.room.items))

		# Game manipulation
		sender.room.items.remove(item)
		sender.inventory.append(item)

		# Messaging
		msg = 'You get {item}.'.format(item=item.getName(sender))
		self.appendToCommandBuffer(sender, msg)

		for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile is not sender]:
			msg = '{sender} gets {item}.'.format(sender=sender.getName(mobile),item=item.getName(mobile))
			self.appendToCommandBuffer(mobile, msg)


class Drop(Command):
	def __init__(self, game):
		super(Drop, self).__init__(game, 'drop')

	def execute(self, args, sender):
		# Preliminary checks
		self.test(self.checkPosition, (sender, [Position.standing, Position.resting, Position.fighting]))
		self.test(self.hasAtLeastOneArgument, args, override='Drop what?')

		# Automatic targeting
		item = self.test(self.getItemFromListByName, (args[0], sender.inventory), override='You\'re not carrying that.')

		# Game manipulation
		sender.inventory.remove(item)
		sender.room.items.append(item)

		# Messaging
		msg = 'You drop {item}.'.format(item=item.getName(sender))
		self.appendToCommandBuffer(sender, msg)

		for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile is not sender]:
			msg = '{sender} drops {item}.'.format(sender=sender.getName(mobile),item=item.getName(mobile))
			self.appendToCommandBuffer(mobile, msg)


class Wear(Command):
	def __init__(self, game):
		super(Wear, self).__init__(game, 'wear')

	def execute(self, args, sender):
		# Preliminary checks
		self.test(self.checkPosition, (sender, [Position.standing, Position.resting, Position.fighting]))

		# Automatic targeting
		item = self.test(self.getItemFromListByName, (args[0], sender.inventory), override='You\'re not carrying that.')

		if not item.wear:
			self.error = 'You can\'t wear that!'

		# Game manipulation
		if item.wear in sender.equipment and sender.equipment[item.wear]:
			oldItem = sender.equipment[item.wear]
			sender.removeItem(oldItem)

			msg = 'You stop using {item}.'.format(item=oldItem.getName(sender))
			self.appendToCommandBuffer(sender, msg)

			for mobile in sender.inRoomExcept(sender):
				msg = '{sender} stops using {item}.'.format(sender=sender.getName(mobile),item=oldItem.getName(mobile))

		sender.equipment[item.wear] = item
		sender.inventory.remove(item)


		msg = 'You wear {item}.'.format(item=item.getName(sender))
		self.appendToCommandBuffer(sender, msg)

		for mobile in sender.inRoomExcept(sender):
			msg = '{sender} wears {item}.'.format(sender=sender.getName(mobile),item=item.getName(mobile))
			self.appendToCommandBuffer(mobile, msg)


class Remove(Command):
	def __init__(self, game):
		super(Remove, self).__init__(game, 'remove')

	def execute(self, args, sender):
		# Preliminary checks
		self.test(self.checkPosition, (sender, [Position.standing, Position.resting, Position.fighting]))

		# Automatic targeting
		item = self.test(self.getItemFromListByName, (args[0], sender.equipment.values()), override='You\'re not wearing that.')

		msg = 'You remove {item}.'.format(item=item.getName(sender))
		self.appendToCommandBuffer(sender, msg)

		for mobile in sender.inRoomExcept(sender):
			msg = '{sender} stops wearing {item}.'.format(sender=sender.getName(mobile),item=item.getName(mobile))
			self.appendToCommandBuffer(mobile, msg)

		sender.removeItem(item)

commandList = [Wear, Get, Drop, Remove]
