from lib.interpreters.constants import Range, Position


class Command(object):
	def __init__(self, game, key):
		self.aggro = False
		self.game = game
		self.canTarget = False
		self.requireTarget = False
		self.useInCombat = False
		self.useWhileJustDied = True
		self.targetSelf = True
		self.range = Range.room
		self.minPosition = Position.standing
		self.key = key

	def execute(self, args, config):
		print ('BUG: This command has no overriding execute function.')
