import copy

import lib.item
from lib.interpreters.command import Command
from lib.interpreters.constants import Position, Range


class Craft(Command):
	def __init__(self, game):
		super(Craft, self).__init__(game, 'craft')

	def execute(self, args, sender):
		# Preliminary checks
		self.test(self.checkPosition, (sender, [Position.standing,]))
		self.test(self.hasAtLeastOneArgument, args, override='What do you want to craft?')

		recipeName = args[0]

		# Does the recipe exist?
		recipe = next((r for r in self.game.recipes if r.name == recipeName), None)

		if not recipe:
			self.error('That recipe doesn\'t exist.')

		ingredients = [ingredient['_id'] for ingredient in recipe.ingredients]
		quantities = {ingredient: ingredients.count(ingredient) for ingredient in set(ingredients)}
		# Do you have the ingredients? Go ingredient by ingredient, get the count, then loop through your inventory to count
		print quantities

		for field, value in quantities.iteritems():
			numberNeeded = value
			numberYouHave = 0

			for item in sender.inventory:
				print item.id, field
				if item.id == field:
					print "got one!"
					numberYouHave += 1

			if numberNeeded > numberYouHave:
				self.error('You don\'t have all the ingredients - double check your recipe!')

		for field, value in quantities.iteritems():
			matching = [item for item in sender.inventory if item.id == field]
			for i in range(0, value):
				sender.inventory.remove(matching[i])
				self.appendToCommandBuffer(sender, "Using one '{item}'...".format(item=matching[i].name))

		product = lib.item.Item(recipe.product)
		sender.inventory.append(product)
		self.appendToCommandBuffer(sender, "You craft a brand new {product}!".format(product=product.getName(sender)))

		for mobile in sender.inRoomExcept(sender):
			msg = '{sender} crafts a brand new {product}.'.format(sender=sender.getName(mobile), product=product.getName(mobile))
			self.appendToCommandBuffer(mobile, msg)

class craftingIngredient(lib.item.Item):
	def __init__(self, config):
		lib.item.Item.__init__(self, config)
		self.__repr__ = self.__str__

	def __str__(self):
		return self.name


class craftingRecipe:
	def __init__(self, name):
		self.ingredients = []
		self.name = name


def craftingInit(game):
	# Add ingredients
	patternShard = craftingIngredient({'name': 'a pattern shard', 'keywords': ['pattern', 'shard']})
	livingChaos = craftingIngredient({'name': 'a piece of living chaos', 'keywords': ['piece', 'living', 'chaos']})
	shadowWisp = craftingIngredient({'name': 'a wisp of shadow', 'keywords': ['wisp', 'shadow']})

	# Add results
	grayswandir = lib.item.Item(
		{'name': 'Grayswandir', 'keywords': ['pattern', 'blade', 'grayswandir'], 'wear': 'weapon', 'stats': {'damage': 50, 'attackSpeed': 5}})
	werewindle = lib.item.Item(
		{'name': 'Werewindle', 'keywords': ['chaos', 'blade', 'werewindle'], 'wear': 'weapon', 'stats': {'damage': 200, 'attackSpeed': 1}})

	game.rooms[0].items.append(copy.deepcopy(patternShard))
	game.rooms[0].items.append(copy.deepcopy(patternShard))
	game.rooms[0].items.append(copy.deepcopy(patternShard))
	game.rooms[0].items.append(copy.deepcopy(livingChaos))
	game.rooms[0].items.append(copy.deepcopy(livingChaos))
	game.rooms[0].items.append(copy.deepcopy(livingChaos))
	game.rooms[0].items.append(copy.deepcopy(shadowWisp))
	game.rooms[0].items.append(copy.deepcopy(shadowWisp))
	game.rooms[0].items.append(copy.deepcopy(shadowWisp))

	# Add recipe

	grayswandirRecipe = craftingRecipe('grayswandir')

	grayswandirRecipe.result = grayswandir

	grayswandirRecipe.ingredients[patternShard.name] = 2
	grayswandirRecipe.ingredients[shadowWisp.name] = 1

	werewindleRecipe = craftingRecipe('werewindle')

	werewindleRecipe.result = werewindle

	werewindleRecipe.ingredients[livingChaos.name] = 1
	werewindleRecipe.ingredients[shadowWisp.name] = 1
	werewindleRecipe.ingredients[patternShard.name] = 1

	game.recipes.append(grayswandirRecipe)
	game.recipes.append(werewindleRecipe)

commandList = [Craft]
