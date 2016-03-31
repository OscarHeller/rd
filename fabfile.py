from fabric.api import local

def deploy():
	local('git add . && git commit')
	local('git push')