import math

damageDecorators = [
	['miss', 'misses', 'clumsy', ''],
	['bruise', 'bruises', 'clumsy', ''],
	['scrape', 'scrapes', 'wobbly', ''],
	['scratch', 'scratches', 'wobbly', ''],
	['lightly wound', 'lightly wounds', 'amateur', ''],
	['injure', 'injures', 'amateur', ''],
	['harm', 'harms', 'competent', ', creating a bruise'],
	['thrash', 'thrashes', 'competent', ', leaving marks'],
	['decimate', 'decimates', 'cunning', ', the wound bleeds'],
	['devastate', 'devastates', 'cunning', ', hitting organs'],
	['mutilate', 'mutilates', 'calculated', ', shredding flesh'],
	['cripple', 'cripples', 'calculated', ', leaving GAPING holes'],
	['DISEMBOWEL', 'DISEMBOWELS', 'calm', ', guts spill out'],
	['DISMEMBER', 'DISMEMBERS', 'calm', ', blood sprays forth'],
	['ANNIHILATE!', 'ANNIHILATES!', 'furious', ', revealing bones'],
	['OBLITERATE!', 'OBLITERATES!', 'furious', 'furious', ', rending organs'],
	['DESTROY!!', 'DESTROYS!!', 'frenzied', 'frenzied', ', shattering bones'],
	['MASSACRE!!', 'MASSACRES!!', 'barbaric', 'barbaric', ', gore splatters everywhere'],
	['!DECAPITATE!', '!DECAPITATES!', 'deadly', 'deadly', ', scrambling some brains'],
	['@r!!SHATTER!!@x', '@r!!SHATTERS!!@x', 'legendary', 'legendary', ' into tiny pieces'],
	['do @rUNSPEAKABLE@x things to', 'does @rUNSPEAKABLE@x things to', 'ultimate', '!'],
]

minDamage = 0.0
maxDamage = 200.0


def doCombat(sender):
	fighting = sender.combat

	if not fighting:
		return None, None
	else:
		sender.becomeNervous(fighting)
		buf = {'sender': '', 'room': '', 'target': ''}
		b2 = {}
		for i in range(0, sender.getStat('attackSpeed')):
			b2 = doHit(sender)
			if 'sender' in b2:
				buf['sender'] += b2['sender']
			if 'room' in b2:
				buf['room'] += b2['room']
			if 'target' in b2:
				buf['target'] += b2['target']

		return (buf, fighting)


def doHit(sender):
	if not sender.combat:
		return {}

	if 'weapon' in sender.equipment and sender.equipment['weapon'] and sender.equipment['weapon'].noun:
		noun = sender.equipment['weapon'].getNoun()
	else:
		noun = 'punch'

	if 'weapon' in sender.equipment and sender.equipment['weapon'] and sender.equipment['weapon'].roll:
		roll = sender.equipment['weapon'].getRoll()
	else:
		roll = 0

	damage = sender.getStat('damage')
	hitroll = sender.getStat('hitroll')

	enemyDefense = sender.getStat('defense')

	import random
	if (random.randint(0, 100) < 10 * hitroll - 10 * enemyDefense):
		return doDamage(sender, damage + random.randint(roll / 2, roll), noun)
	else:
		return doDamage(sender, 0, noun)


def doDamage(sender, amount, noun='hit', target=None):
	buf = {'sender': 'BUG: doDamage called without a specific target for player not in combat.', 'room': '', 'target': ''}

	if not target:
		# If no target is supplied, try to use sender.combat
		if sender.combat:
			target = sender.combat
		else:
			return buf

	decorators = decorateDamage(amount)
	if amount > 0:
		buf['sender'] = 'Your {adj} {noun} {vplural} {{target}}{tag}. ({damage})\n\r'.format(
			noun=noun, adj=decorators[2], vplural=decorators[1], tag=decorators[3], damage=amount)

		buf['target'] = '{{name}}\'s {adj} {noun} {vplural} you{tag}. ({damage})\n\r'.format(
			noun=noun, adj=decorators[2], vplural=decorators[1], tag=decorators[3], damage=amount)

		buf['room'] = '{{0}}\'s {adj} {noun} {vplural} {{1}}{tag}. ({damage})\n\r'.format(
			noun=noun, adj=decorators[2], vplural=decorators[1], tag=decorators[3], damage=amount)

		#target.stats['hitpoints'] -= sender.getStat('damage')
		target.stats['hitpoints'] -= amount
		if target.getStat('hitpoints') <= 0:
			exp = target.level * 500
			target.die()
			buf['sender'] += '@rYou have killed {target}!@x\n\r'
			buf['target'] += '@r{name} has killed you.@x\n\r'
			buf['room'] += '@r{0} killed {1}.@x\n\r'
			buf['sender'] += '@gYou gain {experience} experience points!@x\n\r'.format(experience=exp)
			sender.experience += exp
			if (sender.experience >= 1000 * sender.level):
				sender.experience = sender.experience - 1000 * sender.level
				sender.level += 1
				buf['sender'] += '@yYou are now level {level}!@x\n\r'.format(level=sender.level)
	else:
		buf['sender'] = 'Your {adj} {noun} {vplural} {{target}}{tag}! ({damage})\n\r'.format(
			noun=noun, adj=decorators[2], vplural=decorators[1], tag=decorators[3], damage=amount)

		buf['target'] = '{{name}}\'s {adj} {noun} {vplural} you{tag}. ({damage})\n\r'.format(
			noun=noun, adj=decorators[2], vplural=decorators[1], tag=decorators[3], damage=amount)

		buf['room'] = '{{0}}\'s {adj} {noun} {vplural} {{1}}{tag} ({damage}).\n\r'.format(
			noun=noun, adj=decorators[2], vplural=decorators[1], tag=decorators[3], damage=amount)

	return buf


def decorateDamage(amount):
	length = len(damageDecorators) - 1
	return damageDecorators[min(length, int(math.ceil(length * amount / maxDamage)))]
