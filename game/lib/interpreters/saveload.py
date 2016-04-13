import lib.save as save
from lib.interpreters.command import Command
from lib.interpreters.constants import Position
import thread


class Save(Command):
	def __init__(self, game):
		super(Save, self).__init__(game, 'save')

	def execute(self, args, sender):
		dbd = save.databaseDaemon()

		thread.start_new_thread(dbd.saveMobile, (sender,))

		msg = 'Save complete.'
		self.appendToCommandBuffer(sender, msg)


class Quit(Command):
	def __init__(self, game):
		super(Quit, self).__init__(game, 'quit')

	def execute(self, args, sender):
		# Only quit if they type 'quit confirm'
		if 'confirm' not in args:
			msg = 'You must type quit confirm to quit.'
			self.appendToCommandBuffer(sender, msg)
			return

		# Send disconnect message
		msg = 'Alas, all good things must come to an end.'
		self.appendToCommandBuffer(sender, msg)

		# Kill client connection
		sender.client.close()

		if 'nervous' in sender.affects:
			# If client is nervous, make them linkdead (and only decrement linkdead if not nervous)
			print '{player} used quit command while nervous. Going linkdead.'.format(player=sender.getName())
			sender.goLinkdead()
		else:
			# Otherwise, quit the player
			print '{player} used quit command. Quitting player.'.format(player=sender.getName())
			sender.leaveGame()

		# Get rid of client
		sender.client = None

commandList = [Save]
