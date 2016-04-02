from tornado import gen
from bson.objectid import ObjectId

from base import BaseHandler
from flash import Flash


class PlayerCreateHandler(BaseHandler):
	def get(self):
		if self.has_flash('validation'):
			flash = self.get_flash('validation')
			self.render('player/create.html', flash_msg=flash.message, css_class=flash.css_class)
		else:
			self.render('player/create.html')

	@gen.coroutine
	def post(self):
		name = self.get_argument('name')
		charClass = self.get_argument('charClass')
		favoriteColor = self.get_argument('favoriteColor')
		user_id = self.get_current_user()

		from bson.objectid import ObjectId

		object_user_id = ObjectId(user_id)

		if not self.validate_name(name):
			flash = Flash('The name ' + name + ' is already in use.', css_class='alert-danger')
			self.set_flash(flash, 'validation')
			self.redirect('/player/create')
		else:
			config = {'user_id': object_user_id, 'name': name, 'charClass': charClass, 'stats': {'favoriteColor': favoriteColor, 'charClass': charClass }}
			self.db.mobiles.insert_one(config)
			self.redirect('/')
