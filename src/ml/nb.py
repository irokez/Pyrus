'''
Created on Aug 17, 2011

@author: alexpak
'''

import math
from collections import defaultdict
from .. import ml

class NaiveBayes(ml.Classifier):
	def __init__(self):
		pass
	
	def __repr__(self):
		return 'NaiveBayes'
	
	def _gaus(self, i, mean, var):
		return (1 / math.sqrt(2 * math.pi * var) * math.exp(- (i - mean) ** 2 / (2 * var))) if var > 0 else float(1 if i == mean else 0)
			

	def _prob(self, C, dim, val):
		p = 0
		if dim in self._P[C]:
			p = self._P[C][dim]
		elif dim in self._F[C]:
			p = self._gaus(val, self._F[C][dim][0], self._F[C][dim][1])
			
		return p
	
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
			n = 0
			for dim in numeric_features:
				n += 1
				mean = 0; var = 0; N = 0
				
				# calculate mean and length
				for sample in data[C]:
					mean += sample[dim] if dim in sample else 0
					N += 1
				mean /= N
				
				# calculate variance
				for sample in data[C]:
					var += (mean - (sample[dim] if dim in sample else 0)) ** 2
				var /= (N - 1) if N > 1 else N
				
				F[C][dim] = (mean, var)
								
		self._F = F
	
	def predict(self, x, return_likelihood = False):
		y = []
		for sample in x:
			L = defaultdict(float)
			for C in self._P:
				for dim in sample:
					L[C] += math.log(self._prob(C, dim, sample[dim]) or 1)
					
#			y.append(max(L.keys(), key = lambda i: L[i]) if len(L) else next(iter(self._P)))
			if return_likelihood:
				y.append(L)
			else:
				y.append(max(L.keys(), key = lambda i: L[i]) if len(L) else None)
			
		return y
	
