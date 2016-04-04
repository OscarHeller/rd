import lib.utility as utility
from lib.interpreters.command import Command
from lib.interpreters.constants import Position, Range


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


class Say(Command):
	def __init__(self, game):
		super(Say, self).__init__(game, 'say')
		self.useInCombat = True
		self.minPosition = Position.resting

	def execute(self, args, config):
		sender = config['sender']

		saying = ' '.join(args)
		message = '@y{name} says \'{saying}\'@x'

		# I had to replace game.sendCondition with a list comprehension so I could have each separate mobile make their own call to getName
		targets = [mobile.sendToClient(message.format(
			name=sender.getName(mobile), saying=saying), comm=True) for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]

		sender.sendToClient('@yYou say \'{saying}\'@x'.format(saying=saying), comm=True)


class Yell(Command):
	def __init__(self, game):
		super(Yell, self).__init__(game, 'yell')
		self.useInCombat = True
		self.minPosition = Position.resting
		self.range = Range.area

	def execute(self, args, config):
		sender = config['sender']

		yelling = ' '.join(args)
		message = '@r{name} yells \'{yelling}\'@x'

		targets = [mobile.sendToClient(message.format(
			name=sender.getName(mobile), yelling=yelling), comm=True) for mobile in self.game.mobiles if mobile.room.area == sender.room.area and mobile != sender]

		# self.game.sendCondition(
		# 	(lambda a: a is not sender and a.room.area is sender.room.area),
		# 	'@r{{0}} yells \'{args}\'@x'.format(args=' '.join(args)), [sender])

		sender.sendToClient('@rYou yell \'{yelling}\'@x'.format(yelling=yelling), comm=True)


class Tell(Command):
	def __init__(self, game):
		super(Tell, self).__init__(game, 'tell')
		self.useInCombat = True
		self.minPosition = Position.resting

	def execute(self, args, config):
		sender = config['sender']

		message = args[1:]

		if not message:
			sender.sendToClient('What do you want to tell them?')
			return

		targets = [ mobile for mobile in self.game.mobiles if mobile.client and utility.match( args[0], mobile.getName() ) ]
		if not targets:
			sender.sendToClient('You can\'t find them.')
			return
		else:
			target = targets[0]

		target.sendToClient('@b{name} tells you \'{message}\'@x'.format(name=sender.getName(target), message=' '.join(message)), comm=True)
		sender.sendToClient('@bYou tell {name} \'{message}\'@x'.format(name=target.getName(sender), message=' '.join(message)), comm=True)

commandList = [Say, Yell, Tell]
