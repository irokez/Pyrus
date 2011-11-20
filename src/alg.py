'''
Created on Aug 19, 2011

@author: alexpak
'''

class Vector:
	def __init__(self, iterable):
		self.setData(iterable)
		
	def setData(self, iterable):
		self._data = list(iterable)

	def __getitem__(self, i):
		return self._data[i]
	
	def __len__(self):
		return len(self._data)
		
	def __add__(self, term):
		data = self._data[:]
		if type(term) in (int, float):
			for i in range(0, len(data)):
				data[i] += term
		elif isinstance(term, Vector):
			for i in range(0, len(self._data)):
				data[i] += term[i]
				
		return Vector(data)
	
	def __sub__(self, term):
		data = self._data[:]
		if type(term) in (int, float):
			for i in range(0, len(data)):
				data[i] -= term
		elif isinstance(term, Vector):
			for i in range(0, len(self._data)):
				data[i] -= term[i]
				
		return Vector(data)
	
	def __iadd__(self, term):
		self.setData(self.__add__(term)) 
		return self
	
	def __repr__(self):
		return '[{0}]'.format(', '.join([str(i) for i in self._data]))
			

class Matrix:
	def __init__(self):
		self._data = None
		
	def __radd__(self, term):
		pass