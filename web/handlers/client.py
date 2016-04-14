from base import BaseHandler
from bson.objectid import ObjectId
import os


class ClientHandler(BaseHandler):
	def get(self, slug):
		self.validateInternalPageAccess()

		# Get player ID.
		player_id = slug

		object_player_id = ObjectId(player_id)

		# Make sure player's user_id matches the cookie.

		user_id = self.get_current_user()
		object_user_id = ObjectId(user_id)

		player = self.db.mobiles.find_one({'_id': object_player_id})

		if player and 'user_id' in player:
			player_user_id = player['user_id']
		else:
			player_user_id = None

		if not player_user_id:
			# Bad player user ID.
			print('Player with id {uid} not found. Exiting.'.format(uid=object_player_id))
			return

		if player_user_id != object_user_id:
			# Player user ID doesn't match cookie.
			print('Player ID [{puid}] doesn\'t match cookie ID [{uid}]. Possible hack.'.format(puid=player_user_id, uid=object_user_id))
			return

		# This is a good player ID. Send it to the game to load.
		print('Good player ID found. Sending to game for loading.')

		bgList, iconList = self._preparePreload()

		self.render('client.html', player_id=player_id, bgList=bgList, iconList=iconList)

	def _preparePreload(self):
		print 'Starting preload.'
		# Static file list for preloading
		bgPath = os.path.join(os.path.dirname(__file__), '../static/media')
		bgList = []

		for (dirpath, dirnames, filenames) in os.walk(bgPath):
			bgList.extend(filenames)
			break

		iconPath = os.path.join(os.path.dirname(__file__), '../static/media/icons')
		iconList = []

		for (dirpath, dirnames, filenames) in os.walk(iconPath):
			iconList.extend(filenames)
			break

		bgList = ','.join(bgList)
		iconList = ','.join(iconList)

		return bgList, iconList