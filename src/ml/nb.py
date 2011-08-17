'''
Created on Aug 17, 2011

@author: alexpak
'''

import math
import ml
from collections import defaultdict

class NaiveBayes(ml.Classifier):
	def __init__(self):
		pass
	
	def _gaus(self, i, mean, var):
		return 1 / math.sqrt(2 * math.pi * var) * math.exp(- (i - mean) ** 2 / (2 * var))
	
	def train1(self, x, y):
		P = {}
		
		data = {}
		labels = set()
		i = 0
		for C in y:
			labels.add(C)
			if C not in data:
				data[C] = []
			data[C].append(x[i])
			i += 1
		
		for C in data:
			P[C] = {}
			ndim = len(x[0]) # number of features
			for dim in range(0, ndim):
				mean = 0; var = 0; N = 0
				
				# calculate mean and length
				for sample in data[C]:
					mean += sample[dim]
					N += 1
				mean /= N
				
				# calculate variance
				for sample in data[C]:
					var += (mean - sample[dim]) ** 2
				var /= (N - 1)
				
				P[C][dim] = (mean, var)
				
		self._P = P
		
	def train(self, x, y):
		data = defaultdict(list)
		labels = set()
		discrete_features = set()
		numeric_features = set()
		i = 0
		for C in y:
			labels.add(C)
			data[C].append(x[i])
			for dim in x[i]:
				if isinstance(x[i][dim], float): 
					numeric_features.add(dim)
				else:
					discrete_features.add(dim)
			i += 1
		
		ndim = len(discrete_features)

		# train discrete features
		P = {}
		for C in data:
			count = defaultdict(int)
			total = 0
			for sample in data[C]:
				for dim, val in sample.items():
					if dim in discrete_features:
						count[dim] += val
						total += val
			
			P[C] = {}
			for dim in discrete_features:
				P[C][dim] = (1 + count[dim]) / (ndim + total)
		self._P = P
				
		# train numeric features
		F = {}
		for C in data:
			F[C] = {}
			for dim in numeric_features:
				mean = 0; var = 0; N = 0
				
				# calculate mean and length
				for sample in data[C]:
					mean += sample[dim]
					N += 1
				mean /= N
				
				# calculate variance
				for sample in data[C]:
					var += (mean - sample[dim]) ** 2
				var /= (N - 1)
				
				F[C][dim] = (mean, var)
								
		self._F = F
	
	def prob(self, C, dim, val):
		p = 0
		if dim in self._P[C]:
			p = self._P[C][dim]
		elif dim in self._F[C]:
			p = self._gaus(val, self._F[C][dim][0], self._F[C][dim][1])
			
		return p
	
	def predict(self, x):
		y = []
		for sample in x:
			L = defaultdict(float)
			for C in self._P:
				for dim in sample:
					L[C] += math.log(self.prob(C, dim, sample[dim]) or 1)
					
#			y.append(max(L.keys(), key = lambda i: L[i]) if len(L) else next(iter(self._P)))
			y.append(max(L.keys(), key = lambda i: L[i]) if len(L) else None)
			
		return y
	
	def test1(self, x):
		y = []
		for sample in x:
			L = {}
			for C in self._P:
				L[C] = 0
				for dim in range(0, len(sample)):
					P = self._P[C][dim]
					L[C] += math.log(self._gaus(sample[dim], P[0], P[1]))

			y.append(max(L.keys(), key = lambda i: L[i]) if len(L) else next(iter(self._P)))
			
		return y
	
