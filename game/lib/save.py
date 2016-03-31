import json
from pymongo import MongoClient
from bson.objectid import ObjectId

noSave = False


class databaseDaemon():
	def __init__(self):
		self.client = MongoClient('localhost')  # FIX ME: this is set in two places, here and in tornadoServer.py. Should be only one.
		# self.client = MongoClient('mongodb://rdu:omghot4u@ds027769.mongolab.com:27769/redemptionunleashed')
		self.db = self.client.redemptionunleashed

	def saveMobile(self, mobile):
		import time
		global noSave

		if noSave:
			print ('noSave enabled.')
			return None

		db = self.db
		collection = db.mobiles

		# See if mobile by same name already exists in DB
		# time.sleep(5)

		mobileJSON = {
			'name': mobile.name,
			'stats': mobile.stats,
			'room': mobile.room.getIndex()
		}

		post_id = collection.update_one(
			{'_id': mobile.id},
			{'$set': mobileJSON},
			True
		)

	def loadMobileById(self, player_id):

		db = self.db

		object_player_id = ObjectId(player_id)

		loadedMobile = db.mobiles.find_one({'_id': object_player_id})

		return loadedMobile
