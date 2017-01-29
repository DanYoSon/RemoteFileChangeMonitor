import logging as log
import configparser, json, os, reachmail, base64
import subprocess as sp

import inc.db_sqlite3 as dbClass
#Initialize Logging
log.basicConfig(level=log.INFO)
log.info('Logging Started')

#Initialize Config
conf = configparser.ConfigParser()
conf.read('data/config.ini')

#Initialize Reachmail API
def getAccountGuid(api):
	res = api.adminsitration.users_current()
	if res[0] == 200 :
		data=json.loads(res[1].decode('utf-8')) #parse json response
		log.info('ReachMail AccountKey %s' % (data['AccountKey'],))
		return(data['AccountId'])
	else:
		log.error('ReachMail Failed Status Code: %s Response: %s' % (res[0], res[1]))
		exit(1)

mail = reachmail.ReachMail(conf['General']['reachmailapikey'])
AccountId = getAccountGuid(mail)

#Get all section names and remove the first (General) section
sites = conf.sections()
sites.pop(0)

for configname in sites:
	#Variables
	sitepath = os.getcwd() + '/data/' + configname
	modifiedformat = 'm,%s,%s\n'
	newformat = 'n,%s,%s\n'
	reportdata = ''

	db = dbClass.dbClass(sitepath + '.db')
	#http://stackoverflow.com/questions/2715847/python-read-streaming-input-from-subprocess-communicate
	command = [
		'ssh',
		'-i',
		'%s/data/%s' % (os.getcwd(),configname,),
		'-p',
		conf[configname]['ssh_port'],
		'%s@%s' % (conf[configname]['ssh_user'], conf[configname]['ssh_host']),
		'find',
		conf[configname]['scanfolder'],
		'-type',
		'f',
		'-exec',
		'stat',
		'-c',
		'\\{\\"path\\":\\"%n\\",\\"moddate\\":\\"%Z\\",\\"size\\":\\"%s\\"\\}',
		'{}',
		'\\;'
		]
	print(' '.join(command))
	with sp.Popen(command, stdout=sp.PIPE, bufsize=1, universal_newlines=True) as p:
		for line in p.stdout:
			oFile = json.loads(line)
			oExisting = db.getFile(oFile)
			if oExisting != None:
				log.debug('%s last modified %s' % (oFile['path'],str(oExisting['moddate'])))
				if int(oFile['moddate']) > oExisting['moddate']:
					log.warning('%s has been modified' % (oFile['path'],))
					reportdata += modifiedformat % (oFile['path'], oFile['moddate'])
					db.updateFile(oFile)
					pass
				pass
			else:
				log.info('%s is a NEW file' % (oFile['path'],))
				reportdata += newformat % (oFile['path'], oFile['moddate'])
				db.setFile(oFile)
				pass 

	emaildata={
	'FromAddress': conf[configname]['email_from'],
	'Recipients': [
		{
			'Address': conf[configname]['email_to']
        }
	],
	'Subject': conf[configname]['email_subject'] ,
  	'Headers': { 
		'From': conf[configname]['email_header_from'] , 
		'X-Company': conf[configname]['email_header_company'] 
	}, 
	'BodyText': 'Attached is the file change report',
	'BodyHtml': 'Attached is the file change report', 
	'Tracking': 'true',
	'Attachments': [
		{
			'Filename': '%s.csv' % (configname,),
			'Data': base64.b64encode(reportdata.encode()).decode(),
			'ContentType': 'text/csv',
			'ContentDisposition': 'attachment'
		}
	]
	}

	if reportdata != '':
		#Remove previous report file
		try:
			os.remove(sitepath + '.report')
		except OSError:
			pass
		#Open report
		report = open(sitepath + '.report', 'w')
		report.write(reportdata)
		report.close()
		
		send = mail.easysmtp.delivery(AccountId=AccountId, Data=emaildata)
		if send[0] == 200:
			log.info('Sent Report')
		else:
			log.error('Could not Deliver message. Status Code: %s Response: %s' % (send[0], send[1]))
			exit(1)