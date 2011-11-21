#!/usr/bin/env python3
'''
Created on Nov 21, 2011

@author: alexpak
'''
import os
import sqlite3
import xml.parsers.expat
import glob
from optparse import OptionParser

class Reader:
	def __init__(self):
		self._parser = xml.parsers.expat.ParserCreate()
		self._parser.StartElementHandler = self.start_element
		self._parser.EndElementHandler = self.end_element
		self._parser.CharacterDataHandler = self.char_data		
	
	def start_element(self, name, attr):
		if name == 'W':
			self._info = attr
			self._cdata = ''
	
	def end_element(self, name):
		if name == 'S':
			self._sentences.append(self._sentence)
			self._sentence = []
		elif name == 'W':
			self._sentence.append((self._cdata, self._info))
			self._cdata = ''
	
	def char_data(self, content):
		self._cdata += content
		
	def read(self, filename):
		f = open(filename, encoding='windows-1251')
		content = f.read()
		f.close()
		content = content.replace('encoding="windows-1251"', 'encoding="utf-8"')
		
		self._sentences = []
		self._sentence = []
		self._cdata = ''
		self._info = ''
		
		self._parser.Parse(content)		
		
		return self._sentences

class Lexicon:
	def __init__(self, dbname):
		self.dbname = dbname
		db_exists = os.path.isfile(dbname)
		self.con = sqlite3.connect(dbname)
		self.cur = self.con.cursor()
		
		if not db_exists:
			self.create_db()		
	
	def create_db(self):
		sql = '''
        create table words(
        	id integer primary key autoincrement,
        	lemma text,
        	form text,
        	info text,
        	freq integer
        );
        create index words_lemma_form_info on words(lemma, form, info);
        '''
		[self.cur.execute(st) for st in sql.split(';') if len(st.strip())]
		
	def index(self, filename):
		sentences = Reader().read(filename)
		for sentence in sentences:
			for word in sentence:
				try:
					form = word[0]
					lemma = word[1]['LEMMA']
					info = word[1]['FEAT']
				except:
					print(word)
					continue
				
				self.cur.execute('select id from words where lemma = ? and form = ? and info = ?', (lemma, form, info))
				row = self.cur.fetchone()
				if row is None:
					self.cur.execute('insert into words (lemma, form, info, freq) values (?, ?, ?, 1)', (lemma, form, info))
				else:
					self.cur.execute('update words set freq = freq + 1 where id = ?', row)
					
	def close(self):
		self.con.commit()
		self.con.close()
	
if __name__ == '__main__':
	parser = OptionParser()
	parser.usage = '%prog [options] inputfile'
	parser.add_option('-L', '--construct-lexicon', action = 'store_const', const = True	, dest = 'lexicon', help = 'construct lexicon')

	(options, args) = parser.parse_args()
	
	if options.lexicon:
		L = Lexicon('tmp/lexicon')
		files = glob.glob('res/*/*/*.tgt')
		for file in files:
			L.index(file)
		
		L.close()

	#R = Reader()
	#sentences = R.read(args[0])
	#print(len(sentences))
	#print(sentences[0])
	