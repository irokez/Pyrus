#!/usr/bin/env python3
'''
Created on Aug 17, 2011

@author: alexpak
'''
import sys
sys.path.append('src')

from collections import defaultdict

f_pos = open('res/rt-polaritydata/rt-polaritydata/rt-polarity.pos', 'rb')
f_neg = open('res/rt-polaritydata/rt-polaritydata/rt-polarity.neg', 'rb')

def count_words(line):
	count = defaultdict(bool)
	for word in line.strip().split(' '):
		if len(word) > 1:
			count[word] += 1

	return count

x = []; y = []

i = 0
eof = False
while not eof:
	line = f_pos.readline()
	eof = not len(line)
	x.append(count_words(line.decode('utf-8', 'ignore')))
	y.append(+1)
	x.append(count_words(f_neg.readline().decode('utf-8', 'ignore')))
	y.append(-1)
	i += 1
	
fold = int(i * 0.9)

f_pos.close()
f_neg.close()

from ml.nb import NaiveBayes

classifier = NaiveBayes()
classifier.train(x[0:fold], y[0:fold])
estim_y = classifier.predict(x[fold:])
(acc, ) = classifier.evaluate(y[fold:], estim_y)

print('Naive Bayes accuracy = {0:.2f}%'.format(acc * 100))

from ml.svm import SVM

classifier = SVM()
classifier.train(x[0:fold], y[0:fold])
estim_y = classifier.predict(x[fold:])
(acc, ) = classifier.evaluate(y[fold:], estim_y)

print('SVM accuracy = {0:.2f}%'.format(acc * 100))