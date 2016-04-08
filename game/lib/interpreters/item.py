import lib.utility as utility
from lib.interpreters.command import Command
from lib.interpreters.constants import Position
import lib.interpreters.helper as helper


class Get(Command):
	def __init__(self, game):
		super(Get, self).__init__(game, 'get')

	def execute(self, args, sender):
		try:
			# Preliminary checks
			self.checkPosition(sender, [Position.standing, Position.resting, Position.fighting])

			# Automatic targeting
			item = self.getTargetFromListByName(args[0], sender.room.items)

			# Game manipulation
			sender.room.items.remove(item)
			sender.inventory.append(item)

			# Messaging
			msg = 'You get {item}.'.format(item=item.getName(sender))
			self.appendToCommandBuffer(sender, msg)

			for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile is not sender]:
				msg = '{sender} gets {item}.'.format(sender=sender.getName(mobile),item=item.getName(mobile))
				self.appendToCommandBuffer(mobile, msg)
		except self.TargetNotFoundException as e:
			msg = 'You don\'t see that here.'
			self.appendToCommandBuffer(sender, msg)
		except self.CommandException as e:
			return


class Drop(Command):
	def __init__(self, game):
		super(Drop, self).__init__(game, 'drop')

	def execute(self, args, sender):
		try:
			# Preliminary checks
			self.checkPosition(sender, [Position.standing, Position.resting, Position.fighting])

			# Automatic targeting
			item = self.getTargetFromListByName(args[0], sender.inventory)

			# Game manipulation
			sender.inventory.remove(item)
			sender.room.items.append(item)

			# Messaging
			msg = 'You drop {item}.'.format(item=item.getName(sender))
			self.appendToCommandBuffer(sender, msg)

			for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile is not sender]:
				msg = '{sender} drops {item}.'.format(sender=sender.getName(mobile),item=item.getName(mobile))
				self.appendToCommandBuffer(mobile, msg)
		except self.TargetNotFoundException as e:
			msg = 'You\'re not carrying that.'
			self.appendToCommandBuffer(sender, msg)
		except self.CommandException as e:
			return


class Wear(Command):
	def __init__(self, game):
		super(Wear, self).__init__(game, 'wear')

	def execute(self, args, sender):
		try:
			# Preliminary checks
			self.checkPosition(sender, [Position.standing, Position.resting, Position.fighting])

			# Automatic targeting
			item = self.getTargetFromListByName(args[0], sender.inventory)

			if not item.wear:
				msg = 'You can\'t wear that!'
				self.appendToCommandBuffer(sender, msg)
				return

			# Game manipulation
			if item.wear in sender.equipment and sender.equipment[item.wear]:
				sender.inventory.append(sender.equipment[item.wear])

				msg = 'You stop using {item}.'.format(item=sender.equipment[item.wear].getName(sender))
				self.appendToCommandBuffer(sender, msg)

			sender.equipment[item.wear] = item
			sender.inventory.remove(item)


			msg = 'You now wear {item}.'.format(item=item.getName(sender))
			self.appendToCommandBuffer(sender, msg)
		except self.TargetNotFoundException as e:
			msg = 'You\'re not carrying that.'
			self.appendToCommandBuffer(sender, msg)
		except self.CommandException as e:
			return


class Remove(Command):
	def __init__(self, game):
		super(Remove, self).__init__(game, 'remove')

	def execute(self, args, sender):
		try:
			# Preliminary checks
			self.checkPosition(sender, [Position.standing, Position.resting, Position.fighting])

			# Automatic targeting
			item = self.getTargetFromListByName(args[0], sender.equipment.values())

			msg = 'You remove {item}.'.format(item=item.getName(sender))
			self.appendToCommandBuffer(sender, msg)

			sender.removeItem(item)
		except self.TargetNotFoundException as e:
			msg = 'You\'re not wearing that.'
			self.appendToCommandBuffer(sender, msg)
		except self.CommandException as e:
			return

commandList = [Wear, Get, Drop, Remove]
