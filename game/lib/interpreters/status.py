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


class Who(Command):
	def __init__(self, game):
		super(Who, self).__init__(game, 'who')
		self.minPosition = Position.sleeping
		self.useInCombat = True

	def execute(self, args, config):
		sender = config['sender']

		whoBuf = ''

		for mobile in self.game.mobiles:
			whoBuf += '[{level:2} {charRace:10} {charClass:>10}] [ {clan} ] {linkdead}{name} {title}\n\r'.format(
				level=mobile.level,
				charRace=mobile.charRace,
				charClass=mobile.getStat('charClass'),
				clan=mobile.clan,
				name=mobile.getName(sender),  # FIX ME: should the name be visible when you are blinded?  probably not, right?
				title=mobile.title,
				linkdead='[LINKDEAD] ' if mobile.isLinkdead() else '[PLAYER] ' if mobile.client else '')

		sender.sendToClient(whoBuf)


class Look(Command):
	def __init__(self, game):
		super(Look, self).__init__(game, 'look')
		self.minPosition = Position.resting
		self.useInCombat = True

	def execute(self, args, config):
		sender = config['sender']
		sender.sendToClient('You look around.')
		return


		if len(args) == 0:
			if sender.isAffectedBy('blind'):
				sender.sendToClient('You can\'t see anything!')
				return

			sender.sendToClient('@u{name}@x\n\r@g{exits}@x\n\r{mobiles}\n\r{items}'.format(
				name=sender.room.name,
				exits=sender.room.exits,
				mobiles='\n\r'.join([mobile.getName(sender) for mobile in self.game.mobiles if mobile.room is sender.room and mobile is not sender]),
				items='\n\r'.join([item.getName(sender) for item in sender.room.items]))
			)
		else:
			if sender.isAffectedBy('blind'):
				sender.sendToClient('You don\'t see them here.')
				return

			targets = [mobile.name for mobile in self.game.mobiles if mobile.room is sender.room and utility.matchList(args[0], mobile.keywords)]
			if len(targets) == 0:
				sender.sendToClient('You don\'t see them here.')
			else:
				sender.sendToClient('It\'s {name}!  How about that!'.format(name=targets[0]))


class Affects(Command):
	def __init__(self, game):
		super(Affects, self).__init__(game, 'affects')
		self.minPosition = Position.sleeping
		self.useInCombat = True

	def execute(self, args, config):
		sender = config['sender']
		buf = 'Affects:\n\r'
		for a in sender.affects:
			buf += str(a) + '\n\r'
		sender.sendToClient(buf)


class Score(Command):
	def __init__(self, game):
		super(Score, self).__init__(game, 'score')
		self.minPosition = Position.sleeping
		self.useInCombat = True

	def execute(self, args, config):
		sender = config['sender']
		buf = 'Score:'
		buf += '\n\rDatabase ID: {id}'.format(id=sender.id)
		for s in sender.stats:
			if sender.stats[s]:
				buf += '\n\r{statName}: {stat}'.format(statName=s, stat=sender.stats[s])
		sender.sendToClient(buf)

class Commands(Command):
	def __init__(self, game):
		super(Commands, self).__init__(game, 'commands')
		self.minPosition = Position.sleeping
		self.useInCombat = True

	def execute(self, args, config):
		sender = config['sender']
		buf = 'Commands:\n\r'
		for commandObject in sender.commandInterpreter.commandInterpreters:
			buf += commandObject.__name__ + '\n\r'
		sender.sendToClient(buf)


commandList = [Who, Score, Affects, Look, Commands]
