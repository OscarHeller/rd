from lib.interpreters.interpreter import CommandInterpreter
import affect
from lib.interpreters.constants import Position
import math
import datetime
from item import Item
import lib.utility as utility

# classes!
from lib.interpreters import warrior
from lib.interpreters import admin

class Mobile:
	def __init__(self, name, game, config={}):
		self.name = name
		self.id = None
		self.__repr__ = self.__str__
		self.client = None
		self.game = game
		self.linkdead = 0
		self.combat = None
		self.is_player = False
		self.stats = {
			'attackSpeed': 4,
			'damage': 10,
			'hitroll': 5,
			'hitpoints': 1000,
			'maxhitpoints': 1000,
			'defense': 1,
			'charges': 2,
			'maxcharges': 3,
			'charClass': 'warrior',
			'killer': False,
			'nochan': False
		}

		if 'stats' in config:
			for k, v in config['stats'].iteritems():
				if k in self.stats:
					if type(self.stats[k]) is int:
						self.stats[k] = int(v)
					else:
						self.stats[k] = str(v)
				else:
					self.stats[k] = str(v)

		self.position = Position.standing
		self.affects = []
		self.behaviors = []
		self.inventory = self.loadInventory(config['inventory'] if 'inventory' in config else [])
		self.equipment = self.loadEquipment(config['equipment'] if 'equipment' in config else {})

		#print self.inventory, self.name
		#print config['inventory'] if 'inventory' in config else self.name

		self.keywords = config['keywords'] if 'keywords' in config else [self.name]
		self.level = config['level'] if 'level' in config else 51
		self.experience = config['experience'] if 'experience' in config else 0

		#self.charClass = config['charClass'] if 'charClass' in config else 'dClass'
		self.charRace = config['charRace'] if 'charRace' in config else 'human'
		self.clan = config['clan'] if 'clan' in config else 'Loner'
		self.title = config['title'] if 'title' in config else 'the Default Character'

		self.commandInterpreters = []
		if self.checkClass('warrior'):
			self.commandInterpreters.extend(warrior.commandList)

		if self.checkClass('immortal'):
		# FIX ME: not working properly, for some reason class isn't being set at the right place
			self.commandInterpreters.extend(admin.commandList)

		# fix me: replace this with a 'behavior' list in editor, like stats, items, etc.
		if self.checkClass('herald'):
			from behavior import Herald
			self.behaviors.append(Herald(self))
		if self.checkClass('guard'):
			from behavior import Guard
			self.behaviors.append(Guard(self))
		if self.checkClass('aggro'):
			from behavior import Aggressive
			self.behaviors.append(Aggressive(self))
		# DON'T FORGET to load in a command interpreter
		self.commandInterpreter = CommandInterpreter(self.game, self)

	class MobileException(Exception):
		pass

	def getCombatTargetByArgs(self, args):
		if len(args) > 0:
			key = args[0]
			for candidate in [mobile for mobile in self.game.mobiles if mobile.room == self.room]:
				if utility.matchList(key, candidate.keywords):
					return candidate
			raise self.MobileException('You don\'t see them here.')
		elif self.combat:
			return self.combat
		raise self.MobileException('No default target.')


	def checkClass(self, charClass):
		return ('charClass' in self.stats and self.stats['charClass'] == charClass)

	def getCommandInterpreters(self):
 		return self.commandInterpreters

	def getCondition(self, looker=None):
		hp = self.stats['hitpoints']
		maxhp = self.stats['maxhitpoints']

		percentage = math.floor(float(hp) / float(maxhp) * 100)

		if percentage == 100:
			condition = '{name} is in excellent condition.'
		elif percentage >= 80:
			condition =  '{name} has some small wounds and bruises.'
		elif percentage >= 60:
			condition =  '{name} has quite a few wounds.'
		elif percentage >= 40:
			condition =  '{name} has some big nasty wounds and scratches.'
		elif percentage >= 20:
			condition =  '{name} is pretty hurt.'
		elif percentage > 0:
			condition =  '{name} is in awful condition.'
		else:
			condition =  'BUG: {name} is mortally wounded and should be dead.'

		return condition.format(name=self.getName(looker))

	def heal(self, healAmount):
		self.stats['hitpoints'] = min(self.stats['maxhitpoints'], self.stats['hitpoints'] + healAmount)

	def getPrompt(self):
		prompt = '<@r{hp}/{maxhp}hp @b{xp}/{maxxp}xp @yLevel {level}@x> '.format(
			hp=self.stats['hitpoints'], maxhp=self.stats['maxhitpoints'], xp=self.experience, maxxp=self.level * 1000, level=self.level)
		return prompt

	def __str__(self):
		if self.linkdead > 0:
			status = 'LINKDEAD {timer}'.format(timer=self.linkdead)
		elif self.client:
			status = 'CLIENT'
		else:
			status = 'NOCLIENT'
		return '<{status}> {name}'.format(status=status, name=self.name)

	def getEquipmentList(self):
		eqList = {}

		for slot, item in self.equipment.iteritems():
			if item:
				eqList[slot] = item.getName(self)
			else:
				eqList[slot] = 'none'

		return eqList

	def getAffectList(self):
		affectList = {}

		for affect in self.affects:
			affectList[affect.name] = {
				'duration' : affect.duration,
				'friendly' : affect.friendly,
				'name' : affect.name
			}

		return affectList

	def getRoomDesc(self, looker=None):
		desc = self.getName(looker).capitalize()

		if self.combat:
			desc += ' is here, fighting ' + (self.combat.getName(looker) + '.' if self.combat is not looker else 'YOU!')
		elif self.position is Position.standing:
			desc += ' is here.'
		elif self.position is Position.resting:
			desc += ' is resting here.'
		elif self.position is Position.sleeping:
			desc += ' is sleeping here.'

		return desc

	def getScore(self):
		score = {
			'name' : self.getName(),
			'charRace' : self.charRace,
			'charClass' : self.getStat('charClass')
		}

		for stat in self.stats:
			# show as [base] current
			score[stat] = "[{base}] {current}".format(base=self.stats[stat], current=self.getStat(stat))

		return score

	def getCommandList(self):
		commands = []
		for commandObject in self.commandInterpreter.commandInterpreters:
			commands.append(commandObject.__name__)
		return commands

	def getWhoDesc(self, looker=None):
		return '[{level:2} {charRace:10} {charClass:>10}] [ {clan} ] {player} {linkdead}{name} {title}\n\r'.format(
				level=self.level,
				player=('[M]' if not self.is_player else '[P]') + ('[K]' if self.is_player and self.getStat('killer') else '') + ('[NOCHAN]' if self.is_player and self.getStat('nochan') else ''),
				charRace=self.charRace.capitalize(),
				charClass=self.getStat('charClass').capitalize(),
				clan=self.clan,
				name=self.getName(looker),  # FIX ME: should the name be visible when you are blinded?  probably not, right?
				title=self.getTitle(), # FIX ME: should any of this be visible when you are blinded?
				linkdead='[LINKDEAD] ' if self.isLinkdead() else '')

	def getCraftRecipes(self):
		craft = {}

		for recipe in self.game.recipes:
			ingredients = []

			for ingredient in recipe.ingredients:
				ingredients.append({'count': 1, 'name': ingredient['name']})

			craft[recipe.name] = ingredients

		return craft


	def sendAffectsToClient(self):
		if not self.is_player:
			return

		data = {}
		data['affects'] = self.getAffectList()
		data['score'] = self.getScore()

		self.client.sendToClient(data)

	def sendToClient(self, message, names=None, comm=False):
		names = names if names else []
		if not self.is_player:
			return
		else:
			# Capitalize first letter of message
			if len(message) > 0:
				message = message[0].capitalize() + message[1:]

			# If you're in combat, append condition of your enemy
			if self.combat:
				message += '\n\r' + self.combat.getCondition(self)

			data = {}

			data['commands'] = self.getCommandList()
			data['score'] = self.getScore()
			data['craft'] = self.getCraftRecipes()
			
			data['equipment'] = self.getEquipmentList()
			data['inventory'] = [item.name for item in self.inventory]
			data['who'] = [mobile.getWhoDesc() for mobile in self.game.mobiles if mobile.is_player]
			data['message'] = message

			data['comm'] = comm

			inroom_mobiles = [mobile.getRoomDesc(self) for mobile in self.game.mobiles if mobile.room == self.room and mobile is not self]
			if not inroom_mobiles:
				inroom_mobiles = ['Nobody\'s here.']

			inroom_items = [item.getRoomDesc(self) for item in self.room.items if not item.getStat('invisible')]
			if not inroom_items:
				inroom_items = ['No items here.']

			data['room'] = {
				'title' : self.room.getName(self),
				'desc' : self.room.getDesc(self),
				'mobiles' : inroom_mobiles,
				'items' : inroom_items,
				'bg' : self.room.getBG(self),
				'exits': [exit.key for exit in self.room.exits]
			}

			data['player'] = {
				'hp' : self.stats['hitpoints'],
				'maxhp' : self.stats['maxhitpoints'],
				'name' : self.getName(),
				'charges' : self.stats['charges']
			}

			self.client.sendToClient(data)

	def goLinkdead(self, timer=10):
		print('{name} has gone linkdead.'.format(name=self.name))

		for mobile in [mobile for mobile in self.game.mobiles if mobile is not self]:
			mobile.sendToClient('@r{name} has gone linkdead.@x'.format(name=self.getName(mobile)))

		self.linkdead = timer

	def isLinkdead(self):
		return True if self.linkdead > 0 else False

	def becomeNervous(self, enemy, timer=20):
		affect.Affect.factory('Nervous', enemy, self, timer)

	def leaveGame(self):
		print('{name} has turned themself into line noise.'.format(name=self.name))

		for mobile in [mobile for mobile in self.game.mobiles if mobile is not self]:
			mobile.sendToClient('@r{name} has disconnected.@x'.format(name=self.getName(mobile)))

		self.game.mobiles.remove(self)

	def removeFromCombat(self):
		# Find all mobiles targeting self
		for mobile in [mobile for mobile in self.game.mobiles if mobile.combat == self]:
			# Find another mobile attacking that mobile
			candidates = [candidate for candidate in self.game.mobiles if candidate.combat == mobile and candidate != self]

			if not candidates:
				# No other mobiles are fighting the mobile we're ending combat for
				mobile.combat = None
				mobile.position = Position.standing
			else:
				# Pick the first mobile
				mobile.combat = candidates[0]

		self.combat = None
		self.position = Position.standing

	def damage(self, amount):
		self.setStat('hitpoints', max(0, self.getStat('hitpoints') - amount))

	def die(self):
		self.removeFromCombat()

		affect.Affect.factory('JustDied', self.combat, self, 20)

		self.stats['hitpoints'] = self.stats['maxhitpoints']

	def getStat(self, stat):
		if stat in self.stats:
			s = self.stats[stat]
			for slot, item in self.equipment.iteritems():
				if item:
					si = item.getStat(stat)
					if si and type(s) is type(si):
						s += si
			for affect in self.affects:
				st = affect.getStat(stat)
				if st and type(st) is type(s):
					s += st
			return s
		else:
			return 0

	def saveInventory(self):
		return [str(item.id) for item in self.inventory]

	def loadInventory(self, items):
		return [Item(self.game.items[item]) for item in items]

	def saveEquipment(self):
		return {key: str(value.id) for key, value in self.equipment.iteritems()}

	def loadEquipment(self, equipment):
		return {key: Item(self.game.items[value]) for key, value in equipment.iteritems()}

	def setStat(self, stat, value):
		if stat in self.stats:
			if type(self.stats[stat]) is int:
				self.stats[stat] = int(value)
			else:
				self.stats[stat] = str(value)

	def update(self, amount):
		self.unLag(amount)
		self.updateAffects(amount)
		for behavior in self.behaviors:
			behavior.doUpdate(amount)

		if self.linkdead > 0:
			self.linkdead -= 1
			if self.linkdead <= 0:
				self.leaveGame()

	def updateAffects(self, amount):
		for affect in self.affects:
			affect.update(amount)

	def isAffectedBy(self, key):
		if key in [affect.name for affect in self.affects]:
			return affect
		return False

	def setLag(self, amount):
		self.commandInterpreter.lag = amount * 0.5

	def unLag(self, amount):
		if self.commandInterpreter.lag > 0:
			self.commandInterpreter.lag -= amount
		if self.commandInterpreter.lag <= 0 and len(self.commandInterpreter.commandQueue) > 0:
			self.commandInterpreter.processCommand(self.commandInterpreter.commandQueue.pop(0))

	def processCommand(self, command):
		print 'Appending {command} to queue.'.format(command=command)
		self.commandInterpreter.commandQueue.append(command)

	def getName(self, looker=None):
		if looker and (looker.isAffectedBy('blind') or looker.isAffectedBy('dirtkick')):
			return 'someone'
		else:
			return self.name

	def getTitle(self):
		return self.title

	def removeItem(self, item):
		for key, equipment in self.equipment.iteritems():
			if equipment == item:
				self.inventory.append(equipment)
				self.equipment[key] = None

	def startCombatWith(self, target):
		if self.combat:
			return
		if not target.getStat('killer') and self.is_player and target.is_player:
			self.sendToClient("@rYou are now a killer.@x")
			self.setStat('killer', True)
		self.combat = target
		self.position = Position.fighting
		if target.combat is None:
			target.combat = self
			target.position = Position.fighting

	def inRoomExcept(self, exceptions, room=None):
		room = room if room else self.room
		if isinstance(exceptions, list):
			return [mobile for mobile in self.game.mobiles if mobile.room == room and mobile not in exceptions]
		else:
			return [mobile for mobile in self.game.mobiles if mobile.room == room and mobile != exceptions]