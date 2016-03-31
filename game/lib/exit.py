class Exit:
	def __init__(self, key, destination):
		self.key = key
		self.destination = destination

	def __repr__(self):
		return '({key}: {destination})'.format(key=self.key, destination=self.destination.name)
