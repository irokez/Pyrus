#!/usr/bin/env python3
'''
Created on Aug 17, 2011

@author: alexpak
'''
import sys
sys.path.append('src')

f = open('res/names.txt')

x = []; y = []

for line in f:
	(name, sex) = line.strip().split(' ')
	x.append({name[-1:]: 1, name[-2:]: 1, name[-3:]: 1, name[-4:]: 1})
	y.append(sex)
	
fold = -100

f.close()

import os

from ml.nb import NaiveBayes

filename = 'tmp/nb.pickle'
exists = os.path.isfile(filename)
if exists:
	classifier = NaiveBayes.load(filename)
else:
	classifier = NaiveBayes()
	
classifier.train(x[0:fold], y[0:fold])
estim_y = classifier.predict(x[fold:])
(acc, ) = classifier.evaluate(y[fold:], estim_y)

if not exists:
	classifier.save(filename)

print('Naive Bayes accuracy = {0:.2f}%'.format(acc * 100))

from ml.svm import SVM

filename = 'tmp/svm.pickle'
exists = os.path.isfile(filename)
if exists:
	classifier = SVM.load(filename)
else:
	classifier = SVM()
	
classifier.train(x[0:fold], y[0:fold])
estim_y = classifier.predict(x[fold:])
(acc, ) = classifier.evaluate(y[fold:], estim_y)

if not exists:
	classifier.save(filename)
	
print('SVM accuracy = {0:.2f}%'.format(acc * 100))