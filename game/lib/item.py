import lib.utility as utility
from lib.interpreters.command import Command
from lib.interpreters.constants import Position

class Item:

	def __init__(self, config):
		self.name = config['name']
		# self.longName = config['longName']
		# self.description = config['description']
		self.id = config['_id'] if '_id' in config else 'NA'
		self.keywords = config['keywords'] if 'keywords' in config else self.name
		self.wear = config['wear'] if 'wear' in config else None
		self.stats = config['stats'] if 'stats' in config else {}
		self.noun = config['noun'] if 'noun' in config else 'hit'
		self.roll = config['roll'] if 'roll' in config else 0
		self.commandInterpreters = []

	def getRoll(self):
		return int(self.roll)

	def getNoun(self):
		return self.noun

	def getStat(self, stat):
		if stat in self.stats:
			return self.stats[stat]
		else:
			return None

	def getRoomDesc(self, looker=False):
		desc = self.getName(looker).capitalize()

		desc += ' lies here.'

		return desc

	def getName(self, looker=False):
		#if looker and looker.
		return self.name