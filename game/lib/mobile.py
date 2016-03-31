from lib.interpreters.interpreter import CommandInterpreter
import affect
from lib.interpreters.constants import Position
import math
import datetime

# classes!
from lib.interpreters import warrior

class Mobile:
	def __init__(self, name, game, config={}):
		self.name = name
		self.id = None
		self.__repr__ = self.__str__
		self.client = None
		self.game = game
		self.linkdead = 0
		self.combat = None
		self.combatBuffer = ''
		self.stats = {
			'attackSpeed': 4,
			'damage': 10,
			'hitroll': 5,
			'hitpoints': 900,
			'maxhitpoints': 1000,
			'defense': 1,
			'charges': 3,
			'maxcharges': 3
		}
		self.position = Position.standing
		self.affects = []
		self.inventory = []
		self.equipment = {'weapon': None}

		self.keywords = config['keywords'] if 'keywords' in config else [self.name]
		self.level = config['level'] if 'level' in config else 1
		self.experience = config['experience'] if 'experience' in config else 0

		self.charClass = config['charClass'] if 'charClass' in config else 'dClass'
		self.charRace = config['charRace'] if 'charRace' in config else 'human'
		self.clan = config['clan'] if 'clan' in config else 'dClan'
		self.title = config['title'] if 'title' in config else 'the Default'

		self.commandInterpreters = []
		if self.charClass == 'warrior':
			self.commandInterpreters.extend(warrior.commandList)
		# DON'T FORGET to load in a command interpreter
		self.commandInterpreter = CommandInterpreter(self.game, self, self.charClass)

	def getCommandInterpreters(self):
 		return self.commandInterpreters + self.room.getCommandInterpreters()

	def appendEnemyConditionToBuffer(self):
		if self.combat:
			self.combatBuffer += self.combat.getCondition().format(name=self.combat.getName())

	def getCondition(self):
		hp = self.stats['hitpoints']
		maxhp = self.stats['maxhitpoints']

		percentage = math.floor(float(hp) / float(maxhp) * 100)

		if percentage == 100:
			return '{name} is in excellent condition.'
		elif percentage >= 80:
			return '{name} has some small wounds and bruises.'
		elif percentage >= 60:
			return '{name} has quite a few wounds.'
		elif percentage >= 40:
			return '{name} has some big nasty wounds and scratches.'
		elif percentage >= 20:
			return '{name} is pretty hurt.'
		elif percentage > 0:
			return '{name} is in awful condition.'
		else:
			return 'BUG: {name} is mortally wounded and should be dead..'

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
			affectList[affect.name] = affect.duration

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


	def sendToClient(self, message, names=None, comm=False):
		names = names if names else []
		if not self.client:
			return
		else:
			# Capitalize first letter of message
			if len(message) > 0:
				message.format(*[sender.getName(self) for sender in names])
				message = message[0].capitalize() + message[1:]
			data = {}
			if self.client.getClientType() != 'websocket':
				data['message'] = message + '\n\r' + self.getPrompt()
			else:
				data['equipment'] = self.getEquipmentList()
				data['inventory'] = [item.name for item in self.inventory]
				data['who'] = [mobile.name for mobile in self.game.mobiles]
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
					'items' : inroom_items
				}

				data['player'] = {
					'hp' : self.stats['hitpoints'],
					'maxhp' : self.stats['maxhitpoints'],
					'name' : self.getName(),
					'charges' : self.stats['charges'],
					'charRace' : self.charRace,
					'charClass' : self.charClass
				}

			self.client.sendToClient(data)

	def sendToBuffer(self, message):
		if len(message) > 0:
			message = message[0].capitalize() + message[1:]
		self.combatBuffer += message

	def clearBuffer(self):
		self.combatBuffer = ''

	def goLinkdead(self, timer=10):
		print('{name} has gone linkdead.'.format(name=self.name))
		self.linkdead = timer

	def isLinkdead(self):
		return True if self.linkdead > 0 else False

	def becomeNervous(self, enemy, timer=20):
		affect.Affect.factory('Nervous', enemy, self, timer)

	def leaveGame(self):
		print('{name} has turned themself into line noise.'.format(name=self.name))
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
			for e in self.equipment:
				if self.equipment[e]:
					s += int(self.equipment[e].getStat(stat))
			return s
		else:
			return 0

	def update(self, amount):
		self.unLag(amount)
		self.updateAffects(amount)

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
