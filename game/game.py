import tornado.httpserver
import tornado.ioloop
import tornado.web
from pymongo import MongoClient

from lib import game
import websocket

import os


class Application(tornado.web.Application):
	def __init__(self, newGame):
		self.game = newGame

		urls = [
			(r'/', websocket.WSHandler, {'game': self.game})
		]

		settings = dict(
			template_path=os.path.join(os.path.dirname(__file__), 'templates'),
			static_path=os.path.join(os.path.dirname(__file__), 'static'),
			cookie_secret='__FIX ME:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__',
			debug=True
		)
		super(Application, self).__init__(urls, **settings)


def main():
	newGame = game.Game()

	http_server = tornado.httpserver.HTTPServer(Application(newGame))
	http_server.listen(4000)
	tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
	main()
