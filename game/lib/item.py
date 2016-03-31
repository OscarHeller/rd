import lib.utility as utility
from lib.interpreters.command import Command
from lib.interpreters.constants import Position

class Item:

	def __init__(self, config):
		self.name = config['name']
		# self.longName = config['longName']
		# self.description = config['description']
		self.keywords = config['keywords'] if 'keywords' in config else name
		self.wear = config['wear'] if 'wear' in config else None
		self.stats = config['stats'] if 'stats' in config else {}
		self.noun = config['noun'] if 'noun' in config else 'hit'
		self.roll = config['roll'] if 'roll' in config else 0
		self.commandInterpreters = []

		if 'description' in self.stats:
			self.commandInterpreters.append(Examine)


	def getRoll(self):
		return int(self.roll)

	def getNoun(self):
		return self.noun

	def getStat(self, stat):
		if stat in self.stats:
			return self.stats[stat]
		else:
			return 0

	def getRoomDesc(self, looker=False):
		desc = self.getName(looker).capitalize()

		desc += ' lies here.'

		return desc

	def getName(self, looker=False):
		return self.name

	def getCommandInterpreters(self):
		return self.commandInterpreters

class Examine(Command):
	def __init__(self, game):
		super(Examine, self).__init__(game, 'examine')
		self.useInCombat = True
		self.minPosition = Position.resting

	def execute(self, args, config):
		sender = config['sender']
		items = sender.room.items

		if len(args) <= 0:
			sender.sendToClient('Examine what?')
			return

		for item in items:
			if utility.matchList(args[0], item.keywords):
				if 'description' in item.stats:
					sender.sendToClient(item.stats['description'])
					return
		sender.sendToClient('You don\'t see that here.')