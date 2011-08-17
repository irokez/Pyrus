#!/usr/bin/env python3
'''
Created on Aug 17, 2011

@author: alexpak
'''

import sys
sys.path.append('src')

f = open('res/iris.data')
data = []; x = []; y =[]
for line in f:
	rows = line.strip().split(',')
	if len(rows) == 5:
		x.append([float(i) for i in rows[0:4]])
		y.append(rows[4])
f.close()

def list_to_dict(l):
#	return dict(zip(l, [1 for _ in range(0, len(l))]))
	return dict(zip(range(0, len(l)), l))

# divide into training and test sets
test_x = []; test_y = []; train_x = []; train_y = [];
for i in range(0, len(x)):
	if i % 3:
		train_x.append(list_to_dict(x[i]))
		train_y.append(y[i])
	else:
		test_x.append(list_to_dict(x[i]))
		test_y.append(y[i])
	
from ml.nb import NaiveBayes

classifier = NaiveBayes()
classifier.train(train_x, train_y)
estim_y = classifier.predict(test_x)
(acc, ) = classifier.evaluate(test_y, estim_y)

print('Naive Bayes accuracy = {0:.2f}%'.format(acc * 100))

from ml.svm import SVM

classifier = SVM()
classifier.train(train_x, train_y)
estim_y = classifier.predict(test_x)
(acc, ) = classifier.evaluate(test_y, estim_y)

print('SVM accuracy = {0:.2f}%'.format(acc * 100))