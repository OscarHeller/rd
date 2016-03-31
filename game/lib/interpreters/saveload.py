import lib.save as save
from lib.interpreters.command import Command
from lib.interpreters.constants import Position


"""
Command Attributes;
attribute (default): description

aggro				(False)				: does it start combat?
canTarget			(False)				: can it take an automatic single target?
requireTarget		(False)				: does it require a target?
useInCombat			(False)				: can you use it in combat?
useWhileJustDied	(True)				: can you use it immediately after dying?
targetSelf			(True)				: can you target yourself?
Range				(Range.room)		: for skills that canTarget, what is the range of potential targets?
minPosition			(Position.standing)	: what is the minimum position as defined in constants.py?
"""


class Save(Command):
	def __init__(self, game):
		super(Save, self).__init__(game, 'save')
		self.minPosition = Position.sleeping

	def execute(self, args, config):
		sender = config['sender']

		dbd = save.databaseDaemon()

		sender.sendToClient('Initiating save.')

		import thread
		thread.start_new_thread(dbd.saveMobile, (sender,))
		sender.sendToClient('Save complete.')


class Quit(Command):
	def __init__(self, game):
		super(Quit, self).__init__(game, 'quit')
		self.minPosition = Position.sleeping

	def execute(self, args, config):
		sender = config['sender']

		# Only quit if they type 'quit confirm'
		if 'confirm' not in args:
			sender.sendToClient('You must type quit confirm to quit.')
			return

		# Send disconnect message
		sender.sendToClient('Alas, all good things must come to an end.')

		# Kill client connection
		if sender.client.getClientType() == 'websocket':
			sender.client.close()

		if 'nervous' in sender.affects:
			# If client is nervous, make them linkdead (and only decrement linkdead if not nervous)
			sender.goLinkdead()
		else:
			# Otherwise, quit the player
			sender.leaveGame()

		# Get rid of client
		sender.client = None

commandList = [Save, Quit]
