from base import BaseHandler
from tornado import gen
from flash import Flash


class AuthLoginHandler(BaseHandler):
	def get(self):
		if self.has_flash('validation'):
			flash = self.get_flash('validation')
			self.render('auth/login.html', flash_msg=flash.message, css_class=flash.css_class)
		else:
			self.render('auth/login.html')

	@gen.coroutine
	def post(self):
		email = self.get_argument('email')
		password = self.get_argument('password')

		doc = self.db.accounts.find_one({'email': email, 'password': password})
		if doc:
			stringID = str(doc['_id'])

			role = 'admin' if 'admin' in doc and doc['admin'] else 'user'
			self.set_secure_cookie('rdu_role', role)
			self.set_secure_cookie('rdu_user', stringID)
			
			flash = Flash('Welcome to Redemption: Unleashed.', css_class='alert-success')
			self.set_flash(flash, 'validation')

			self.redirect('/')
		else:
			# No such user or wrong password.
			flash = Flash('Login incorrect.', css_class='alert-danger')
			self.set_flash(flash, 'validation')
			self.redirect('/auth/login')
