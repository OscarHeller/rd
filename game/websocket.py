import tornado.websocket
import json
import random
import string
import datetime


class WSHandler(tornado.websocket.WebSocketHandler):
	def check_origin(self, origin):
		return True
		
	def initialize(self, game):
		self.game = game
		self.player = None

	def open(self):
		print 'New websocket player.'

		# Create a random name and register a player
		# playerData = { 'name' : ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) }
		# self.player = self.game.registerPlayer(self, playerData)

		print 'Connection opened.'
		self.write_message( {
			'message': 'Connection successful.',
			'time': datetime.datetime.utcnow().isoformat()
		})

	def sendToClient(self, data):
		data['time'] = datetime.datetime.utcnow().isoformat()
		
		try:
			if 'message' in data:
				data['message'] = self.colorize(data['message'])

			from bson.json_util import dumps
			encodedData = dumps(data)
			self.write_message(encodedData)
		except Exception as inst:
			print 'Error in sendToClient: ', inst

	def loadPlayer(self, message):
		player_id = message

		from lib import save

		dbd = save.databaseDaemon()

		loadedPlayer = dbd.loadMobileById(player_id)

		if loadedPlayer:
			self.player = self.game.registerPlayer(self, loadedPlayer)

			if not self.player:
				# We found a player, but it was rejected by the game - probably because that player is already online and not linkdead
				print 'Rejected attempt to connect to existing player.'
				self.sendToClient({'message': 'Rejected attempt to connect to existing player.'})
				return False
			return True
		else:
			print ('Player ID not found in database.')
			self.sendToClient({'message': 'Player ID not found in database.'})
			return False

	def colorize(self, data):
		import re
		import itertools

		# sanitize here, because why not?
		TAG_RE = re.compile(r'<[^>]+>')

		data = TAG_RE.sub('', data)

		# colorize!

		open_spans = 0
		closed_spans = 0
		# Switch out all the colors for spans
		data = re.sub('@[a-zA-Z]', self.getColor, data)
		# Switch out the newlines for <br>s
		data = re.sub('\n\r', '<br>', data)

		# Count the open and closed spans
		for _ in re.finditer('<span', data):
			open_spans += 1
		for _ in re.finditer('</span>', data):
			closed_spans += 1

		if closed_spans > open_spans:
			# Match the closed spans with open spans at the start
			for _ in itertools.repeat(None, closed_spans - open_spans):
				data = '<span>' + data
		elif open_spans > closed_spans:
			# Match the open spans with closed spans at the end
			for _ in itertools.repeat(None, open_spans - closed_spans):
				data = data + '</span>'

		return data

	def getColor(self, matchobj):
		code = matchobj.group(0)

		if code == '@y':
			return '<span class="lightyellow">'
		elif code == '@r':
			return '<span class="red">'
		elif code == '@m':
			return '<span class="magenta">'
		elif code == '@g':
			return '<span class="green">'
		elif code == '@x':
			return '</span>'
		return ''

	def on_message(self, message):
		if not self.player:
			success = self.loadPlayer(message)
			return
		self.player.processCommand(message)

	def on_close(self):
		if self.player:
			self.player.goLinkdead()
		print 'Connection closed.'
