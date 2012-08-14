#!/usr/bin/env python3

import requests
import time
import sqlite3
from bs4 import BeautifulSoup as soup

def download(cl, limit):
	url = 'http://www.kinopoisk.ru/review/type/comment/status/{0}/period/year/perpage/100/page/{1}/'

	texts = []
	p = 1

	while True:
		r = requests.get(url.format(cl, p))
		s = soup(r.text)
		for div in s.find_all('div', {'class': 'userReview'}):
			div_resp = div.find('div', {'class': 'response'})
			div_text = div.find('div', {'class': 'brand_words'})

			texts.append((div_text.text,))

		print('Processed page {0}, {1} texts'.format(p, len(texts)))
		if len(texts) >= limit:
			break

		p += 1
		time.sleep(1)

	return texts[:limit]

con = sqlite3.connect('test.db')
cur = con.cursor()

cur.execute('''
	create table docs(
		id integer primary key autoincrement,
		text text,
		class text
	)
	''')

limit = 500

texts_pos = download('good', limit)
texts_neg = download('bad', limit)

cur.executemany('insert into docs (class, text) values ("pos", ?)', texts_pos)
cur.executemany('insert into docs (class, text) values ("neg", ?)', texts_neg)

con.commit()
con.close()