from base import BaseHandler


class HomeHandler(BaseHandler):
	def get(self):
		user_id = self.get_current_user()
		mobiles = self.get_mobiles(user_id)

		if self.has_flash('validation'):
			flash = self.get_flash('validation')
			self.render('index.html', mobiles=list(mobiles), flash_msg=flash.message, css_class=flash.css_class)
		else:
			self.render('index.html', mobiles=list(mobiles))

