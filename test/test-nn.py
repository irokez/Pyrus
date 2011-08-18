#!/usr/bin/env python3
'''
Created on Aug 18, 2011

@author: alexpak
'''
import sys
sys.path.append('src')

def list_to_dict(l):
	return dict(zip(range(0, len(l)), l))

from ml.nn import Perceptron

classifier = Perceptron(2)
x = [
	list_to_dict([0, 0]),
	list_to_dict([0, 1]),
	list_to_dict([1, 0]),
	list_to_dict([1, 1])
]
y = [0, 1, 1, 0]
#y = [1]

classifier.train(x, y)
y = classifier.predict(x)
print(y)