from fabric.api import local, run, cd

def commit():
	local('git add . && git commit')

def push():
	local('git push')

def pull():
	code_dir = '~/rd'
	with cd(code_dir):
		run('git pull')

def deploy():
	commit()
	push()
	pull()