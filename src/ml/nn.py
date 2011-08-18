'''
Created on Aug 18, 2011

@author: alexpak
'''

import ml
import math
import random
from collections import defaultdict

random.seed()

class Perceptron(ml.Classifier):
	def __init__(self, Nh):
		self.Nh = Nh
		
		self._labels = ml.Autoincrement()
		self._features = ml.Autoincrement()
		
	def _init(self, Ni, Nh, No):
		self.momentum = 0.9
		self.learn_rate = 0.5
		
		self._Wh = [[self._seed() for _ in range(0, Ni)] for __ in range(0, Nh)]
		self._Wo = [[self._seed() for _ in range(0, Nh)] for __ in range(0, No)]
		
		self._dWh = [[0] * Ni] * Nh
		self._dWo = [[0] * Nh] * No

	def get_class_id(self, C):
		if C not in self._class_ids:
			self._class_ids[C] = len(self._class_ids)
		
	def _seed(self):
		return (random.random() - 0.5)
		
	def _sigmod(self, x):
		return x
		return 1 / (1 + math.exp(-x))
	
	def _calc_layer(self, input, W):
		output = []
		for i in range(0, len(W)):
			s = 0
			for j in range(0, len(W[i])):
				s += W[i][j] * input[j]
			output.append(self._sigmod(s))
			
		return output

	def _propagate(self, input):
		self._pi = input
		self._ph = self._calc_layer(self._pi, self._Wh)
		self._po = self._calc_layer(self._ph, self._Wo)
		return self._po
	
	def _backpropagate(self, output):
		# delta's for output layer 
		do = []
		for i in range(0, len(self._Wo)):
			print(output[i], self._po[i])
			do.append(self._po[i] * (1 - self._po[i]) * (output[i] - self._po[i]))
#		print(do)
			
		# correct output layer weights
		for i in range(0, len(self._Wo)):
			for j in range(0, len(self._Wo[i])):
				self._dWo[i][j] = self.momentum * self._dWo[i][j] + (1 - self.momentum) * self.learn_rate * do[i] * self._ph[j]
				self._Wo[i][j] += self._dWo[i][j]
				
		# delta's for hidden layer
		dh = []
		for i in range(0, len(self._Wh)):
			d = 0
			for j in range(0, len(self._Wo)):
				d += do[j] * self._Wo[j][i]
			d *= self._ph[i] * (1 - self._ph[i])
			dh.append(d)
#		print(dh)
			
		# correct hidden layer weights
		for i in range(0, len(self._Wh)):
			for j in range(0, len(self._Wh[i])):
				self._dWh[i][j] = self.momentum * self._dWh[i][j] + (1 - self.momentum) * self.learn_rate * dh[i] * self._pi[j]
				self._Wh[i][j] += self._dWh[i][j]

		print(self._Wo)
		print(self._Wh)
		print()
	
	def train(self, x, y):
		labels = [self._labels.setId(C) for C in y]
		data = []
		for sample in x:
			data.append(defaultdict(float, [(self._features.setId(d), sample[d]) for d in sample]))
			
		self._init(self._features.count(), self.Nh, self._labels.count())

		epsilon = 1e-3
		for epoch in range(1, 10):
			i = 0
			error = 0
			for sample in data:
				output = self._propagate(sample)
				target = defaultdict(float)
				target[labels[i] - 1] = 1
				self._backpropagate(target)
				for j in range(0, len(output)):
					error += (output[j] - target[j]) ** 2
					
				i += 1
			
			print(error)
			print()
			if error < epsilon:
				break
			
	def predict(self, x):
		y = []
		for sample in x:
			output = self._propagate(defaultdict(float, [(self._features.getId(d), sample[d]) for d in sample]))
			which_max = max(range(0, len(output)), key = lambda i: output[i])
			y.append(self._labels.getVal(which_max + 1))
			
		return y