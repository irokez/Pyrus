class Classifier:
	def train(self, x, y):
		pass
	
	def predict(self, x):
		pass
	
	def evaluate(self, gold, test):
		tp = 0; fp = 0
		
		for i in range(0, len(gold)):
			if test[i] == gold[i]:
				tp += 1
			else:
				fp += 1
		
		acc = tp / (tp + fp) if tp + fp else 0
		
		return (acc, )
	
class Autoincrement:
	def __init__(self):
		self._ids = {}
		self._inv = {}
		
	def setId(self, val):
		if val not in self._ids:
			self._ids[val] = len(self._ids) + 1
			self._inv[self._ids[val]] = val
			
		return self._ids[val]
	
	def getId(self, val):
		return self._ids[val] if val in self._ids else 0
	
	def getVal(self, id):
		return self._inv[id] if id in self._inv else None
	
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