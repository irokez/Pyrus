#!/usr/bin/env python3

import sqlite3
from yatk import ir
from yatk import ml
from yatk.ml.svm import SVM
from yatk.ml.nb import NaiveBayes

con = sqlite3.connect('test.db')
con.row_factory = sqlite3.Row
cur = con.cursor()

docs = []
cur.execute('select class, text from docs')
for row in cur.fetchall():
	docs.append((row['class'], row['text']))

con.close()

docs_even = []
N = int(len(docs) / 2)
for i in range(N):
	docs_even.append(docs[i])
	docs_even.append(docs[N + i])

def	test(classifier, features, weight):
	p = []
	for fold in range(1, 6):
		train_docs, test_docs = ml.folds(docs_even, 5, fold)

		index = ir.SentimentIndex(weight, features)
		index.get_class = lambda x: x[0]
		index.get_text = lambda x: x[1]
		index.build(train_docs)

		train_x = []
		train_y = []
		for doc in train_docs:
			train_x.append(index.weight(index.features(doc)))
			train_y.append(doc[0])

		test_x = []
		test_y = []
		for doc in test_docs:
			test_x.append(index.weight(index.features(doc)))
			test_y.append(doc[0])


		cl = classifier()
		cl.train(train_x, train_y)
		labels = cl.predict(test_x)
		mic, mac = cl.evaluate(test_y, labels)
		p.append(mic)

	print('{0} {1} {2}: {3:.1f}%'.format(classifier, features, weight, ir.avg(p) * 100))

test(NaiveBayes, 'unigram', 'bin')
test(NaiveBayes, 'bigram', 'bin')
test(NaiveBayes, 'bogram', 'bin')
test(SVM, 'unigram', 'bin')
test(SVM, 'bigram', 'bin')
test(SVM, 'bogram', 'bin')
test(SVM, 'unigram', 'delta')
test(SVM, 'bigram', 'delta')
test(SVM, 'bogram', 'delta')