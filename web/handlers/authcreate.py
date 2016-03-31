from base import BaseHandler
from tornado import gen
from flash import Flash


class AuthCreateHandler(BaseHandler):
	def get(self):
		if self.has_flash('validation'):
			flash = self.get_flash('validation')
			self.render('auth/create.html', flash_msg=flash.message, css_class=flash.css_class)
		else:
			self.render('auth/create.html')

	@gen.coroutine
	def post(self):
		email = self.get_argument('email')
		password = self.get_argument('password')
		retype = self.get_argument('retype')

		if self.email_in_use(email):
			print ('Email in use.')
			flash = Flash('That email is taken.', css_class='alert-danger')
			self.set_flash(flash, 'validation')
			self.redirect('/auth/create')
		elif password != retype:
			print ('Passwords don\'t match.')
			flash = Flash('Passwords don\'t match.', css_class='alert-danger')
			self.set_flash(flash, 'validation')
			self.redirect('/auth/create')
		else:
			self.db.accounts.insert_one({'email': email, 'password': password})
			print ('Successfully registered.')
			flash = Flash('You have successfully registered.', css_class='alert-success')
			self.set_flash(flash, 'validation')
			self.redirect('/auth/login')
