from base import BaseHandler

class EditorHandler(BaseHandler):
  def get(self):
    self.validateInternalPageAccess()

    self.render('editor.html')

  def post(self):
    user_id = self.get_current_user()
    if user_id:    
        rooms = [room for room in self.get_rooms()]
        items = [item for item in self.get_items()]
        npcs = [npc for npc in self.get_npcs()]
        images = [image for image in self.get_images()]
        recipes = [recipe for recipe in self.get_recipes()]
        result = {'rooms': rooms, 'items': items, 'npcs': npcs, 'images': images, 'recipes': recipes}
        from bson.json_util import dumps
        self.write(dumps(result))

  def patch(self):
    user_id = self.get_current_user()
    if user_id:
        from bson.json_util import loads
        data = loads(self.get_argument('data'))
        newRoomData = data['rooms']
        newItemData = data['items']
        newNPCData = data['npcs']
        newRecipeData = data['recipes']
        #newRoomData = self.get_argument('rooms')
        #newItemData = self.get_argument('items')
        #newNPCData = self.get_argument('npcs')
        # hang on ... print newRoomData here again - is the string itself cut off?!
        #from bson.json_util import loads
        self.set_rooms(newRoomData)
        self.set_items(newItemData)
        self.set_npcs(newNPCData)
        self.set_recipes(newRecipeData)