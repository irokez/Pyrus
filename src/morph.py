#!/usr/bin/env python3
'''
Created on Nov 21, 2011

@author: alexpak
'''

import sys
import ml
import ml.nb
from collections import Counter

class Guesser:
	def __init__(self, cond, category, anticond = set()):
		self.cond = cond if type(cond) == set else {cond}
		self.anticond = anticond if type(anticond) == set else {anticond}
		self.category = category
		
		self._svm = ml.nb.NaiveBayes()
	
	def train(self, sentences):
		train_x = []
		train_y = []
		for sentence in sentences:
			for word in sentence:
				try:
					form = word[0]
					lemma = word[1]['LEMMA']
					info = word[1]['FEAT']
				except:
#					print(word, file = sys.stderr)
					continue
				
				categories = set(info.split(' '))
				if not self.cond & categories or self.anticond & categories:
					continue
				
				train_x.append(self.gen_features(form))
				train_y.append(int(self.category in categories))
				
#		print(train_x[0:10])
#		print(train_y[0:10])
#		print(Counter(train_y))
		self._svm.train(train_x, train_y)
	
	def test(self, sentences):
		test_x = []
		test_y = []
		for sentence in sentences:
			for word in sentence:
				try:
					form = word[0]
					lemma = word[1]['LEMMA']
					info = word[1]['FEAT']
				except:
#					print(word, file = sys.stderr)
					continue
				
				categories = set(info.split(' '))
				if not self.cond & categories or self.anticond & categories:
					continue
				
				test_x.append(self.gen_features(form))
				test_y.append(int(self.category in categories))
				
		estim_y = self._svm.predict(test_x)
#		print(Counter(test_y))
#		print(Counter(estim_y))
		return self._svm.evaluate(test_y, estim_y)
	
	def predict(self, word):
		return self._svm.predict([self.gen_features(word)])
	
	def gen_features(self, word):
		x = {}
		
#		x['p3:' + word[0:3]] = 1
#		x['p4:' + word[0:4]] = 1
		x['p2:' + word[0:2]] = 1
		x['p3:' + word[0:3]] = 1
#		x['p6:' + word[0:6]] = 1
#		x['s1:' + word[-1:]] = 1
		x['s2:' + word[-2:]] = 1
		x['s3:' + word[-3:]] = 1
		x['s4:' + word[-4:]] = 1
		x['s5:' + word[-5:]] = 1
		x['w:' + word] = 1
		
		return x
	
	def save(self, path):
		self._svm.save(path)
		
	@staticmethod
	def load(path, cond, category):
		obj = Guesser(cond, category)
		obj._svm = ml.Classifier.load(path)
		return obj
	
if __name__ == '__main__':
	import glob
	from optparse import OptionParser
	import syntagrus
	
	parser = OptionParser()
	parser.usage = '%prog [options]'
	
	(options, args) = parser.parse_args()
	
#	cats = [
#		('S', 'МУЖ', 's-mas'),
#		('S', 'ЖЕН', 's-fem'),
#		('S', 'СРЕД', 's-neu'),
#		('S', 'МН', 's-pl'),
#		('S', 'ЕД', 's-sg'),
#		('S', 'ИМ', 's-nom'),
#		('S', 'РОД', 's-gen'),
#		('S', 'ДАТ', 's-dat'),
#		('S', 'ВИН', 's-acc'),
#		('S', 'ТВОР', 's-ins'),
#		('S', 'ПР', 's-prep'),
#		('S', 'ОД', 's-anim'),
#		('S', 'НЕОД', 's-inan')
#	]
	
	cats = [
		('V', '1-Л', 'v-1p', {'ПРИЧ', 'ДЕЕПР'}),
		('V', '2-Л', 'v-2p', {'ПРИЧ', 'ДЕЕПР'}),
		('V', '3-Л', 'v-3p', {'ПРИЧ', 'ДЕЕПР'}),
		('V', 'МН', 'v-pl', {'ПРИЧ', 'ДЕЕПР'}),
		('V', 'ЕД', 'v-sg', {'ПРИЧ', 'ДЕЕПР'}),
		('V', 'МУЖ', 'v-mas', {'ПРИЧ', 'ДЕЕПР'}),
		('V', 'ЖЕН', 'v-fem', {'ПРИЧ', 'ДЕЕПР'}),
		('V', 'СРЕД', 'v-neu', {'ПРИЧ', 'ДЕЕПР'}),
		('V', 'ПРОШ', 'v-past', {'ПРИЧ', 'ДЕЕПР'}),
		('V', 'НЕПРОШ', 'v-notpast', {'ПРИЧ', 'ДЕЕПР'})
	]

	if not len(args):
		files = glob.glob('res/*/*/*.tgt')
		corpus = []
		for file in files:
			R = syntagrus.Reader()
			sentences = R.read(file)
			corpus.extend(sentences)
			
		train_set = corpus[0:-round(len(corpus) / 10)]
		test_set = corpus[-round(len(corpus) / 10):]
			
		perf = 0
		for cat in cats:
			G = Guesser(cat[0], cat[1])
			G.train(train_set)
			results = G.test(test_set)
			G.save('tmp/' + cat[2])
			del(G)
			print('{0} acc = {1:.3f}%'.format(cat[1], results[0] * 100))
			perf += results[0]
			
		print('Total: {0:.3f}%'.format(perf * 100 / len(cats)))
		
	else:
		print(args[0])
		for cat in cats:
			G = Guesser.load('tmp/' + cat[2], cat[0], cat[1])
			print('{0}: {1}'.format(cat[1], G.predict(args[0])))