from enum import IntEnum


class Position(IntEnum):
	sleeping = 0
	resting = 1
	standing = 2
	fighting = 3


class Range(IntEnum):
	self = 0
	room = 1
	area = 2
	game = 3
