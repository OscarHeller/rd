import math
import random
from lib.interpreters.constants import Position

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


def doGlobalRound(game):
	# Initialize a dictionary of all in-combat mobiles and an empty buffer. This will get
	# passed around and filled in as the combat round progresses.

	fighters = [mobile for mobile in game.mobiles if mobile.combat]
	combatBuffer = {}

	for fighter in fighters:
		combatBuffer = doSingleRound(game, fighter, combatBuffer=combatBuffer)

	# Append conditions for everyone who's in combat.
	combatBuffer = appendConditionsToCombatBuffer(combatBuffer)

	sendCombatBuffer(game, combatBuffer)

def doSingleRound(game, fighter, combatBuffer=None):
	combatBuffer = {} if not combatBuffer else combatBuffer

	target = fighter.combat

	for i in range(0, fighter.getStat('attackSpeed')):
		combatBuffer = doHit(game, fighter, combatBuffer=combatBuffer)

	return combatBuffer


def doHit(game, fighter, combatBuffer=None):

	if 'weapon' in fighter.equipment and fighter.equipment['weapon'] and fighter.equipment['weapon'].noun:
		noun = fighter.equipment['weapon'].getNoun()
	else:
		noun = 'punch'

	if 'weapon' in fighter.equipment and fighter.equipment['weapon'] and fighter.equipment['weapon'].roll:
		roll = fighter.equipment['weapon'].getRoll()
	else:
		roll = 0

	damage = fighter.getStat('damage')
	hitroll = fighter.getStat('hitroll')
	enemyDefense = fighter.getStat('defense')

	if random.randint(0, 100) < ( ( 10 * hitroll ) - ( 10 * enemyDefense ) ):
		combatBuffer = doDamage(game, fighter, damage + random.randint(roll / 2, roll), noun, target=fighter.combat, combatBuffer=combatBuffer)
	else:
		combatBuffer = doDamage(game, fighter, 0, noun, target=fighter.combat, combatBuffer=combatBuffer)

	return combatBuffer


def doDamage(game, fighter, amount, noun='hit', target=None, combatBuffer=None):
	combatBuffer = {} if not combatBuffer else combatBuffer

	if not target:
		return combatBuffer

	decorators = decorateDamage(amount)

	message = 'Your {adj} {noun} {vplural} {target}{tag}. ({damage})'.format(
		noun=noun, adj=decorators[2], vplural=decorators[1], tag=decorators[3], damage=amount, target=target.getName(fighter))

	combatBuffer = appendToCombatBuffer(fighter, message, combatBuffer)

	message = '{fighter}\'s {adj} {noun} {vplural} you{tag}. ({damage})'.format(
		noun=noun, adj=decorators[2], vplural=decorators[1], tag=decorators[3], damage=amount, fighter=fighter.getName(target))

	combatBuffer = appendToCombatBuffer(target, message, combatBuffer)

	for mobile in [mobile for mobile in game.mobiles if mobile != fighter and mobile != target and mobile.room == target.room]:
		message = '{fighter}\'s {adj} {noun} {vplural} {target}{tag}. ({damage})'.format(
			fighter=fighter.getName(mobile), target=target.getName(mobile), noun=noun, adj=decorators[2], vplural=decorators[1],
			tag=decorators[3], damage=amount)

		combatBuffer = appendToCombatBuffer(mobile, message, combatBuffer)

	target.stats['hitpoints'] -= amount
	if target.getStat('hitpoints') <= 0:
		# looting, can probably move elsewhere when it become more sophisticated -> only loots from inventory at the moment
		fighter.inventory.extend(target.inventory)
		if len(target.inventory) > 0:
			message = "You loot " + ", ".join([str(item.name) for item in target.inventory]) + " from " + target.getName(fighter) + "'s' dead body."
		else:
			message = target.getName(fighter) + " wasn't carrying anything."
		combatBuffer = appendToCombatBuffer(fighter, message, combatBuffer)
		target.inventory = []
		endCombatForPlayersByTarget(game, target)
		target.die()

		message = 'You have killed {target}!'.format(target=target.getName(fighter))
		combatBuffer = appendToCombatBuffer(fighter, message, combatBuffer)

		message = 'You have been killed!'
		combatBuffer = appendToCombatBuffer(target, message, combatBuffer)

		for mobile in [mobile for mobile in game.mobiles if mobile != fighter and mobile != target and mobile.room == target.room]:
			message = '{fighter} killed {target}!'.format(fighter=fighter.getName(mobile), target=target.getName(mobile))
			combatBuffer = appendToCombatBuffer(mobile, message, combatBuffer)

		if target.is_player:
			for mobile in [mobile for mobile in game.mobiles]:
				message = '@r{target}@x suffers defeat at the hands of @r{fighter}@x.'.format(target=target.getName(mobile), fighter=fighter.getName(mobile))
				combatBuffer = appendToCombatBuffer(mobile, message, combatBuffer)

	return combatBuffer


def endCombatForPlayersByTarget(game, target):
	target.position = Position.standing
	target.combat = None

	for mobile in [mobile for mobile in game.mobiles if mobile.combat == target]:
		print 'ending combat for ' + mobile.getName()
		mobile.combat = None
		mobile.position = Position.standing


def decorateDamage(amount):
	length = len(damageDecorators) - 1
	return damageDecorators[min(length, int(math.ceil(length * amount / maxDamage)))]


def appendToCombatBuffer(key, string, combatBuffer):
	if key in combatBuffer:
		combatBuffer[key].append(string)
	else:
		combatBuffer[key] = [string,]

	return combatBuffer


def sendCombatBuffer(game, combatBuffer):
	for mobile, bufferList in combatBuffer.iteritems():
		bufferString = '\n\r'.join( bufferList )

		mobile.sendToClient( bufferString )


def appendConditionsToCombatBuffer(combatBuffer):
	for mobile in combatBuffer:
		if mobile.combat:
			combatBuffer[mobile].append(mobile.combat.getCondition(looker=mobile))

	return combatBuffer
