from tornado import gen
from bson.objectid import ObjectId

from base import BaseHandler
from flash import Flash


class PlayerCreateHandler(BaseHandler):
	def get(self):
		self.validateInternalPageAccess()

		if self.has_flash('validation'):
			flash = self.get_flash('validation')
			self.render('player/create.html', flash_msg=flash.message, css_class=flash.css_class)
		else:
			self.render('player/create.html')

	@gen.coroutine
	def post(self):
		name = self.get_argument('name')
		charClass = self.get_argument('charClass')
		user_id = self.get_current_user()

		from bson.objectid import ObjectId

		object_user_id = ObjectId(user_id)

		if not self.validate_name(name):
			flash = Flash('The name ' + name + ' is already in use or does not meet our naming guidelines.', css_class='alert-danger')
			self.set_flash(flash, 'validation')
			self.redirect('/player/create')
		elif not self.validate_class(charClass):
			flash = Flash('Illegal class.', css_class='alert-danger')
			self.set_flash(flash, 'validation')
			self.redirect('/player/create')
		else:
			config = {'user_id': object_user_id, 'name': name, 'charClass': charClass, 'stats': {'charClass': charClass }}
			self.db.mobiles.insert_one(config)

			flash = Flash('New character "{name}" successfully created.'.format(name=name), css_class='alert-success')
			self.set_flash(flash, 'validation')
			self.redirect('/')

			self.redirect('/')
