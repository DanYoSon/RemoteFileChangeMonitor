import sqlite3
import logging
import pprint
log = logging.getLogger(__name__)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class dbClass:
	#Initialize Database
	def __init__(self, dbpath):
		log.debug('Opening: ' + dbpath)
		try:
			self.dbCon = sqlite3.connect(dbpath)
			self.dbCon.row_factory = dict_factory
			self.db = self.dbCon.cursor()
			self.db.execute('CREATE TABLE IF NOT EXISTS files (filepath TEXT UNIQUE, moddate INTEGER, size INTEGER)')
			log.debug('Opened: %s' % dbpath)
		except Exception as e:
			log.error(str(e))
			pass

	#Get file 
	#Args
	#-file: python dict of {path:"",moddate:"",size:""}
	def getFile(self, file):
		log.debug('Getting file: ' + file['path'])
		try:
			self.db.execute('SELECT * FROM files WHERE filepath = ?', (file['path'],))
			return self.db.fetchone()
		except Exception as e:
			log.error(str(e))
			return False
		pass

	#Set file 
	#Args
	#-file: python dict of {path:"",moddate:"",size:""}
	def setFile(self, file):
		log.debug('Setting file: ' + file['path'])
		try:
			self.db.execute('INSERT INTO files (filepath, moddate, size) VALUES (?,?,?)',(file['path'], file['moddate'], file['size']))
			self.dbCon.commit()
			return self.db.fetchone()
		except Exception as e:
			log.error(str(e))
			return False
		pass

	def updateFile(self, file):
		log.debug('Updateing file: ' + file['path'])
		try:
			self.db.execute('UPDATE files SET moddate=?, size=? WHERE filepath=?',(file['moddate'], file['size'], file['path']))
			self.dbCon.commit()
			return self.db.fetchone()
		except Exception as e:
			log.error(str(e))
			return False
		pass