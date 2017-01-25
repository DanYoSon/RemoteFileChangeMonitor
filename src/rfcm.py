import logging as log
import configparser, json, os, pprint
import subprocess as sp

import inc.db_sqlite3 as dbClass
#Initialize Logging
log.basicConfig(level=log.INFO)
log.info('Logging Started')
#TODO: log to file

#Initialize Config
conf = configparser.ConfigParser()
conf.read('data/config.ini')

#Get all section names and remove the first (General) section
sites = conf.sections()
sites.pop(0)

for configname in sites:
	db = dbClass.dbClass(os.getcwd() + '/data/' + configname + '.db')
	#http://stackoverflow.com/questions/2715847/python-read-streaming-input-from-subprocess-communicate
	command = [
		#'ssh',
		#'conf[configname]["sshid"]',
		'find',
		'/home/rfcm',
		'-type',
		'f',
		'-exec',
		'stat',
		'-c',
		'{"path":"%n","moddate":"%Z","size":"%s"}',
		'{}',
		';'
		]
	with sp.Popen(command, stdout=sp.PIPE, bufsize=1, universal_newlines=True) as p:
	    for line in p.stdout:
	    	oFile = json.loads(line)
	    	oExisting = db.getFile(oFile)
	    	if oExisting != None:
	    		log.debug('%s last modified %s' % (oFile['path'],str(oExisting['moddate'])))
	    		if int(oFile['moddate']) > oExisting['moddate']:
	    			log.warning('%s has been modified' % (oFile['path'],))
	    			db.updateFile(oFile)
	    			pass
	    		pass
	    	else:
	    		log.info('%s is a NEW file' % (oFile['path'],))
	    		db.setFile(oFile)
	    		pass 

	        