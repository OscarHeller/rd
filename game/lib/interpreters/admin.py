import lib.utility as utility
from lib.interpreters.command import Command
from lib.item import Item

class Goto(Command):
  def __init__(self, game):
    super(Goto, self).__init__(game, 'goto')

  def execute(self, args, sender):
    # Manual targeting
    if len(args) <= 0:
      # show available rooms & their 'vnum'?
        buf = ""
        for i in range(0, len(self.game.rooms)):
          buf += str(i) + ": " + self.game.rooms[i].name + "\n\r"

        self.appendToCommandBuffer(sender, buf)
    elif args[0].isdigit():
      vnum = int(args[0])
      if self.game.rooms[vnum]:
        oldRoom = sender.room
        sender.room = self.game.rooms[vnum]

        msg = 'You vanish in a flash of flame.'
        self.appendToCommandBuffer(sender, msg)

        for mobile in [mobile for mobile in self.game.mobiles if mobile.room == oldRoom and mobile != sender]:
          msg = '{sender} vanishes in a flash of flame.'.format(sender=sender.getName(mobile))
          self.appendToCommandBuffer(mobile, msg)

        for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]:
          msg = '{sender} appears in a flash of flame.'.format(sender=sender.getName(mobile))
          self.appendToCommandBuffer(mobile, msg)
    else:
      msg = 'You must choose a valid room index.'
      self.appendToCommandBuffer(sender, msg)

class CreateItem(Command):
  def __init__(self, game):
    super(CreateItem, self).__init__(game, 'createitem')

  def execute(self, args, sender):
    if len(args) <= 0:
      # show available rooms & their 'vnum'?
      i_keys = self.game.items.keys()
      buf = ""
      for i in range(0, len(i_keys)):
        item = self.game.items[i_keys[i]]
        buf += str(i) + ": " + item['name'] + "\n\r"

      self.appendToCommandBuffer(sender, buf)
    elif args[0].isdigit():

      i_keys = self.game.items.keys()
      vnum = int(args[0])
      key = i_keys[vnum] if vnum < len(i_keys) else "bafdlasdfa"
      if key in self.game.items:
        r = sender.room
        item = Item(self.game.items[key])
        sender.room.items.append(item)

        msg = 'You create {item}.'.format(item=item.getName(sender))
        self.appendToCommandBuffer(sender, msg)

        for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]:
          msg = '{sender} creates {item}.'.format(sender=sender.getName(mobile),item=item.getName(mobile))
          self.appendToCommandBuffer(mobile, msg)
    else:
      msg = 'You must choose a valid item index.'
      self.appendToCommandBuffer(sender, msg)

class SpawnMobile(Command):
  def __init__(self, game):
    super(SpawnMobile, self).__init__(game, 'spawnmobile')

  def execute(self, args, sender):
    #quick double check here, but only immortals should even have this command
    if len(args) <= 0:
      # show available rooms & their 'vnum'?
      i_keys = self.game.mobile_list.keys()
      print i_keys
      buf = ""
      for i in range(0, len(i_keys)):
        mobile = self.game.mobile_list[i_keys[i]]
        print mobile
        if 'name' in mobile:  # FIX ME: Is self.game.mobile_list clean? I saw some weird stuff if I did 'print mobile' in an else clause here
          buf += str(i) + ": " + mobile["name"] + "\n\r"

      self.appendToCommandBuffer(sender, buf)
    elif args[0].isdigit():
      from lib.mobile import Mobile

      i_keys = self.game.mobile_list.keys()
      vnum = int(args[0])
      key = i_keys[vnum] if vnum < len(i_keys) else "bafdlasdfa"
      if key in self.game.mobile_list:
        i = self.game.mobile_list[key]
        m = Mobile(i['name'], self.game, i)
        m.room = sender.room
        self.game.mobiles.append(m)

        msg = "You spawn {mobile}.".format(mobile=m.getName(sender))
        self.appendToCommandBuffer(sender, msg)

        for mobile in [mobile for mobile in self.game.mobiles if mobile.room == sender.room and mobile != sender]:
          msg = "{sender} spawns {mobile}.".format(sender=sender.getName(mobile),mobile=m.getName(mobile))
          self.appendToCommandBuffer(mobile, msg)
    else:
      msg = 'You must choose a valid mobile index.'
      self.appendToCommandBuffer(sender, msg)

class MovePlayer(Command):
  def __init__(self, game):
    super(MovePlayer, self).__init__(game, 'moveplayer')

  def execute(self, args, sender):
    #quick double check here, but only immortals should even have this command
    if len(args) <= 0:
      buf = "Players: \n\r"
      players = [mobile for mobile in self.game.mobiles if mobile.client]
      for i in range(0, len(players)):
        buf += str(i) + ": " + players[i].name + "\n\r"

      self.appendToCommandBuffer(sender, buf)
    elif args[0].isdigit():
      players = [mobile for mobile in self.game.mobiles if mobile.client]
      vnum = int(args[0])
      #args.remove(0)
      if vnum < len(players):
        player = players[vnum]
        rooms = self.game.rooms
        if len(args) <= 1:
          buf = "Rooms: \n\r"
          for i in range(0, len(rooms)):
            buf += '{index}: {name}\n\r'.format(index=i, name=rooms[i].name)
          self.appendToCommandBuffer(sender, buf)
        elif args[1].isdigit() and int(args[1]) < len(rooms):
          room_id = int(args[1])
          self.appendToCommandBuffer(sender, "You move {player} to {room}".format(player=player.name, room=rooms[room_id].name))
          self.appendToCommandBuffer(player, "You find yourself suddenly in {room}".format(room=rooms[room_id].name))
          player.room = rooms[room_id]
          # FIX ME: should force save for player that has been moved, so they can't relog quickly to escape!
        else:
          self.appendToCommandBuffer(sender, "Invalid Room Id")
      else:
        msg = 'You must choose a valid player index.'
        self.appendToCommandBuffer(sender, msg)        
    else:
      msg = 'You must choose a valid player index.'
      self.appendToCommandBuffer(sender, msg)

class PlayerList(Command):
  def __init__(self, game):
    super(PlayerList, self).__init__(game, 'playerlist')

  def execute(self, args, sender):
    #quick double check here, but only immortals should even have this command
    if len(args) <= 0:
      buf = "Players: \n\r"
      players = [mobile for mobile in self.game.mobiles if mobile.client]
      for i in range(0, len(players)):
        buf += str(i) + ": " + players[i].name + "\n\r"

      self.appendToCommandBuffer(sender, buf)
    elif args[0].isdigit():
      players = [mobile for mobile in self.game.mobiles if mobile.client]
      vnum = int(args.pop(0))
      #args.remove(0)
      if vnum < len(players):
        player = players[vnum]
        if len(args) == 0:
          msg = '{player}'.format(player=player.getName(sender))
          self.appendToCommandBuffer(sender, msg)
        else:
          player.processCommand(" ".join(args))
    else:
      msg = 'You must choose a valid player index.'
      self.appendToCommandBuffer(sender, msg)

class SetStat(Command):
  def __init__(self, game):
    super(SetStat, self).__init__(game, 'setstat')

  def execute(self, args, sender):
    if len(args) <= 0:
      buf = "Players: \n\r"
      players = [mobile for mobile in self.game.mobiles if mobile.is_player]
      for i in range(0, len(players)):
        buf += str(i) + ": " + players[i].name + "\n\r"

      self.appendToCommandBuffer(sender, buf)
    elif args[0].isdigit():
      players = [mobile for mobile in self.game.mobiles if mobile.is_player]
      vnum = int(args.pop(0))
      #args.remove(0)
      if vnum < len(players):
        player = players[vnum]
        if len(args) >= 2:
          if args[0] in player.stats:
            player.setStat(args[0], args[1])

            msg = 'You set {player}\'s {stat} to {value}.'.format(player=player.getName(sender),stat=args[0],value=args[1])
            self.appendToCommandBuffer(sender, msg)

            msg = '{sender} set your {stat} to {value}.'.format(sender=sender.getName(player),stat=args[0],value=args[1])
            self.appendToCommandBuffer(player, msg)
          else:
            msg = 'That\'s not a valid stat.'
            self.appendToCommandBuffer(sender, msg)
        else:
          msg = "Stats:\n\r" + "\n\r".join([str(key) + ": " + str(value) for key, value in player.stats.iteritems()])
          self.appendToCommandBuffer(sender, msg)
    else:
      msg = 'You must choose a valid player index.'
      self.appendToCommandBuffer(sender, msg)


class Reload(Command):
  def __init__(self, game):
    super(Reload, self).__init__(game, 'reload')

  def execute(self, args, sender):
    msg = 'Reload started.'
    self.appendToCommandBuffer(sender, msg)

    self.game.loadItems()
    self.game.loadMobiles()

    msg = 'Reload complete.'
    self.appendToCommandBuffer(sender, msg)

class Repop(Command):
  def __init__(self, game):
    super(Repop, self).__init__(game, 'repop')

  def execute(self, args, sender):
    msg = 'Repop started.'
    self.appendToCommandBuffer(sender, msg)

    self.game.repopulate()

    msg = 'Repop complete.'
    self.appendToCommandBuffer(sender, msg)

class WizInfo(Command):
  def __init__(self, game):
    super(WizInfo, self).__init__(game, 'wizinfo')

  def execute(self, args, sender):
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
    self.appendToCommandBuffer(sender, buf)

commandList = [Goto, CreateItem, SpawnMobile, PlayerList, Reload, Repop, SetStat, WizInfo, MovePlayer]