REFRESHABLE = True
NOT_REFRESHABLE = False

FRIENDLY = True
NOT_FRIENDLY = False

VISIBLE = True
NOT_VISIBLE = False

class Affect(object):
	def __init__(self, name, caster, target, duration, refreshable, friendly):
		if not target:
			assert 0, 'Affect must have target.'

		self.name = 'unnamed affect' if not name else name
		self.target = target
		self.caster = caster
		self.game = target.game
		self.refreshable = refreshable
		self.friendly = friendly
		self.stats = {}

		# Convert duration (in seconds) to duration (in game cycles)
		self.duration = duration / self.game.interval

		if not self.refreshable and self.target.isAffectedBy(self.name):
			self.caster.sendToClient('{target} is already affected by {affect}'.format(target=self.target.name, affect=self.name))
		elif self.refreshable and self.target.isAffectedBy(self.name):
			# Refresh it
			self.refresh()
		else:
			# Apply it
			self.apply()

			# Send the affect to its target
			self.target.sendAffectsToClient()

	def __str__(self):
		return '{name}: {duration}s (from {caster})'.format(name=self.name, duration=self.duration, caster=self.caster.name)

	def refresh(self):
		existingAffect = self.target.isAffectedBy(self.name)
		existingAffect.duration = self.duration

	def getStat(self, stat):
		if stat in self.stats:
			return self.stats[stat]
		else:
			return None

	def apply(self):
		self.target.affects.append(self)
		self.target.sendToClient('You are affected by {name}.'.format(name=self.name))

		for mobile in self.target.inRoomExcept(self.target):
			mobile.sendToClient('{target} is affected by {name}.'.format(target=self.target,name=self.name))

	def wear(self):
		self.target.affects.remove(self)
		self.target.sendToClient('!{name}!'.format(name=self.name))

		for mobile in self.target.inRoomExcept(self.target):
			mobile.sendToClient('{target} is no longer affected by {name}.'.format(target=self.target,name=self.name))

	def update(self, amount):
		self.duration -= amount
		if self.duration <= 0:
			self.wear()

		# Send to target
		self.target.sendAffectsToClient()

	@staticmethod
	def factory(type, caster, target, duration):
		if type == 'Berserk':
			return Berserk(caster, target, duration)
		if type == 'Guardian':
			return Guardian(caster, target, duration)
		if type == 'Blind':
			return Blind(caster, target, duration)
		if type == 'DirtKick':
			return DirtKick(caster, target, duration)
		if type == 'Nervous':
			return Nervous(caster, target, duration)
		if type == 'JustDied':
			return JustDied(caster, target, duration)
		if type == 'Sneak':
			return Sneak(caster, target, duration)
		if type == 'Stun':
			return Stun(caster, target, duration)
		assert 0, "Invalid affect creation: " + type


class Berserk(Affect):
	def __init__(self, caster, target, duration):
		super(Berserk, self).__init__('berserk', caster, target, duration, NOT_REFRESHABLE, FRIENDLY)
		self.stats = { 'damage': 50, 'defense': -20 }

	def apply(self):
		self.target.affects.append(self)
		self.target.sendToClient('Your pulse races as you are consumed by rage!')
		for mobile in self.target.inRoomExcept(self.target):
			mobile.sendToClient('{target} gets a wild look in their eyes!'.format(target=self.target))

	def wear(self):
		self.target.affects.remove(self)
		self.target.sendToClient('You feel your pulse slow down.')

class Guardian(Affect):
	def __init__(self, caster, target, duration):
		super(Guardian, self).__init__('guardian', caster, target, duration, NOT_REFRESHABLE, FRIENDLY)
		self.stats = { 'defense': 50, 'damage': -20 }

	def apply(self):
		self.target.affects.append(self)
		self.target.sendToClient('You adopt the constant vigilance of a guardian.')
		for mobile in self.target.inRoomExcept(self.target):
			mobile.sendToClient('{target} becomes serene, yet watchful.'.format(target=self.target))

	def wear(self):
		self.target.affects.remove(self)
		self.target.sendToClient('You feel less alert, less aware.')

class Blind(Affect):
	def __init__(self, caster, target, duration):
		super(Blind, self).__init__('blind', caster, target, duration, NOT_REFRESHABLE, NOT_FRIENDLY)
		self.stats = { 'hitroll': -5, 'defense': -5 }

	def apply(self):
		self.target.affects.append(self)
		self.target.sendToClient('You are blinded!')
		for mobile in self.target.inRoomExcept(self.target):
			mobile.sendToClient('{target} appears to be blinded!'.format(target=self.target))

	def wear(self):
		self.target.affects.remove(self)
		self.target.sendToClient('You are no longer blinded.')
		for mobile in self.target.inRoomExcept(self.target):
			mobile.sendToClient('{target} is no longer blinded.'.format(target=self.target))


class DirtKick(Affect):
	def __init__(self, caster, target, duration):
		super(DirtKick, self).__init__('dirtkick', caster, target, duration, NOT_REFRESHABLE, NOT_FRIENDLY)
		self.stats = { 'hitroll': -5, 'defense': -5 }

	def apply(self):
		self.target.affects.append(self)
		self.target.sendToClient('You are blinded by the dirt in your eyes!')
		for mobile in self.target.inRoomExcept(self.target):
			mobile.sendToClient('{target} is blinded by the dirt in their eyes!'.format(target=self.target))

	def wear(self):
		self.target.affects.remove(self)
		self.target.sendToClient('You rub the dirt out of your eyes.')
		for mobile in self.target.inRoomExcept(self.target):
			mobile.sendToClient('{target} rubs the dirt out of their eyes.'.format(target=self.target))


class Nervous(Affect):
	def __init__(self, caster, target, duration):
		super(Nervous, self).__init__('nervousness', caster, target, duration, REFRESHABLE, NOT_FRIENDLY)

	def apply(self):
		self.target.affects.append(self)

	def wear(self):
		self.target.affects.remove(self)
		self.target.sendToClient('You feel less nervous.')


class Stun(Affect):
	def __init__(self, caster, target, duration):
		super(Stun, self).__init__('stun', caster, target, duration, REFRESHABLE, NOT_FRIENDLY)


class JustDied(Affect):
	def __init__(self, caster, target, duration):
		super(JustDied, self).__init__('justdied', caster, target, duration, REFRESHABLE, NOT_FRIENDLY)

	def apply(self):
		self.target.affects.append(self)

	def wear(self):
		self.target.affects.remove(self)
		self.target.sendToClient('You are ready to fight again.')


class Sneak(Affect):
	def __init__(self, caster, target, duration):
		super(Sneak, self).__init__('sneak', caster, target, duration, REFRESHABLE, FRIENDLY)

	def wear(self):
		self.target.affects.remove(self)
		self.target.sendToClient('You no longer feel so stealthy. ')
