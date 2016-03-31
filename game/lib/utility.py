import re


# utility functions
def match(search, target):
	return re.match(search, target, re.I)


def matchList(search, listOfTargets):
	for target in listOfTargets:
		if re.match(search, target, re.I):
			return True
	return False
