from fabric.api import *

env.hosts = ['104.236.28.149']
env.user = 'ghostwheel'

def commit():
	local('git add . && git commit')

def push():
	local('git push')

def pull():
	code_dir = '~/rd'
	with cd(code_dir):
		run('git pull')

def kill():
	run('sudo killall -9 python')

def database():
	run('sudo service mongod status')

def restart():
	pass

def deploy():
	commit()
	push()
	pull()
	kill()
	database()
	restart()