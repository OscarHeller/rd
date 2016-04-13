from base import BaseHandler
from flash import Flash

class AuthLogoutHandler(BaseHandler):
	def get(self):
		self.clear_cookie('rdu_user')
		self.clear_cookie('rdu_role')

		flash = Flash('Alas, all good things must come to an end.', css_class='alert-success')
		self.set_flash(flash, 'validation')
		self.redirect('/')
