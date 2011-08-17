'''
Created on Aug 18, 2011

@author: alexpak
'''

import config
import liblinearutil as liblinear
import ml
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
	
	def get_class_id(self, C):
		if C not in self._class_ids:
			self._class_ids[C] = len(self._class_ids)
		
	def train(self, x, y):
		labels = [self._labels.setId(C) for C in y]
		data = []
		for sample in x:
			data.append(dict([(self._features.setId(d), sample[d]) for d in sample]))
		
		param = liblinear.parameter('-c 1 -s 4 -q')
		prob = liblinear.problem(labels, data)
		self._model = liblinear.train(prob, param)

	def predict(self, x):
		y = []
		for sample in x:
			data = dict([(self._features.getId(d), sample[d]) for d in sample if self._features.getId(d)])
			label, _, _ = liblinear.predict([0], [data], self._model, '')
			y.append(self._labels.getVal(label[0]))
			
		return y