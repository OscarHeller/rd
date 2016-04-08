import lib.utility as utility
from lib.interpreters.command import Command
from lib.interpreters.constants import Position, Range


class Say(Command):
	def __init__(self, game):
		super(Say, self).__init__(game, 'say', comm=True)

	def execute(self, args, sender):
		try:
			# Preliminary checks
			self.checkPosition(sender, [Position.standing, Position.resting, Position.fighting])

			saying = ' '.join(args)

			for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]:
				msg = '@y{name} says \'{saying}\'@x'.format(name=sender.getName(mobile),saying=saying)
				self.appendToCommandBuffer(mobile, msg)

			msg = '@yYou say \'{saying}\'@x'.format(saying=saying)
			self.appendToCommandBuffer(sender, msg)
		except self.CommandException as e:
			self.exceptionOccurred = True


class Yell(Command):
	def __init__(self, game):
		super(Yell, self).__init__(game, 'yell', comm=True)

	def execute(self, args, sender):
		try:
			# Preliminary checks
			self.checkPosition(sender, [Position.standing, Position.resting, Position.fighting])

			saying = ' '.join(args)

			for mobile in [mobile for mobile in self.game.mobiles if mobile.room.area == sender.room.area and mobile != sender]:
				msg = '@r{name} yells \'{saying}\'@x'.format(name=sender.getName(mobile),saying=saying)
				self.appendToCommandBuffer(mobile, msg)

			msg = '@rYou yell \'{saying}\'@x'.format(saying=saying)
			self.appendToCommandBuffer(sender, msg)
		except self.CommandException as e:
			self.exceptionOccurred = True


class Tell(Command):
	def __init__(self, game):
		super(Tell, self).__init__(game, 'tell', comm=True)

	def execute(self, args, sender):
		try:
			# Preliminary checks
			self.checkPosition(sender, [Position.standing, Position.resting, Position.fighting])

			target = self.getTargetFromListByName(args[0], [mobile for mobile in self.game.mobiles if mobile.is_player])

			message = args[1:]

			if not message:
				self.appendToCommandBuffer(sender, 'What do you want to tell them?')
				return

			saying = ' '.join(message)

			msg = '@mYou tell {name} \'@y{saying}@x\'@x'.format(name=target.getName(sender),saying=saying)
			self.appendToCommandBuffer(sender, msg)

			msg = '@m{name} tells you \'@y{saying}@x\'@x'.format(name=sender.getName(target),saying=saying)
			self.appendToCommandBuffer(target, msg)
		except self.TargetNotFoundException as e:
			msg = 'You can\'t find them.'
			self.appendToCommandBuffer(sender, msg)
			self.exceptionOccurred = True
		except self.CommandException as e:
			self.exceptionOccurred = True

commandList = [Say, Yell, Tell]
