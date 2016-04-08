from lib.interpreters.interpreter import CommandInterpreter
import affect
from lib.interpreters.constants import Position
import math
import datetime

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
			'charClass': 'warrior'
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
		self.inventory = self.loadInventory(config['inventory'] if 'inventory' in config else [])
		self.equipment = self.loadEquipment(config['equipment'] if 'equipment' in config else {})

		self.keywords = config['keywords'] if 'keywords' in config else [self.name]
		self.level = config['level'] if 'level' in config else 51
		self.experience = config['experience'] if 'experience' in config else 0

		#self.charClass = config['charClass'] if 'charClass' in config else 'dClass'
		self.charRace = config['charRace'] if 'charRace' in config else 'human'
		self.clan = config['clan'] if 'clan' in config else 'Loner'
		self.title = config['title'] if 'title' in config else 'the Default Character'

		self.commandInterpreters = []
		if 'charClass' in self.stats and self.stats['charClass'] == 'warrior':
			self.commandInterpreters.extend(warrior.commandList)

		#if 'charClass' in self.stats and self.stats['charClass'] == 'immortal':
		# FIX ME: not working properly, for some reason class isn't being set at the right place
		self.commandInterpreters.extend(admin.commandList)
#			print 'what the actual hell'
		# DON'T FORGET to load in a command interpreter
		self.commandInterpreter = CommandInterpreter(self.game, self)

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

		for affect in [affect for affect in self.affects if affect.visible]:
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
			score[stat] = self.stats[stat]

		return score

	def getCommandList(self):
		commands = []
		for commandObject in self.commandInterpreter.commandInterpreters:
			commands.append(commandObject.__name__)
		return commands

	def getWhoDesc(self, looker=None):
		return '[{level:2} {charRace:10} {charClass:>10}] [ {clan} ] {player} {linkdead}{name} {title}\n\r'.format(
				level=self.level,
				player=('[M]' if not self.is_player else '[P]'),
				charRace=self.charRace.capitalize(),
				charClass=self.getStat('charClass').capitalize(),
				clan=self.clan,
				name=self.getName(looker),  # FIX ME: should the name be visible when you are blinded?  probably not, right?
				title=self.title,
				linkdead='[LINKDEAD] ' if self.isLinkdead() else '')

	def getCraftRecipes(self):
		craft = {}

		for recipe in self.game.recipes:
			ingredients = []

			for ingredient in recipe.ingredients:
				ingredients.append({
					'count' : recipe.ingredients[ingredient],
					'name' : ingredient
					})

			craft[recipe.name] = ingredients

		return craft

	def sendToClient(self, message, names=None, comm=False):
		names = names if names else []
		if not self.client:
			return
		else:
			# Capitalize first letter of message
			if len(message) > 0:
				message = message[0].capitalize() + message[1:]
			data = {}

			data['commands'] = self.getCommandList()
			data['score'] = self.getScore()
			data['craft'] = self.getCraftRecipes()
			
			data['equipment'] = self.getEquipmentList()
			data['inventory'] = [item.name for item in self.inventory]
			data['who'] = [mobile.getWhoDesc() for mobile in self.game.mobiles if mobile.is_player]
			data['time'] = datetime.datetime.utcnow().isoformat()
			data['message'] = message
			data['affects'] = self.getAffectList()

			data['comm'] = comm

			inroom_mobiles = [mobile.getRoomDesc(self) for mobile in self.game.mobiles if mobile.room == self.room and mobile is not self]
			if not inroom_mobiles:
				inroom_mobiles = ['Nobody\'s here.']

			inroom_items = [item.getRoomDesc(self) for item in self.room.items]
			if not inroom_items:
				inroom_items = ['No items here.']

			data['room'] = {
				'title' : self.room.name,
				'desc' : self.room.desc,
				'mobiles' : inroom_mobiles,
				'items' : inroom_items,
				'bg' : self.room.bg
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

	def die(self):
		affect.Affect.factory('JustDied', self.combat, self, 20)
		self.combat = None
		self.position = Position.standing
		self.stats['hitpoints'] = self.stats['maxhitpoints']
		self.game.endCombat(self)

	def getStat(self, stat):
		if stat in self.stats:
			s = self.stats[stat]
			for slot, item in self.equipment.iteritems():
				if item:
					si = item.getStat(stat)
					if si and type(s) is type(si):
						s += si
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
			self.stats[stat] = value

	def update(self, amount):
		self.unLag(amount)
		self.updateAffects(amount)

		if self.linkdead > 0:
			self.linkdead -= 1
			if self.linkdead <= 0:
				self.leaveGame()


	def updateAffects(self, amount):
		for affect in self.affects:
			affect.update()

	def isAffectedBy(self, key):
		if key in [affect.name for affect in self.affects]:
			return affect
		return False

	def setLag(self, amount):
		self.commandInterpreter.lag = amount

	def unLag(self, amount):
		if self.commandInterpreter.lag > 0:
			self.commandInterpreter.lag -= amount
		if self.commandInterpreter.lag <= 0 and len(self.commandInterpreter.commandQueue) > 0:
			self.processCommand(self.commandInterpreter.commandQueue.pop(0))

	def processCommand(self, command):
		self.commandInterpreter.processCommand(command)

	def getName(self, looker=None):
		if not looker or not looker.isAffectedBy('blind') or not looker.isAffectedBy('dirtkick'):
			return self.name
		else:
			return 'someone'

	def removeItem(self, item):
		for key, equipment in self.equipment.iteritems():
			if equipment == item:
				self.inventory.append(equipment)
				self.equipment[key] = None

	def startCombatWith(self, target):
		if self.combat:
			return
		self.combat = target
		self.position = Position.fighting
		if target.combat is None:
			target.combat = self
			target.position = Position.fighting