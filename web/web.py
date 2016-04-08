import tornado.httpserver
import tornado.ioloop
import tornado.web
from pymongo import MongoClient
import os

from handlers import home, client, authlogin, authlogout, authcreate, playercreate, editor, error, media

class Application(tornado.web.Application):
	def __init__(self):

		# Have one global MongoDB collection across all users that gets passed into BaseHandler
		# self.client = MongoClient('mongodb://rdu:omghot4u@ds027769.mongolab.com:27769/redemptionunleashed')
		self.client = MongoClient('localhost')
		self.db = self.client.redemptionunleashed

		urls = [
			(r'/', home.HomeHandler, {'db': self.db}),
			(r'/client/([^/]+)', client.ClientHandler, {'db': self.db}),
			(r'/auth/login', authlogin.AuthLoginHandler, {'db': self.db}),
			(r'/auth/logout', authlogout.AuthLogoutHandler, {'db': self.db}),
			(r'/auth/create', authcreate.AuthCreateHandler, {'db': self.db}),
			(r'/player/create', playercreate.PlayerCreateHandler, {'db': self.db}),
			(r'/editor', editor.EditorHandler, {'db': self.db}),
			(r'/media', media.MediaHandler, {'db': self.db})
		]

		settings = dict(
			template_path=os.path.join(os.path.dirname(__file__), 'templates'),
			static_path=os.path.join(os.path.dirname(__file__), 'static'),
			cookie_secret='__FIX ME:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__',
			debug=True,
			default_handler_class = error.ErrorHandler
		)
		super(Application, self).__init__(urls, **settings)


def main():
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(5000)
	tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
	main()
