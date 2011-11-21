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
		
		self._cl = ml.nb.NaiveBayes()
	
	def train(self, sentences):
		train_x = []
		train_y = []
		for sentence in sentences:
			for w in range(0, len(sentence)):
				word = sentence[w]
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
				
				feats = self.gen_features(sentence, w)
				train_x.append(feats)
				train_y.append(int(self.category in categories))
				
		self._cl.train(train_x, train_y)
	
	def predict(self, sentences, return_likelihood = False):
		test_x = []
		test_y = []
		for sentence in sentences:
			for w in range(0, len(sentence)):
				word = sentence[w]
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
				
				test_x.append(self.gen_features(sentence, w))
				test_y.append(int(self.category in categories))
				
		return (self._cl.predict(test_x, return_likelihood), test_y)
	
	def test(self, sentences):
		(estim_y, test_y) = self.predict(sentences)
		return self._cl.evaluate(test_y, estim_y)
	
	def guess(self, word):
		return self._cl.predict([self.gen_features(word)])
	
	def gen_features(self, sentence, w):
		word = sentence[w][0]
		
		x = {}
		
		x['p3:' + word[0:3]] = 1
		x['p4:' + word[0:4]] = 1
		x['p5:' + word[0:5]] = 1
		x['p6:' + word[0:6]] = 1
#		x['s1:' + word[-1:]] = 1
		x['s2:' + word[-2:]] = 1
		x['s3:' + word[-3:]] = 1
		x['s4:' + word[-4:]] = 1
		x['s5:' + word[-5:]] = 1
		x['w:' + word] = 1
		
		for i in range(1, 4):
			if w > i - 1:
				word = sentence[w - i][0]
#				x[str(i) + 'p3:' + prev[0:3]] = 1
#				x[str(i) + 'p4:' + prev[0:4]] = 1
#				x[str(i) + 'p5:' + prev[0:5]] = 1
#				x[str(i) + 'p6:' + prev[0:6]] = 1
		#		x['s1:' + word[-1:]] = 1
				x[str(i) + 's2:' + word[-2:]] = 1
				x[str(i) + 's3:' + word[-3:]] = 1
				x[str(i) + 's4:' + word[-4:]] = 1
#				x[str(i) + 's5:' + prev[-5:]] = 1
				x[str(i) + 'w:' + word] = 1
				
		for i in range(1, 2):
			if w + i < len(sentence) - 1:
				word = sentence[w + i][0]
#				x[str(i) + 'p3:' + prev[0:3]] = 1
#				x[str(i) + 'p4:' + prev[0:4]] = 1
#				x[str(i) + 'p5:' + prev[0:5]] = 1
#				x[str(i) + 'p6:' + prev[0:6]] = 1
		#		x['s1:' + word[-1:]] = 1
				x[str(i) + '+s2:' + word[-2:]] = 1
				x[str(i) + '+s3:' + word[-3:]] = 1
				x[str(i) + '+s4:' + word[-4:]] = 1
#				x[str(i) + 's5:' + prev[-5:]] = 1
				x[str(i) + '+w:' + word] = 1
		
		return x
	
	def save(self, path):
		self._cl.save(path)
		
	@staticmethod
	def load(path, cond, category):
		obj = Guesser(cond, category)
		obj._cl = ml.Classifier.load(path)
		return obj
	
class GuesserGroup:
	def __init__(self, cond, categories, anticond = set()):
		self.cond = cond if type(cond) == set else {cond}
		self.anticond = anticond if type(anticond) == set else {anticond}
		self._guessers = []
		self._categories = categories
		for category in categories:
			self._guessers.append(Guesser(cond, category, anticond))
			
	def train(self, sentences):
		for guesser in self._guessers:
			guesser.train(sentences)
	
	def test(self, sentences):
		test_y = []
		scores = []
		
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
				
				intersect = set(self._categories) & categories
				test_y.append(intersect.pop() if len(intersect) == 1 else None)

		
		for guesser in self._guessers:
			(estim_y, _) = guesser.predict(sentences, True)
			scores.append(estim_y)
			
		estim_y = []
		for i in range(0, len(test_y)):
			p = []
			for j in range(0, len(scores)):
				L = scores[j][i]
				p.append(L[1])
				
			m = max(range(0, len(p)), key = lambda i: p[i])
			estim_y.append(self._categories[m])
			
		print(test_y[0:10])
		print(estim_y[0:10])
		return self._guessers[0]._cl.evaluate(test_y, estim_y)
	
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
		
#		Gr = GuesserGroup('S', ['ОД', 'НЕОД'])
#		Gr = GuesserGroup('S', ['МН', 'ЕД'])
#		Gr = GuesserGroup('S', ['МУЖ', 'ЖЕН', 'СРЕД'])
		Gr = GuesserGroup({'ИМ', 'РОД', 'ДАТ', 'ВИН', 'ТВОР', 'ПР'}, ['ИМ', 'РОД', 'ДАТ', 'ВИН', 'ТВОР', 'ПР'])
#		Gr = GuesserGroup({'ПРОШ', 'НЕПРОШ'}, ['ПРОШ', 'НЕПРОШ'], {'ПРИЧ', 'ДЕЕПР'})
		Gr.train(train_set)
		results = Gr.test(test_set)
		print(results)
#		print('Acc = {0:.3f}%'.format(results[0] * 100))
		exit()
			
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
			print('{0}: {1}'.format(cat[1], G.guess(args[0])))