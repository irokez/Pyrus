'''
Created on Aug 4, 2011

@author: alexpak <irokez@gmail.com>
'''

class FeatureSpace:
	
	def __init__(self):
		self.featureset = {}
		self.start = 0
		self.default_size = int(1e5)
		
	def add(self, featureset, size = None):
		if size is None:
			size = self.default_size
			
		for (feature, value) in featureset.items():
			self.featureset[feature + self.start] = value
		
		self.start += size