from base import BaseHandler
from bson.objectid import ObjectId


class ClientHandler(BaseHandler):
	def get(self, slug):
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
		self.render('client.html', player_id=player_id)
