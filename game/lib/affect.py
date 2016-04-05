REFRESHABLE = True
NOT_REFRESHABLE = False

FRIENDLY = True
NOT_FRIENDLY = False

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

	def __str__(self):
		return '{name}: {duration}s (from {caster})'.format(name=self.name, duration=self.duration, caster=self.caster.name)

	def refresh(self):
		existingAffect = self.target.isAffectedBy(self.name)
		existingAffect.duration = self.duration
		self.target.sendToClient('{caster} refreshes your {name}.'.format(caster=self.caster.getName(self.target), name=self.name))

	def apply(self):
		self.target.affects.append(self)
		self.target.sendToClient('You are affected by {name}.'.format(name=self.name))
		self.target.game.sendCondition(
			(lambda a: a.room == self.target.room and a is not self.target),
			'{{0}} is affected by {name}.'.format(name=self.name), [self.target])

	def wear(self):
		self.target.affects.remove(self)
		self.target.sendToClient('!{name}!'.format(name=self.name))
		self.target.game.sendCondition(
			(lambda a: a.room == self.target.room and a is not self.target),
			'{{0}} is no longer affected by {name}.'.format(name=self.name), [self.target])

	def update(self):
		self.duration -= 1
		if self.duration <= 0:
			self.wear()

	@staticmethod
	def factory(type, caster, target, duration):
		if type == 'Berserk':
			return Berserk(caster, target, duration)
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

	def apply(self):
		self.target.affects.append(self)
		self.target.sendToClient('Your pulse races as you are consumed by rage!')
		self.target.game.sendCondition(
			(lambda a: a.room == self.target.room and a is not self.target), '{0} gets a wild look in their eyes!', [self.target])

	def wear(self):
		self.target.affects.remove(self)
		self.target.sendToClient('You feel your pulse slow down.')


class Blind(Affect):
	def __init__(self, caster, target, duration):
		super(Blind, self).__init__('blind', caster, target, duration, NOT_REFRESHABLE, NOT_FRIENDLY)

	def apply(self):
		self.target.affects.append(self)
		self.target.sendToClient('You are blinded!')
		self.target.game.sendCondition(
			(lambda a: a.room == self.target.room and a is not self.target), '{0} appears to be blinded!', [self.target])

	def wear(self):
		self.target.affects.remove(self)
		self.target.sendToClient('You are no longer blinded.')
		self.target.game.sendCondition(
			(lambda a: a.room == self.target.room and a is not self.target), '{0} is no longer blinded.', [self.target])


class DirtKick(Affect):
	def __init__(self, caster, target, duration):
		super(DirtKick, self).__init__('dirtkick', caster, target, duration, NOT_REFRESHABLE, NOT_FRIENDLY)

	def apply(self):
		self.target.affects.append(self)
		self.target.sendToClient('You are blinded by the dirt in your eyes!')
		self.target.game.sendCondition(
			(lambda a: a.room == self.target.room and a is not self.target), '{0} is blinded by the dirt in their eyes!', [self.target])

	def wear(self):
		self.target.affects.remove(self)
		self.target.sendToClient('You rub the dirt out of your eyes.')
		self.target.game.sendCondition(
			(lambda a: a.room == self.target.room and a is not self.target), '{0} rubs the dirt out of their eyes.', [self.target])


class Nervous(Affect):
	def __init__(self, caster, target, duration):
		super(Nervous, self).__init__('nervousness', caster, target, duration, REFRESHABLE, NOT_FRIENDLY)


class Stun(Affect):
	def __init__(self, caster, target, duration):
		super(Stun, self).__init__('stun', caster, target, duration, REFRESHABLE, NOT_FRIENDLY)


class JustDied(Affect):
	def __init__(self, caster, target, duration):
		super(JustDied, self).__init__('just died', caster, target, duration, REFRESHABLE, NOT_FRIENDLY)


class Sneak(Affect):
	def __init__(self, caster, target, duration):
		super(Sneak, self).__init__('sneak', caster, target, duration, REFRESHABLE, FRIENDLY)

	def wear(self):
		self.target.affects.remove(self)
		self.target.sendToClient('You no longer fear so stealthy. ')
