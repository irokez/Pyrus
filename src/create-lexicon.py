#!/usr/bin/env python3
'''
Created on Aug 6, 2011

@author: alexpak
'''

import sys
import os
import rnc
import sqlite3

if len(sys.argv) < 3:
	exit('Usage: create-lexicon.py filename dbname')
	
dbname = sys.argv[2]
db_exists = os.path.isfile(dbname)
con = sqlite3.connect(dbname)
cur = con.cursor()

def create_db():
	sql = '''
	create table words(
		id integer primary key autoincrement,
		lemma text,
		form text,
		accent integer,
		info text,
		freq integer
	);
	create index words_lemma_form_info_accent on words(lemma, form, info, accent);
	'''
	[cur.execute(st) for st in sql.split(';') if len(st.strip())]

if not db_exists:
	create_db()

sentences = rnc.Reader().read(sys.argv[1])
for sentence in sentences:
	for word in sentence:
		accent = word[0].index('`') + 1 if '`' in word[0] else 0 
		form = word[0].replace('`', '')
		lemma = word[1]['lex']
		info = word[1]['gr']
		
		cur.execute('select id from words where lemma = ? and form = ? and info = ? and accent = ?', (lemma, form, info, accent))
		row = cur.fetchone()
		if row is None:
			cur.execute('insert into words (lemma, form, info, accent, freq) values (?, ?, ?, ?, 1)', (lemma, form, info, accent))
		else:
			cur.execute('update words set freq = freq + 1 where id = ?', row)
		
con.commit()
con.close()