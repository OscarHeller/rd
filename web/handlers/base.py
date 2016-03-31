import tornado.web
from flash import Flash
import pickle


class BaseHandler(tornado.web.RequestHandler):
	def initialize(self, db=None):
		self.db = db

	def write_error(self, status_code, **kwargs):
		print str(status_code) + ' Error'
		if status_code == 404:
			self.render('errors/404.html', page=None)
		else:
			self.render('errors/unknown.html', page=None)

	def get_rooms(self):
		return self.db.rooms.find()

	def set_rooms(self, rooms):
		for rm in rooms:
			room = rooms[rm]
			if '_id' in room:
				if 'delete' in room and room['delete'] == 1:
					self.db.rooms.delete_one({'_id': room['_id']})
				else:
					self.db.rooms.update_one({'_id': room['_id']}, {'$set': room}, True)
			else:
				self.db.rooms.insert_one(room)

	def get_items(self):
		return self.db.items.find()

	def set_items(self, items):
		for i in range(0, len(items)):
			item = items[i]
			if '_id' in item:
				if 'delete' in item and item['delete'] == 1:
					print 'blargh', item
					self.db.items.delete_one({'_id': item['_id']})
				else:
					self.db.items.update_one({'_id': item['_id']}, {'$set': item}, True)
			else:
				self.db.items.insert_one(item)

	def get_npcs(self):
#		return self.db.mobiles.find()
		return self.db.mobiles.find({'user_id': { '$exists': False }} )

	def set_npcs(self, npcs):
		for i in range(0, len(npcs)):
			npc = npcs[i]
			if '_id' in npc:
				if 'delete' in npc and npc['delete'] == 1:
					self.db.mobiles.delete_one({'_id': npc['_id']})
				else:
					self.db.mobiles.update_one({'_id': npc['_id']}, {'$set': npc}, True)
			else:
				self.db.mobiles.insert_one(npc)

	def get_current_user(self):
		return self.get_secure_cookie('rdu_user')

	def email_in_use(self, email):
		doc = self.db.accounts.find_one({'email': email})
		return bool(doc)

	def get_mobiles(self, user_id):
		from bson.objectid import ObjectId

		object_user_id = ObjectId(user_id)
		doc = self.db.mobiles.find({'user_id': object_user_id})

		return doc

	def player_exists(self, name):
		doc = self.db.mobiles.find_one({'name': name})
		return bool(doc)

	def validate_name(self, name):
		if len(name) < 3:
			print ('Names must be at least three characters.')
			return False
		if self.player_exists(name):
			print ('That name is taken.')
			return False

		return True

	"""
	Extends Tornado's RequestHandler by adding flash functionality.
	"""

	def _cookie_name(self, key):
		return key + '_flash_cookie'  # change this to store/retrieve flash cookies under a different name

	def _get_flash_cookie(self, key):
		return self.get_cookie(self._cookie_name(key))

	def has_flash(self, key):
		"""
		Returns true if a flash cookie exists with a given key (string);
		false otherwise.
		"""
		return self._get_flash_cookie(key) is not None

	def get_flash(self, key):
		"""
		Returns the flash cookie under a given key after converting the
		cookie data into a Flash object.
		"""
		if not self.has_flash(key):
			return None
		flash = tornado.escape.url_unescape(self._get_flash_cookie(key))
		try:
			flash_data = pickle.loads(flash)
			self.clear_cookie(self._cookie_name(key))
			return flash_data
		except:
			return None

	def set_flash(self, flash, key='error'):
		"""
		Stores a Flash object as a flash cookie under a given key.
		"""
		flash = pickle.dumps(flash)
		self.set_cookie(self._cookie_name(key), tornado.escape.url_escape(flash))
