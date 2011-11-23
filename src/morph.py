#!/usr/bin/env python3
'''
Created on Nov 21, 2011

@author: alexpak
'''

import ml
import ml.nb

class Guesser:
	def __init__(self):
		self._cl = ml.nb.NaiveBayes()
		
	def is_candidate(self, word):
		pass
		
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
	
	def predict(self, sentences, return_likelihood = False):
		(test_x, test_y) = self.traverse(sentences)
		return (self._cl.predict(test_x, return_likelihood), test_y)
	
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
		obj._cl = ml.Classifier.load(path)
		return obj
	
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
		
		def intersects_classes(classes):
			return lambda w: (w[1].feat & classes).pop()
		
		def intersects_classes_or_none(classes, none):
			return lambda w: (w[1].feat & classes or {none}).pop()
		
		def has_classes(pos, classes):
			return lambda w: w[1].pos == pos and w[1].feat & classes
		
		def pos_equals(pos):
			return lambda w: w[1].pos == 'V'
		
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
			
#			('s-gender', has_classes('S', genders), intersects_classes(genders)),
#			('s-case', has_classes('S', cases), intersects_classes(cases)),
#			('s-animacy', has_classes('S', animacy), intersects_classes(animacy)),
#			('s-number', has_classes('S', number), intersects_classes(number)),
#
#			('v-form', pos_equals('V'), intersects_classes_or_none(vform, 'pers')),
#			('v-person', has_classes('V', person), intersects_classes(person)),
#			('v-number', has_classes('V', number), intersects_classes(number)),
#			('v-gender', has_classes('V', genders), intersects_classes(genders)),
#			('v-type', has_classes('V', vtypes), intersects_classes(vtypes)),
#			('v-tense', has_classes('V', tenses), intersects_classes(tenses)),
#			('v-mood', has_classes('V', vmood), intersects_classes(vmood)),
#			
#			('a-gender', has_classes('A', genders), intersects_classes(genders)),
#			('a-case', has_classes('A', cases), intersects_classes(cases)),
#			('a-number', has_classes('A', number), intersects_classes(number)),
#			('a-degree', pos_equals('A'), intersects_classes_or_none(degree, 'ncomp')),
#			('a-short', pos_equals('A'), has_class('shrt')),
#
#			('adv-comp', pos_equals('ADV'), intersects_classes_or_none(degree, 'ncomp')),
#			
#			('num-gender', has_classes('NUM', genders), intersects_classes(genders)),
#			('num-case', has_classes('NUM', cases), intersects_classes(cases)),
#			('num-number', has_classes('NUM', number), intersects_classes(number)),
#			('num-degree', pos_equals('NUM'), intersects_classes_or_none(degree, 'ncomp')),
		]
		
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
		word = args[0]
		print(word)
		
		Tagger = Guesser.load('tmp/pos')
		pos = Tagger.guess(word)
		feat = []
		print(pos)
		if pos == 'S':
			for p in ['tmp/s-gender', 'tmp/s-number', 'tmp/s-case', 'tmp/s-animacy']:
				G = Guesser.load(p)
				feat.append(G.guess(word))
		elif pos == 'A':
			for p in ['tmp/a-gender', 'tmp/a-number', 'tmp/a-case', 'tmp/a-degree']:
				G = Guesser.load(p)
				feat.append(G.guess(word))
		elif pos == 'NUM':
			for p in ['tmp/num-gender', 'tmp/num-number', 'tmp/num-case', 'tmp/num-degree']:
				G = Guesser.load(p)
				feat.append(G.guess(word))
		elif pos == 'V':
			G = Guesser.load('tmp/v-form')
			form = G.guess(word)
			if form == 'pers' or form == 'adjp':
				for p in ['tmp/v-person', 'tmp/v-number', 'tmp/v-gender', 'tmp/v-tense', 'tmp/v-mood', 'tmp/v-type']:
					G = Guesser.load(p)
					feat.append(G.guess(word))
			else:
				feat.append(form)
		elif pos == 'ADV':
			for p in ['tmp/adv-comp']:
				G = Guesser.load(p)
				feat.append(G.guess(word))
			
		print(' '.join(feat))