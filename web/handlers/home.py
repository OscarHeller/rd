from base import BaseHandler


class HomeHandler(BaseHandler):
	def get(self):
		user_id = self.get_current_user()
		mobiles = self.get_mobiles(user_id)

		self.render('index.html', mobiles=list(mobiles))
