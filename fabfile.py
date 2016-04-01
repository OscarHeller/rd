from fabric.api import *

env.hosts = ['104.236.28.149']
env.user = 'root'

def commit():
	local('git add . && git commit')

def push():
	local('git push')

def pull():
	code_dir = '~/rd'
	with cd(code_dir):
		run('git pull')

def kill():
	with settings(warn_only=True):
		run('killall -9 python')

def database():
	run('service mongod status')

def restart():
	run('python ~/rd/game/game.py')
	run('python ~/rd/web/web.py')

def deploy():
	commit()
	push()
	pull()
	kill()
	database()
	restart()

