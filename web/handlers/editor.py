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

    from bson.json_util import loads
    data = loads(self.get_argument('data'))
    newRoomData = data['rooms']
    newItemData = data['items']
    newNPCData = data['npcs']
    #newRoomData = self.get_argument('rooms')
    #newItemData = self.get_argument('items')
    #newNPCData = self.get_argument('npcs')
    # hang on ... print newRoomData here again - is the string itself cut off?!
    print data
    #from bson.json_util import loads
    self.set_rooms(newRoomData)
    self.set_items(newItemData)
    self.set_npcs(newNPCData)