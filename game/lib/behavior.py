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

class Guard(Behavior):

  def doUpdate(self, amount):
    if not self.mobile.combat:
      killers = [mobile for mobile in self.mobile.inRoomExcept(self.mobile) if mobile.getStat('killer')]
      if len(killers) > 0:
        import random
        killer = killers[random.randint(0, len(killers) - 1)]
        self.mobile.processCommand("yell " + killer.name + " is a killer!  Protect the innocent!!!")
        self.mobile.startCombatWith(killer)

class Aggressive(Behavior):

  def doUpdate(self, amount):
    if not self.mobile.combat:
      targets = [mobile for mobile in self.mobile.inRoomExcept(self.mobile) if mobile.is_player]
      if len(targets) > 0:
        print "what the hell is going on here?"
        import random
        target = targets[random.randint(0, len(targets) - 1)]
        self.mobile.processCommand("say You are in the wrong place, " + target.name + ".")
        self.mobile.startCombatWith(target)
