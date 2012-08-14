#!/usr/bin/env python3

import sqlite3
from yatk import ir
from yatk.ml.svm import SVM as Classifier
# from yatk.ml.nb import NaiveBayes as Classifier

con = sqlite3.connect('test.db')
con.row_factory = sqlite3.Row
cur = con.cursor()

docs = []
cur.execute('select class, text from docs')
for row in cur.fetchall():
	docs.append((row['class'], row['text']))

index = ir.SentimentIndex('delta', 'bogram')
index.get_class = lambda x: x[0]
index.get_text = lambda x: x[1]
index.build(docs)

x = []
y = []
for doc in docs:
	x.append(index.weight(index.features(doc)))
	y.append(doc[0])

cl = Classifier()
cl.train(x, y)
cl.save('test.svm')

index.save('test.index')

con.close()