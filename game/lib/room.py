class Room:
	def __init__(self, game, config):
		self.name = config['name'] if 'name' in config else 'NO NAME'
		self.desc = config['description'] if 'description' in config else ''
		self.bg = config['bg'] if 'bg' in config else None
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

	def getCommandInterpreters (self):
		itemCommands = []
		for item in self.items:
			itemCommands += item.getCommandInterpreters()
		return self.commandInterpreters + itemCommands