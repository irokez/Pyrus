'''
Created on Aug 18, 2011

@author: alexpak
'''
import sys
sys.path.append('/home/alexpak/tools/liblinear-1.8/python/')

import liblinearutil as liblinear
from .. import ml
import pickle

class SVM(ml.Classifier):
	def __init__(self):
		self._labels = ml.Autoincrement()
		self._features = ml.Autoincrement()
		
	def save(self, path):
		liblinear.save_model(path + '-model', self._model)
		del(self._model)
		ml.Classifier.save(self, path)
		
	@staticmethod
	def load(path):
		obj = ml.Classifier.load(path)
		obj._model = liblinear.load_model(path + '-model')
		return obj
	
	def train(self, x, y, biased = False):
		data = []
		for sample in x:
			data.append(dict([(self._features.setId(d), sample[d]) for d in sample]))
			
		labels = [self._labels.setId(C) for C in y]
		if self._labels.count() == 2:
			labels = [1 if label == 1 else -1 for label in labels]
			param = liblinear.parameter('-c 1 -s 2 -q' + (' -B {0}'.format(biased) if biased else ''))
		else:
			param = liblinear.parameter('-c 1 -s 4 -q' + (' -B {0}'.format(biased) if biased else ''))
		prob = liblinear.problem(labels, data)
		self._model = liblinear.train(prob, param)

	def predict(self, x):
		y = []
		for sample in x:
			data = dict([(self._features.getId(d), sample[d]) for d in sample if self._features.getId(d)])
			label, _, _ = liblinear.predict([0], [data], self._model, '')
			if self._labels.count() == 2:
				label[0] = 1 if label[0] == 1 else 2
			y.append(self._labels.getVal(label[0]))
			
		return y