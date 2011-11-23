#!/usr/bin/env python3
'''
Created on Nov 22, 2011

@author: alexpak
'''

import sys
import ml
#from ml.svm import SVM as Classifier
from ml.nb import NaiveBayes as Classifier
from collections import Counter, OrderedDict

features = {'m', 'f', 'n', 'nom', 'gen', 'gen2', 'dat', 'acc', 'ins', 'prep', 'loc', 'sg', 'pl', 'real', 'inf', 'advp', 'adjp', 'imp', 'pass', '1p', '2p', '3p'}

class Linker:
	def __init__(self):
		self._cl = Classifier()
	
	def traverse(self, sentences):
		x = []
		y = []
		for sentence in sentences:
			for w in range(0, len(sentence)):
				word_from = sentence[w]
				feats = {}

#				meta1 = word_from[1].pos + '_'.join(sorted(word_from[1].feat & features))
#				feats['f:' + meta1] = 1
				
				for feat in word_from[1].feat & features:
					feats['f:' + feat] = 1
				feats['fp:' + word_from[1].pos] = 1
				feats['fw:' + word_from[0]] = 1
				
				for v in range(0, len(sentence)):
					if v == w:
						continue
					
					word_to = sentence[v]
						
					feats2 = feats.copy()
#					meta2 = word_to[1].pos + '_'.join(sorted(word_to[1].feat & features))
#					feats['t:' + meta2] = 1
					
					for feat in word_to[1].feat & features:
						feats2['t:' + feat] = 1
					for feat in word_from[1].feat & word_to[1].feat:
						feats2['c:' + feat] = 1
					feats2['tp:' + word_to[1].pos] = 1
					feats2['tw:' + word_to[0]] = 1
					feats2['dst'] = float(w - v)
					
					'''
					for i in range(1, 3):
						u = v - i
						if u > 0 or u != w:
							continue
						word_prev = sentence[u]
						for feat in word_prev[1].feat:
							feats2[str(i) + 'p:' + feat] = 1
#						for feat in word_from[1].feat & word_prev[1].feat:
#							feats2[str(i) + 'pfc:' + feat] = 1
#						for feat in word_to[1].feat & word_prev[1].feat:
#							feats2[str(i) + 'ptc:' + feat] = 1
						feats2[str(i) + 'pp:' + word_prev[1].pos] = 1
						#feats2[str(i) + 'pw:' + word_prev[0]] = 1
					'''
						
					
#					if word_from[1].dom != word_to[1].id:
#						continue
					
					x.append(feats2)
					y.append(word_from[1].link if word_from[1].dom == word_to[1].id else 'none')
#					y.append(int(word_from[1].dom == word_to[1].id))
					
			#endfor w
		#endfor sentence
		return (x, y)
	
	def train(self, sentences):
		x, y = self.traverse(sentences)
#		print(x[0:10])
#		print(y[0:10])
		self._cl.train(x, y)

	def predict(self, sentences):
		(test_x, test_y) = self.traverse(sentences)
		return (self._cl.predict(test_x), test_y)
	
	def evaluate_bin(self, gold, test):
		tp = 0; fp = 0; tn = 0; fn = 0
		
		for i in range(0, len(gold)):
			if gold[i] != 'none':
				if test[i] == gold[i]:
					tp += 1
				else:
					fn += 1
			else:
				if test[i] == gold[i]:
					tn += 1
				else:
					fp += 1
				
		
		acc = (tp + tn) / (tp + fp + tn + fn) if tp + fp + tn + fn else 0
		pr = tp / (tp + fp) if tp + fp else 0
		rec = tp / (tp + fn) if tp + fn else 0
		f1 = 2 * (pr * rec) / (pr + rec) if pr + rec else 0
		
		return (acc, pr, rec, f1)
	
	def evaluate_mul(self, gold, test):
		tp = 0; fp = 0; tn = 0; fn = 0; cl = 0
		
		for i in range(0, len(gold)):
			if gold[i] != 'none':
				if test[i] != 'none':
					tp += 1
				else:
					fn += 1
					
				if test[i] == gold[i]:
					cl += 1
					
			else:
				if test[i] == 'none':
					tn += 1
				else:
					fp += 1
		
		acc = cl / (tp + fn) if tp + fn else 0
		pr = tp / (tp + fp) if tp + fp else 0
		rec = tp / (tp + fn) if tp + fn else 0
		f1 = 2 * (pr * rec) / (pr + rec) if pr + rec else 0
		
		return (acc, pr, rec, f1)
	
	def test(self, sentences):
		(estim_y, test_y) = self.predict(sentences)
		print(Counter(test_y))
		print(Counter(estim_y))
		return self.evaluate_mul(test_y, estim_y)
	
	def save(self, path):
		self._cl.save(path)
		
	@staticmethod
	def load(path):
		obj = Linker()
		obj._cl = ml.Classifier.load(path)
		return obj
	
def print_table(data, outfile = sys.stdout):
	vsep = '|'
	endl = '\n'
	s = ''
	
	keys = []
	maxkey = 0
	maxlen = {}
	for rowkey, row in data.items():
		l = len(str(rowkey))
		if l > maxkey:
			maxkey = l
		for key in row:
			if key not in keys:
				keys.append(key)
			l = len(str(row[key]))
			if key not in maxlen or l > maxlen[key]:
				maxlen[key] = l
		
	for key in keys:
		l = len(str(key))
		if l > maxlen[key]:
			maxlen[key] = l
		if maxlen[key] < 3:
			maxlen[key] = 3
			
	hline = '+' + '-' * maxkey + '+' + '+'.join(['-' * maxlen[key] for key in keys]) + '+'

	s = endl + hline + endl
	s += vsep
	s += ' ' * maxkey
	s += vsep
	s += vsep.join([str(key).ljust(maxlen[key]) for key in keys])
	s += vsep
	s += endl + hline + endl
	
	for rowkey, row in data.items():
		s += vsep
		s += str(rowkey).ljust(maxkey)
		s += vsep
		s += vsep.join([str(row[key] if key in row else '').center(maxlen[key]) for key in keys])
		s += vsep
		s += endl + hline + endl
			
	print(s, file=outfile)
	
class Parser:
	def __init__(self, linker):
		self._linker = linker
		
	def parse(self, sentence):
		estim_y, test_y = self._linker.predict([sentence])
		i = 0
		table_estim = OrderedDict()
		table_true = OrderedDict()
		rowwords = set()
		for w in range(0, len(sentence)):
			word_from = sentence[w][0]
			if word_from in rowwords:
				word_from += '-' + str(sentence[w][1].id)
			else:
				rowwords.add(word_from)
				
			table_estim[word_from] = OrderedDict()
			table_true[word_from] = OrderedDict()
			colwords = set()
			for v in range(0, len(sentence)):
				word_to = sentence[v][0]
				if word_to in colwords:
					word_to += '-' + str(sentence[v][1].id)
				else:
					colwords.add(word_to)
				table_estim[word_from][word_to] = '.' if v == w else estim_y[i] if estim_y[i] != 'none' else ''
				table_true[word_from][word_to] = '.' if v == w else test_y[i] if test_y[i] != 'none' else ''
#				table_estim[word_from][word_to] = '.' if v == w else 'x' if estim_y[i] else ''
#				table_true[word_from][word_to] = '.' if v == w else 'x' if test_y[i] else ''
				i += v != w
				
		print_table(table_true)
		print_table(table_estim)
	
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
		for file in files[0:10]:
			R = syntagrus.Reader()
			sentences = R.read(file)
			corpus.extend(sentences)
			del(R)

		fold_size = round(len(corpus) / 10)
		
		train_set = corpus[0:-fold_size]
		test_set = corpus[-fold_size:]
		
		print('{0} sentences'.format(len(corpus)))
		
		del(corpus)
		
		L = Linker()
		L.train(train_set)	
		results = L.test(test_set)
		print('Accuracy = {0[0]:.3f}, precision = {0[1]:.3f}, recall = {0[2]:.3f}, F1 = {0[3]:.3f}'.format(results))

		P = Parser(L)
		example = test_set[6]
		for word in example:
			print(word)
		P.parse(example)
