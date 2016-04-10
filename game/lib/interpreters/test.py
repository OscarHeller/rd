from lib.interpreters.command import Command
from lib.interpreters.constants import Position
import lib.affect as affect


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


class Test(Command):
	def __init__(self, game):
		super(Test, self).__init__(game, 'test')

	def execute(self, args, sender):
		sender.setStat('charges', max(0, sender.getStat('charges') - 1) )
		affect.Affect.factory('Blind', sender, sender, 500)

commandList = [Test]
