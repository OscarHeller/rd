import copy

import lib.item
from lib.interpreters.command import Command
from lib.interpreters.constants import Position, Range


class Craft(Command):
	def __init__(self, game):
		super(Craft, self).__init__(game, 'craft')

	def execute(self, args, sender):
		try:
			# Preliminary checks
			self.checkPosition(sender, [Position.standing,])

			if not args:
				msg = 'What do you want to craft?'
				self.appendToCommandBuffer(sender, msg)
				return

			recipeName = args[0]

			# Does the recipe exist?
			recipe = next((r for r in self.game.recipes if r.name == recipeName), None)

			if not recipe:
				msg = 'That recipe doesn\'t exist.'
				self.appendToCommandBuffer(sender, msg)
				return

			# Do you have the ingredients? Go ingredient by ingredient, get the count, then loop through your inventory to count
			for ingredient in recipe.ingredients:
				ingredientName = str(ingredient)

				numberNeeded = recipe.ingredients[ingredient]
				numberYouHave = 0

				for item in sender.inventory:
					if item.name == ingredientName:
						numberYouHave += 1

				if numberNeeded > numberYouHave:
					sender.sendToClient('You don\'t have enough {ingredient}. You need {number}.'.format(ingredient=ingredient, number=numberNeeded))
					return

			# You have enough of each. Take them out of your inventory and give you the recipe result

			craftingBuffer = ''

			tempInventory = copy.copy(sender.inventory)
			for ingredient in recipe.ingredients:
				ingredientName = str(ingredient)
				numberNeeded = recipe.ingredients[ingredient]

				# Get the object associated with that name (REFACTOR: should be ID)

				for item in sender.inventory:
					if item.name == ingredientName:
						tempInventory.remove(item)
						numberNeeded -= 1
						craftingBuffer += '{name} is consumed.\n\r'.format(name=item.name)

						if numberNeeded <= 0:
							break

			sender.inventory = tempInventory

			# Give them the recipe result

			newItem = copy.deepcopy(recipe.result)
			sender.inventory.append(newItem)

			craftingBuffer += 'You receive {newItem}.'.format(newItem=newItem.name)
			sender.sendToClient(craftingBuffer)
		except self.CommandException as e:
			self.exceptionOccurred = True


class craftingIngredient(lib.item.Item):
	def __init__(self, config):
		lib.item.Item.__init__(self, config)
		self.__repr__ = self.__str__

	def __str__(self):
		return self.name


class craftingRecipe:
	def __init__(self, name):
		self.ingredients = {}
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
