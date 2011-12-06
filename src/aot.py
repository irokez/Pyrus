#!/usr/bin/env python3
import sqlite3
import re
import os
import memcache

class Morphology:
	conn = None
	db = None
	cache = {}
	
	def __init__(self, db, lexicon = None):
		load = False
		if not os.path.exists(db):
			load = True
			
		self.conn = sqlite3.connect(db, check_same_thread = False)
		self.mc = memcache.Client(['127.0.0.1:11211'], debug=0)

#		def re_match(a, b):
#			return re.match(a, b) is not None
#		
#		def concat(a, b):
#			return a + b
#			
#		self.conn.create_function('re_match', 2, re_match)
#		self.conn.create_function('concat', 2, concat)
		
		self.db = self.conn.cursor()

		if load:
			self.load(lexicon)
			
	def close(self):
		self.db.close()
		self.conn.close()
			
	def skip_lines(self, handle):
		line = handle.readline()
		if not len(line):
			return False
		
		line = line.strip()
		if re.search('^\d+$', line):
			for i in range(0, int(line)):
				line = handle.readline()
				if not len(line):
					return False
		else:
			print(line)
			return False 
		
		return True

	def load(self, file):
		handle = open(file, 'r', encoding='cp1251')
		
		# load rules
		self.load_rules(handle)
		
		# skip accents
		if not self.skip_lines(handle):
			return False
		
		# skip logs
		if not self.skip_lines(handle):
			return False
		
		# skip prefixes
		if not self.skip_lines(handle):
			return False
		
		print(self.load_lemmas(handle), 'lemmas loaded')
		
		handle.close()
		
	def load_rules(self, handle):
		# create table
		self.db.execute('''create table rules(
							id integer,
							prefix text,
							suffix text)''')
		
		lines = handle.readline().strip()
		reg_split = re.compile('\\%');
		alf = '\w';
		reg_rule = re.compile('^(?P<suffix>' + alf + '*)\\*(?P<ancode>' + alf + '+)(?:\\*(?P<prefix>' + alf + '+))?$')
		
		for i in range(0, int(lines)):
			line = handle.readline()
			if not len(line):
				break
			
			rules = reg_split.split(line.strip())
			
			for rule in rules:
				match = reg_rule.search(rule)
				if match is not None:
					record = match.groupdict()				  
					if 'prefix' not in record or record['prefix'] is None:
						record['prefix'] = ''
						
					suffix = record['suffix'].lower()
					prefix = record['prefix'].lower()
					
					self.db.execute('insert into rules (id, prefix, suffix) values (?, ?, ?)', (i, prefix, suffix))

		self.db.execute('create index rules_id on rules(id)')
		return i
	
	def load_lemmas(self, handle):
		# create table
		self.db.execute('''create table lemmas(
							base text,
							rule integer)''')

		lines = int(handle.readline().strip())
		reg_split = re.compile('\s+')
		
		for i in range(0, lines):
			line = handle.readline()
			if not len(line):
				break
			
			record = reg_split.split(line)
			self.db.execute('insert into lemmas values(?, ?)', (record[0].lower() + '%', int(record[1])))
			
		self.db.execute('create index lemmas_base on lemmas(base)')
		
		return i
	
	def make_forms(self, lemma):
		self.db.execute('select prefix, suffix from rules where id = ?', (lemma['rule'],))

		forms = []
		for rule in self.db.fetchall():
			forms.append({
						  'base': lemma['base'],
						  'form': rule[0] + lemma['base'] + rule[1],
						  })
		return forms

	def normalize(self, word):
		word = word.lower()

		lemmas = self.mc.get(word)
		if lemmas is None:
#		if word not in self.cache:
			self.db.execute('select base, rule from lemmas where ? like base', (word,))
			
			lemmas = []
			for lemma in self.db.fetchall():
				base = lemma[0][0:-1]
				forms = self.make_forms({'base': base, 'rule': lemma[1]})
				for form in forms:
#					print(word, form['form'])
					if word == form['form']:
						init_form = forms[0]['form']
						lemmas.append(init_form)
						
#			self.cache[word] = set(lemmas)
			lemmas = set(lemmas)
			self.mc.set(word, lemmas)
					
		return lemmas

if __name__ == '__main__':
	from optparse import OptionParser
	parser = OptionParser()
	parser.usage = '%prog [options]'
	parser.add_option('-i', '--index', action='store_const', const=True, dest='index')
	parser.add_option('-d', '--database', action='store', type='string', dest='database')
	
	(options, args) = parser.parse_args()
	if options.index:
		morphology = Morphology(options.database, args[0])
		print('Done')
	else:
		morphology = Morphology(options.database)
		print(morphology.normalize(args[0]))