class Room:
	def __init__(self, game, config):
		self.name = config['name'] if 'name' in config else 'NO NAME'
		self.desc = config['description'] if 'description' in config else ''
		self.bg = config['bg'] if 'bg' in config else None
		self.stats = config['stats'] if 'stats' in config else {}
		self.exits = []
		self.items = []
		self.commandInterpreters = []
		self.__repr__ = self.__str__
		self.game = game
		self.area = None

	def __str__(self):
		return '{name}: {exits}'.format(name=self.name, exits=', '.join([str(exit) for exit in self.exits]))

	def getIndex(self):
		for index, room in enumerate(self.game.rooms):
			if self == room:
				return index

	def getExit(self, direction):
		for exit in self.exits:
			if exit.key == direction:
				return exit
		return None

	def getStat(self, stat):
		if stat in self.stats:
			return self.stats[stat]
		else:
			return False

	def getCommandInterpreters (self):
		itemCommands = []
		for item in self.items:
			itemCommands += item.getCommandInterpreters()
		return self.commandInterpreters + itemCommands

	def getName(self, looker=None):
		if looker and (looker.isAffectedBy('blind') or looker.isAffectedBy('dirtkick')):
			return "You can't see a thing!"
		else:
			return self.name

	def getDesc(self, looker=None):
		if looker and (looker.isAffectedBy('blind') or looker.isAffectedBy('dirtkick')):
			return "Everything is pitch black."
		else:
			return self.desc

	def getBG(self, looker=None):
		if looker and (looker.isAffectedBy('blind') or looker.isAffectedBy('dirtkick')):
			return ""
		else:
			return self.bg