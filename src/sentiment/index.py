#!/usr/bin/env python3

import sqlite3
import re
from yatk import ir
from collections import defaultdict

con = sqlite3.connect('test.db')
con.row_factory = sqlite3.Row
cur = con.cursor()

cur.execute('''
	create table if not exists ngrams (
		id integer primary key autoincrement,
		body text,
		n_pos integer,
		n_neg integer
	)
	''')

count = defaultdict(lambda: {'pos': 0, 'neg': 0})

cur.execute('select class, text from docs')
for row in cur.fetchall():
	words = ir.tokenize(row['text'].lower())
	ngrams = set(words + ir.ngrams(words, 2))
	for ngram in ngrams:
		count[ngram]['pos'] += row['class'] == 'pos'
		count[ngram]['neg'] += row['class'] == 'neg'

for ngram_id, ngram_count in count.items():
	cur.execute('insert into ngrams (body, n_pos, n_neg) values (?, ?, ?)', (ngram_id, ngram_count['pos'], ngram_count['neg']))

cur.execute('create index ngrams_body on ngrams(body)')

con.commit()
con.close()