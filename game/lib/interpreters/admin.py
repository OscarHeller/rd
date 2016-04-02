import lib.utility as utility
from lib.interpreters.command import Command

class Goto(Command):
  def __init__(self, game):
    super(Goto, self).__init__(game, 'goto')

  def execute(self, args, config):
    sender = config['sender']
    #quick double check here, but only immortals should even have this command
    if sender.charClass is not 'warrior':
      sender.sendToClient('yeah right')
    elif len(args) <= 0:
      # show available rooms & their 'vnum'?
        buf = ""
        for i in range(0, len(self.game.rooms)):
          buf += str(i) + ": " + self.game.rooms[i].name + "\n\r"
        sender.sendToClient(buf)
    else:
      vnum = int(args[0])
      if self.game.rooms[vnum]:
        r = sender.room
        sender.room = self.game.rooms[vnum]
        sender.sendToClient("You vanish in a burst of flame.\n\rYou arrive in a burst of flame.")
        [mobile.sendToClient(sender.name + " vanishes in a burst of flame.") for mobile in self.game.mobiles if mobile.room == r and mobile != sender]
        [mobile.sendToClient(sender.name + " arrives in a burst of flame.") for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]

class CreateItem(Command):
  def __init__(self, game):
    super(CreateItem, self).__init__(game, 'createitem')

  def execute(self, args, config):
    sender = config['sender']
    #quick double check here, but only immortals should even have this command
    if sender.charClass is not 'warrior':
      sender.sendToClient('yeah right')
    elif len(args) <= 0:
      # show available rooms & their 'vnum'?
      i_keys = self.game.items.keys()
      buf = ""
      for i in range(0, len(i_keys)):
        item = self.game.items[i_keys[i]]
        buf += str(i) + ": " + item.name + "\n\r"
      sender.sendToClient(buf)
    else:
      import copy

      i_keys = self.game.items.keys()
      vnum = int(args[0])
      key = i_keys[vnum]
      if self.game.items[key]:
        r = sender.room
        item = copy.deepcopy(self.game.items[key])
        sender.room.items.append(item)
        sender.sendToClient("You create a " + item.name)
        [mobile.sendToClient(sender.name + " creates a " + item.name) for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]

class SpawnMobile(Command):
  def __init__(self, game):
    super(SpawnMobile, self).__init__(game, 'spawnmobile')

  def execute(self, args, config):
    sender = config['sender']
    #quick double check here, but only immortals should even have this command
    if sender.charClass is not 'warrior':
      sender.sendToClient('yeah right')
    elif len(args) <= 0:
      # show available rooms & their 'vnum'?
      i_keys = self.game.mobile_list.keys()
      buf = ""
      for i in range(0, len(i_keys)):
        mobile = self.game.mobile_list[i_keys[i]]
        buf += str(i) + ": " + mobile["name"] + "\n\r"
      sender.sendToClient(buf)
    else:
      from lib.mobile import Mobile

      i_keys = self.game.mobile_list.keys()
      vnum = int(args[0])
      key = i_keys[vnum]
      if self.game.mobile_list[key]:
        i = self.game.mobile_list[key]
        m = Mobile(i['name'], self.game, i)
        m.room = sender.room
        self.game.mobiles.append(m)
        sender.sendToClient("You spawn a " + m.name)
        [mobile.sendToClient(sender.name + " spawn a " + m.name) for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]

class PlayerList(Command):
  def __init__(self, game):
    super(PlayerList, self).__init__(game, 'playerlist')

  def execute(self, args, config):
    sender = config['sender']
    #quick double check here, but only immortals should even have this command
    if sender.charClass is not 'warrior':
      sender.sendToClient('yeah right')
    elif len(args) <= 0:
      buf = "Players: \n\r"
      players = [mobile for mobile in self.game.mobiles if mobile.client]
      for i in range(0, len(players)):
        buf += str(i) + ": " + players[i].name + "\n\r"
      sender.sendToClient(buf)
    elif len(args) == 1:
      players = [mobile for mobile in self.game.mobiles if mobile.client]
      vnum = int(args[0])
      if players[vnum]:
        sender.sendToClient(players[vnum].name)
    else:
      players = [mobile for mobile in self.game.mobiles if mobile.client]
      vnum = int(args.pop(0))
      player = players[vnum]
      if player:
        player.processCommand(" ".join(args))

commandList = [Goto, CreateItem, SpawnMobile, PlayerList]