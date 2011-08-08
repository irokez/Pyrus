'''
Created on Aug 4, 2011

@author: alexpak <irokez@gmail.com>
'''
import config
import liblinearutil as svm

tagset = ['S', 'A', 'NUM', 'A-NUM', 'V', 'ADV', 'PRAEDIC', 'PARENTH', 'S-PRO', 'A-PRO', 'ADV-PRO', 'PRAEDIC-PRO', 'PR', 'CONJ', 'PART', 'INTJ', 'INIT', 'NONLEX']
tag_id = {}
tag_inv = {}
for i in range(0, len(tagset)):
	tag_id[tagset[i]] = i + 1
	tag_inv[i + 1] = tagset[i]

class Tagger:
	def __init__(self):
		self.chain_len = 3
		self._features = TaggerFeatures()
		pass
	
	def load(self, modelname, featuresname):
		self._svm_model = svm.load_model(modelname)
		self._features.load(open(featuresname, 'rb'))
		
	def save(self, modelname, featuresname):
		svm.save_model(modelname, self._svm_model)
		self._features.save(open(featuresname, 'wb'))
		
	def get_label_id(self, pos):
		return tag_id[pos] if pos in tag_id else 0
	
	def get_label(self, id):
		return tag_inv[id] if id in tag_inv else '?'
		
	def train(self, sentences, labels, cross_validation = False):
		x = []
		y = []
		
		for i in range(0, len(sentences)):
			sentence = sentences[i]
			prev = []
			
			j = 0
			for word in sentence:
				body = word.lower()
				
				featurespace = self._construct_featurespace(body, prev)
				
				prev.append((body, labels[i][j]))
				if len(prev) > self.chain_len:
					del(prev[0])
					
				x.append(featurespace.featureset)
				j += 1

			y.extend(labels[i])

		prob = svm.problem(y, x)
		
		if cross_validation:
			param = svm.parameter('-c 1 -v 4 -s 4')
			svm.train(prob, param)
		else:
			param = svm.parameter('-c 1 -s 4')
			self._svm_model = svm.train(prob, param)
	
	def label(self, sentence):
		labeled = []
		prev = []
		for word in sentence:
			body = word.lower()
			
			featurespace = self._construct_featurespace(body, prev)
			
			p_label, _, _ = svm.predict([0], [featurespace.featureset], self._svm_model, '')
			label = p_label[0]
			
			prev.append((body, label))
			if len(prev) > self.chain_len:
				del(prev[0])
				
			labeled.append((word, label))
			
		return labeled
				
	def _construct_featurespace(self, word, prev):
		featurespace = ml.FeatureSpace()
			
		featurespace.add({1: len(word)}, 10)
		featurespace.add(self._features.from_suffix(word))
		featurespace.add(self._features.from_prefix(word))
		featurespace.add(self._features.from_body(word))
		
		for item in prev:
			featurespace.add({1: item[1]}, 100)
#			featurespace.add(features.from_suffix(item[0]))
#			featurespace.add(features.from_prefix(item[0]))
#			featurespace.add(features.from_body(item[0]))
	
		return featurespace
	
				
import pickle
import ml
class TaggerFeatures:
	def __init__(self):
		self._body_id = {}
		self._suffix_id = {}
		self._prefix_id = {}
		
		self._train = True
		self._featurespace = ml.FeatureSpace()
		
	def load(self, fp):
		(self._body_id, self._suffix_id, self._prefix_id) = pickle.load(fp)
		self._train = False
		
	def save(self, fp):
		pickle.dump((self._body_id, self._suffix_id, self._prefix_id), fp)

	def from_body(self, body):
		featureset = {}
		if self._train:
			if body not in self._body_id:
				self._body_id[body] = len(self._body_id) + 1
					
			featureset[self._body_id[body]] = 1
		else:
			if body in self._body_id:
				featureset[self._body_id[body]] = 1
				
		return featureset
	
	def from_suffix(self, body):
		featureset = {}
		
		suffix2 = body[-2:]
		if suffix2 not in self._suffix_id:
			self._suffix_id[suffix2] = len(self._suffix_id) + 1
		featureset[self._suffix_id[suffix2]] = 1
		
		suffix3 = body[-3:]
		if suffix3 not in self._suffix_id:
			self._suffix_id[suffix3] = len(self._suffix_id) + 1
		featureset[self._suffix_id[suffix3]] = 1
		
		return featureset
	
	def from_prefix(self, body):
		featureset = {}
		
		prefix2 = body[:2]
		if prefix2 not in self._prefix_id:
			self._prefix_id[prefix2] = len(self._prefix_id) + 1
		featureset[self._prefix_id[prefix2]] = 1
		
		prefix3 = body[:3]
		if prefix3 not in self._prefix_id:
			self._prefix_id[prefix3] = len(self._prefix_id) + 1
		featureset[self._prefix_id[prefix3]] = 1
		
		return featureset