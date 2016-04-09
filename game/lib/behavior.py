class Behavior:
  def __init__(self, mobile):
    self.mobile = mobile

  def doUpdate(self, amount):
    return

class Herald(Behavior):
  def __init__(self, mobile):
    self.mobile = mobile
    self.heard = []
    self.message = self.mobile.stats['heraldMessage'] if 'heraldMessage' in self.mobile.stats else 'I have nothing to say.'

  def doUpdate(self, amount):
    newInRoom = [mobile for mobile in self.mobile.game.mobiles if mobile.room is self.mobile.room and not mobile in self.heard]
    if len(newInRoom) > 0:
      self.mobile.processCommand("say " + self.message)
      for mobile in newInRoom:
        self.heard.append(mobile)