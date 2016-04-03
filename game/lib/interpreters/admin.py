import lib.utility as utility
from lib.interpreters.command import Command

class Goto(Command):
  def __init__(self, game):
    super(Goto, self).__init__(game, 'goto')

  def execute(self, args, config):
    sender = config['sender']
    #quick double check here, but only immortals should even have this command
    if len(args) <= 0:
      # show available rooms & their 'vnum'?
        buf = ""
        for i in range(0, len(self.game.rooms)):
          buf += str(i) + ": " + self.game.rooms[i].name + "\n\r"
        sender.sendToClient(buf)
    elif args[0].isdigit():
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
    if len(args) <= 0:
      # show available rooms & their 'vnum'?
      i_keys = self.game.items.keys()
      buf = ""
      for i in range(0, len(i_keys)):
        item = self.game.items[i_keys[i]]
        buf += str(i) + ": " + item['name'] + "\n\r"
      sender.sendToClient(buf)
    elif args[0].isdigit():
      import copy

      i_keys = self.game.items.keys()
      vnum = int(args[0])
      key = i_keys[vnum]
      if self.game.items[key]:
        r = sender.room
        item = copy.deepcopy(self.game.items[key])
        sender.room.items.append(item)
        sender.sendToClient("You create a " + item['name'])
        [mobile.sendToClient(sender.name + " creates a " + item['name']) for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]

class SpawnMobile(Command):
  def __init__(self, game):
    super(SpawnMobile, self).__init__(game, 'spawnmobile')

  def execute(self, args, config):
    sender = config['sender']
    #quick double check here, but only immortals should even have this command
    if len(args) <= 0:
      # show available rooms & their 'vnum'?
      i_keys = self.game.mobile_list.keys()
      buf = ""
      for i in range(0, len(i_keys)):
        mobile = self.game.mobile_list[i_keys[i]]
        buf += str(i) + ": " + mobile["name"] + "\n\r"
      sender.sendToClient(buf)
    elif args[0].isdigit():
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
    if len(args) <= 0:
      buf = "Players: \n\r"
      players = [mobile for mobile in self.game.mobiles if mobile.client]
      for i in range(0, len(players)):
        buf += str(i) + ": " + players[i].name + "\n\r"
      sender.sendToClient(buf)
    elif args[0].isdigit():
      players = [mobile for mobile in self.game.mobiles if mobile.client]
      vnum = int(args.pop(0))
      #args.remove(0)
      if vnum < len(players):
        player = players[vnum]
        if len(args) == 0:
          sender.sendToClient(player.name)
        else:
          player.processCommand(" ".join(args))

class SetStat(Command):
  def __init__(self, game):
    super(SetStat, self).__init__(game, 'setstat')

  def execute(self, args, config):
    sender = config['sender']
    #quick double check here, but only immortals should even have this command
    if len(args) <= 0:
      buf = "Players: \n\r"
      players = [mobile for mobile in self.game.mobiles if mobile.client]
      for i in range(0, len(players)):
        buf += str(i) + ": " + players[i].name + "\n\r"
      sender.sendToClient(buf)
    elif args[0].isdigit():
      players = [mobile for mobile in self.game.mobiles if mobile.client]
      vnum = int(args.pop(0))
      #args.remove(0)
      if vnum < len(players):
        player = players[vnum]
        if len(args) >= 2:
          if args[0] in player.stats:
            player.stats[args[0]] = args[1]
        else:
          sender.sendToClient("Stats:\n\r" + "\n\r".join([str(key) + ": " + str(value) for key, value in player.stats.iteritems()]))


class Reload(Command):
  def __init__(self, game):
    super(Reload, self).__init__(game, 'reload')

  def execute(self, args, config):
    sender = config['sender']
    [mobile.sendToClient('reloading objects... started') for mobile in self.game.mobiles]
    self.game.loadItems()
    self.game.loadMobiles()
    [mobile.sendToClient('reloading objects... done') for mobile in self.game.mobiles]    

class Repop(Command):
  def __init__(self, game):
    super(Repop, self).__init__(game, 'repop')

  def execute(self, args, config):
    sender = config['sender']
    [mobile.sendToClient('repopulating rooms... started') for mobile in self.game.mobiles]
    self.game.repopulate()
    [mobile.sendToClient('repopulating rooms... done') for mobile in self.game.mobiles]

class WizInfo(Command):
  def __init__(self, game):
    super(WizInfo, self).__init__(game, 'wizinfo')

  def execute(self, args, config):
    sender = config['sender']
    buf = """
      <b>Commands</b>: (1) (2) (...) description (with 1) (with 2) (...)\n\r
      -----------------------------------------------------\n\r
      <b>Goto</b>: (i) display list of rooms (go to room by i)\n\r
      <b>CreateItem</b>: (i) display list of items (create item by i)\n\r
      <b>SpawnMobile</b>: (i) display list of npc mobiles (create mobile by i)\n\r
      <b>PlayerList</b>: (i) (c) display list of players (player info by i) (player[i] execute 'c')\n\r
      <b>Reload</b>: reload item/mobile lists from database\n\r
      <b>Repop</b>: repopulate rooms with items/npcs/exits as defined in database\n\r
      <b>WizInfo</b>: you're looking at it
    """
    sender.sendToClient(buf)

commandList = [Goto, CreateItem, SpawnMobile, PlayerList, Reload, Repop, SetStat, WizInfo]