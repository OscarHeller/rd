from base import BaseHandler


class AuthLogoutHandler(BaseHandler):
	def get(self):
		self.clear_cookie('rdu_user')
		self.redirect(self.get_argument('next', '/'))
