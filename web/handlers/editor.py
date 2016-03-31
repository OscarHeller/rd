from base import BaseHandler

class EditorHandler(BaseHandler):
  def get(self):
    self.render('editor.html')

  def post(self):
    rooms = [room for room in self.get_rooms()]
    items = [item for item in self.get_items()]
    npcs = [npc for npc in self.get_npcs()]
    result = {'rooms': rooms, 'items': items, 'npcs': npcs}
    from bson.json_util import dumps
    self.write(dumps(result))

  def patch(self):
    newRoomData = self.get_argument('rooms')
    newItemData = self.get_argument('items')
    newNPCData = self.get_argument('npcs')
    from bson.json_util import loads
    self.set_rooms(loads(newRoomData))
    self.set_items(loads(newItemData))
    self.set_npcs(loads(newNPCData))