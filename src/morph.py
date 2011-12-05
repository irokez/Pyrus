#!/usr/bin/env python3
'''
Created on Nov 21, 2011

@author: alexpak
'''

import ml
#from ml.nb import NaiveBayes as Classifier
from ml.svm import SVM as Classifier
from collections import Counter

def intersects_classes(classes):
	return lambda w: (w[1].feat & classes).pop()

def intersects_classes_or_none(classes, none):
	return lambda w: (w[1].feat & classes or {none}).pop()

def has_classes(pos, classes):
	return lambda w: w[1].pos == pos and w[1].feat & classes

def pos_equals(pos):
	return lambda w: w[1].pos == pos

def has_class(a_class):
	return lambda w: int(a_class in w[1].feat)
	
pos = {'S', 'A', 'V', 'ADV', 'NID', 'NUM', 'PR', 'PART', 'CONJ', 'COM', 'INTJ', 'P', 'UNK'}

genders = {'m', 'f', 'n'}
cases = {'nom', 'gen', 'dat', 'acc', 'ins', 'prep', 'gen2', 'loc'}
animacy = {'anim', 'inan'}
number = {'sg', 'pl'}
person = {'1p', '2p', '3p'}
vtypes = {'perf', 'imperf'}
vmood = {'real', 'imp', 'pass'}
vform = {'inf', 'advj', 'advp'}
tenses = {'pst', 'npst', 'prs'}
degree = {'comp', 'supl'}

cats = [
	('pos', lambda w: True, lambda w: w[1].pos),
	
	('s-gender', has_classes('S', genders), intersects_classes(genders)),
	('s-case', has_classes('S', cases), intersects_classes(cases)),
	('s-animacy', has_classes('S', animacy), intersects_classes(animacy)),
	('s-number', has_classes('S', number), intersects_classes(number)),

	('v-form', pos_equals('V'), intersects_classes_or_none(vform, 'pers')),
	('v-person', has_classes('V', person), intersects_classes(person)),
	('v-number', has_classes('V', number), intersects_classes(number)),
	('v-gender', has_classes('V', genders), intersects_classes(genders)),
	('v-type', has_classes('V', vtypes), intersects_classes(vtypes)),
	('v-tense', has_classes('V', tenses), intersects_classes(tenses)),
	('v-mood', has_classes('V', vmood), intersects_classes(vmood)),

	('vadj-number', has_classes('VADJ', number), intersects_classes(number)),
	('vadj-gender', has_classes('VADJ', genders), intersects_classes(genders)),
	('vadj-type', has_classes('VADJ', vtypes), intersects_classes(vtypes)),
	('vadj-tense', has_classes('VADJ', tenses), intersects_classes(tenses)),
	('vadj-mood', has_classes('VADJ', vmood), intersects_classes(vmood)),
	('vadj-case', has_classes('VADJ', cases), intersects_classes(cases)),
	
	('a-gender', has_classes('A', genders), intersects_classes(genders)),
	('a-case', has_classes('A', cases), intersects_classes(cases)),
	('a-number', has_classes('A', number), intersects_classes(number)),
	('a-degree', pos_equals('A'), intersects_classes_or_none(degree, 'ncomp')),
	('a-short', pos_equals('A'), has_class('shrt')),
	('a-animacy', has_classes('A', animacy), intersects_classes(animacy)),

	('adv-comp', pos_equals('ADV'), intersects_classes_or_none(degree, 'ncomp')),
	
	('num-gender', has_classes('NUM', genders), intersects_classes(genders)),
	('num-case', has_classes('NUM', cases), intersects_classes(cases)),
	('num-number', has_classes('NUM', number), intersects_classes(number)),
	('num-degree', pos_equals('NUM'), intersects_classes_or_none(degree, 'ncomp')),
]

class Guesser:
	def __init__(self):
		self._cl = Classifier()
		
	def is_candidate(self, word):
		return True
		
	def make_class(self, word):
		pass
		
	def traverse(self, sentences):
		x = []
		y = []
		for sentence in sentences:
			for w in range(0, len(sentence)):
				word = sentence[w]
				
				if not self.is_candidate(word):
					continue
				
				x.append(self.gen_features(sentence, w))
				y.append(self.make_class(word))
				
		return (x, y)
	
	def train(self, sentences):
		(train_x, train_y) = self.traverse(sentences)
		self._cl.train(train_x, train_y)
	
	def predict(self, sentences):
		(test_x, test_y) = self.traverse(sentences)
		return (self._cl.predict(test_x), test_y)
	
	def test(self, sentences):
		(estim_y, test_y) = self.predict(sentences)
		return self._cl.evaluate(test_y, estim_y)
	
	def guess(self, word):
		return self._cl.predict([self.gen_features([(word,)], 0)])[0]
	
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
	def load(path):
		obj = Guesser()
		obj._cl = Classifier.load(path)
		return obj
	
class Tagger:
	def __init__(self):
		self._pos = Guesser.load('tmp/pos')
		self._guesser = {}
		for cat in cats:
			self._guesser[cat[0]] = Guesser.load('tmp/' + cat[0])
	
	def label(self, sentence):
		tagged = self._pos.predict([sentence])[0]
		feats = {}
		for cat, guesser in self._guesser.items():
			feats[cat] = guesser.predict([sentence])[0]
			
		labeled = []
		for w in range(0, len(sentence)):
			pos = tagged[w]
			feat = []
			cats = []
			if pos == 'S':
				cats = ['s-number', 's-case', 's-animacy']
				if True or feats['s-number'][w] == 'sg':
					feat.append(feats['s-gender'][w])
			elif pos == 'A':
				cats = ['a-number', 'a-degree']
				if feats['a-short'][w]:
					feat.append('shrt')
				else:
					feat.append(feats['a-case'][w])
				if feats['a-number'][w] == 'sg':
					feat.append(feats['a-gender'][w])
			elif pos == 'NUM':
				cats = ['num-gender', 'num-number', 'num-case', 'num-degree']
			elif pos == 'V':
				cats = ['v-number', 'v-tense', 'v-mood', 'v-type']
				if feats['v-tense'][w] == 'pst':
					if feats['v-number'][w] == 'sg':
						feat.append(feats['v-gender'][w])
				else:
					feat.append(feats['v-person'][w])
					
			elif pos == 'VINF':
				cats = ['v-type']
			elif pos == 'VADV':
				cats = ['v-type', 'v-tense']
			elif pos == 'VADJ':
				cats = ['vadj-number', 'vadj-gender', 'vadj-tense', 'vadj-type', 'vadj-mood']
				if feats['a-short'][w]:
					feat.append('shrt')
				else:
					feat.append(feats['vadj-case'][w])
					feat.append(feats['a-degree'][w])
				if feats['vadj-number'][w] == 'sg':
					feat.append(feats['vadj-gender'][w])
			elif pos == 'ADV':
				cats = ['adv-comp']
					
			for cat in cats:
				feat.append(feats[cat][w])
				
			featset = set(feat) - {'ncomp'}
				
			labeled.append((sentence[w][0], pos, featset))

		return labeled
	
if __name__ == '__main__':
	import glob
	from optparse import OptionParser
	import syntagrus
	
	parser = OptionParser()
	parser.usage = '%prog [options]'
	
	(options, args) = parser.parse_args()
	
	if not len(args):
		files = glob.glob('res/*/*/*.tgt')
		corpus = []
		for file in files:
			R = syntagrus.Reader()
			sentences = R.read(file)
			corpus.extend(sentences)
			del(R)
			
		print(len(corpus))
		
		fold_size = round(len(corpus) / 2)
		
		train_set = corpus[0:-fold_size]
		test_set = corpus[-fold_size:]
		del(corpus)
		
		for cat in cats:
			G = Guesser()
			G.is_candidate = cat[1]
			G.make_class = cat[2]
			G.train(train_set)
			results = G.test(test_set)
			G.save('tmp/' + cat[0])
			del(G)
			print('{0}\t\t{1:.3f}%'.format(cat[0], results[0] * 100))
		
	else:
		T = Tagger()
		print('Loaded')
		words = args[0].split(' ')
		sentence = []
		for word in words:
			sentence.append((word, tuple()))
			
		labeled = T.label(sentence)
		for word in labeled:
			print(word)
