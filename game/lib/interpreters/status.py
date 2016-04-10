import lib.utility as utility
from lib.interpreters.command import Command
from lib.interpreters.constants import Position, Range


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

class Look(Command):
  def __init__(self, game):
    super(Look, self).__init__(game, 'look')

  def execute(self, args, sender):
    # Preliminary checks
    self.test(self.checkPosition, (sender, [Position.standing, Position.resting, Position.fighting]))
    self.test(self.hasAtLeastOneArgument, args, override='Look at what?')

    thing = self.test(self.getTargetFromListByName, (args[0], sender.room.items + [mobile for mobile in sender.game.mobiles if mobile.room is sender.room]))

    d = thing.getStat('description')
    if not d:
      d = 'You see nothing special.'

    self.appendToCommandBuffer(sender, d)
    for mobile in sender.inRoomExcept(sender):
      self.appendToCommandBuffer(mobile, sender.name + ' looks at ' + thing.getName(mobile))
    # FIX ME: show message to everyone in room...


commandList = [Look]
