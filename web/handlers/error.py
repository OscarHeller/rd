from base import BaseHandler


class ErrorHandler(BaseHandler):
	def get(self):
		self.render('errors/404.html')