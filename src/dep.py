#!/usr/bin/env python3
'''
Created on Nov 22, 2011

@author: alexpak
'''

import sys
import ml
import math
from ml.svm import SVM as Classifier
#from ml.nb import NaiveBayes as Classifier
from collections import Counter, OrderedDict
import sqlite3
import os
import syntagrus

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
#					y.append(word_from[1].link if word_from[1].dom == word_to[1].id else 'none')
					y.append(int(word_from[1].dom == word_to[1].id))
					
			#endfor w
		#endfor sentence
		return (x, y)
	
	def train(self, sentences):
		x, y = self.traverse(sentences)
		self._cl.train_regression(x, y)

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
	
def print_table(data, outfile = sys.stdout, maxlen = {}):
	vsep = '|'
	endl = '\n'
	s = ''
	
	keys = []
	maxkey = 0
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

	s += endl + hline + endl
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
		s += vsep.join([str(row[key] if key in row else '').rjust(maxlen[key]) for key in keys])
		s += vsep
		s += endl + hline + endl
			
	print(s, file=outfile)
	return maxlen
	
class Parser:
	def __init__(self, linker):
		self._linker = linker
		
	def parse(self, sentence):
		table_estim = OrderedDict()
		table_true = OrderedDict()
		rowwords = set()
		
		con = sqlite3.connect('tmp/links')
		cur = con.cursor()
		
		prep = False
		for w in range(0, len(sentence)):
			source = sentence[w]
			source_word = source[0]
			
			if source_word in rowwords:
				source_word += '-' + str(source[1].id)
			else:
				rowwords.add(source_word)
				
			table_estim[source_word] = OrderedDict()
			table_true[source_word] = OrderedDict()
			
			source_feat = ' '.join([source[1].pos] + sorted(source[1].feat))
			
			# root
			target_word = '_root'
			if source[1].pos == 'PR':
				prep = True
				cur.execute('select sum(freq) from links where ffeat = ? and fword = ? and root', (source_feat, source_word))
			else:
				cur.execute('select sum(freq) from links where ffeat = ? and root', (source_feat, ))
				
			table_estim[source_word][target_word] = cur.fetchone()[0] or 0
			table_true[source_word][target_word] = 'root' if source[1].dom == 0 else ''
			
			colwords = set()
			no = False
			for v in range(0, len(sentence)):
				target = sentence[v]
				target_word = target[0]
				if target_word in colwords:
					target_word += '-' + str(target[1].id)
				else:
					colwords.add(target_word)
					
				target_feat = ' '.join([target[1].pos] + sorted(target[1].feat))
				if target[1].pos == 'CONJ' or (target[1].pos == 'PR' and source[1].pos in {'S', 'ADV', 'ADJ'}):
					cur.execute('select sum(freq) from links where ffeat = ? and tfeat = ? and tword = ?', (source_feat, target_feat, target_word))
				elif source[1].pos == 'CONJ' or (source[1].pos == 'PR' and target[1].pos in {'S', 'ADV', 'ADJ'}):
					cur.execute('select sum(freq) from links where ffeat = ? and fword = ? and tfeat = ?', (source_feat, source_word, target_feat))
				else:
					cur.execute('select sum(freq) from links where ffeat = ? and tfeat = ?', (source_feat, target_feat))
#				table_estim[word_from][word_to] = '.' if v == w else round((cur.fetchone()[0] or 0) / (math.log(abs(v - w) + 2)))
				freq = cur.fetchone()[0] or 0
					
				if source[1].pos == 'S' and target[1].pos == 'PR' and w > v and prep:
					freq = 9999
					prep = False

				if source_word == 'не' and w < v and not no:
					freq = 9999
					no = True

				table_estim[source_word][target_word] = '.' if v == w else freq
				table_true[source_word][target_word] = '.' if v == w else source[1].link if source[1].dom == target[1].id else ''
#				table_estim[word_from][word_to] = '.' if v == w else 'x' if estim_y[i] else ''
#				table_true[word_from][word_to] = '.' if v == w else 'x' if test_y[i] else ''

		maxlen = print_table(table_true)
		print_table(table_estim, maxlen = maxlen)
#		'''
		for rowkey, row in table_estim.items():
			maxval = max([int(val) if val != '.' else 0 for val in list(row.values())[1:]])
			for key, val in row.items():
				if key == '_root':
					continue
				if val == '.':
					continue
				if val < maxval:
					table_estim[rowkey][key] = ''
#		'''	
		print_table(table_estim, maxlen = maxlen)
		
	def parse0(self, sentence):
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
#				table_estim[word_from][word_to] = '.' if v == w else round(estim_y[i], 5) if estim_y[i] != 'none' else ''
#				table_true[word_from][word_to] = '.' if v == w else test_y[i] if test_y[i] != 'none' else ''
				table_estim[word_from][word_to] = '.' if v == w else estim_y[i] if estim_y[i] else ''
				table_true[word_from][word_to] = '.' if v == w else 'x' if test_y[i] else ''
				i += v != w
				
		maxlen = print_table(table_true)
		print_table(table_estim, maxlen = maxlen)
		
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

class Links:
	def __init__(self, dbname):
		self.dbname = dbname
		db_exists = os.path.isfile(dbname)
		self.con = sqlite3.connect(dbname)
		self.cur = self.con.cursor()
		
		if not db_exists:
			self.create_db()		
	
	def create_db(self):
		sql = '''
        create table links(
        	id integer primary key autoincrement,
        	name text,

			fword text,
			ffeat text,
        	fpos text,
			fnum text,
        	fgen text,
			fcase text,
			fpers text,
        	fanim text,
        	ftype text,
        	fmood text,
        	ftens text,
        	fdegr text,

			tword text,
			tfeat text,
			tpos text,
			tnum text,
			tgen text,
			tcase text,
			tpers text,
			tanim text,
			ttype text,
			tmood text,
			ttens text,
			tdegr text,

			root integer,
        	freq integer,
        	dist integer
        );
        create index links_info on links(name, fword, tword, root, ffeat, tfeat, dist);
        create index links_info2 on links(ffeat, tfeat);
        create index links_info3 on links(ffeat, root);
        create index links_info4 on links(ffeat, fword, root);
        create index links_info5 on links(ffeat, fword, tfeat);
        create index links_info6 on links(ffeat, tfeat, tword);
        '''
        
		sql0 = '''
        create table links(
        	id integer primary key autoincrement,
        	name text,

			fword text,
			ffeat text,

			tword text,
			tfeat text,

			root integer,
        	freq integer
        );
        create index links_info on links(name, fword, tword, root, ffeat, tfeat);
        '''
		[self.cur.execute(st) for st in sql.split(';') if len(st.strip())]
		
	def index(self, sentences):
		for sentence in sentences:
			for word_from in sentence:
				is_root = 0
				if word_from[1].dom:
					word_to = sentence[word_from[1].dom - 1]
				else:
					word_to = ('', syntagrus.word_t(lemma='', pos='', dom='', link='root', id=0, feat=set()))
					is_root = 1
				from_feat = ' '.join([word_from[1].pos] + sorted(word_from[1].feat))
				to_feat = ' '.join([word_to[1].pos] + sorted(word_to[1].feat))
			
				fpos = word_from[1].pos
				fnum = (number & word_from[1].feat or {None}).pop()
				fgen = (genders & word_from[1].feat or {None}).pop()
				fcase = (cases & word_from[1].feat or {None}).pop()
				fpers = (person & word_from[1].feat or {None}).pop()
				fanim = (animacy & word_from[1].feat or {None}).pop()
				ftype = (vtypes & word_from[1].feat or {None}).pop()
				fmood = (vmood & word_from[1].feat or {None}).pop()
				ftens = (tenses & word_from[1].feat or {None}).pop()
				fdegr = (degree & word_from[1].feat or {None}).pop()
				
				tpos = word_to[1].pos
				tnum = (number & word_to[1].feat or {None}).pop()
				tgen = (genders & word_to[1].feat or {None}).pop()
				tcase = (cases & word_to[1].feat or {None}).pop()
				tpers = (person & word_to[1].feat or {None}).pop()
				tanim = (animacy & word_to[1].feat or {None}).pop()
				ttype = (vtypes & word_to[1].feat or {None}).pop()
				tmood = (vmood & word_to[1].feat or {None}).pop()
				ttens = (tenses & word_to[1].feat or {None}).pop()
				tdegr = (degree & word_to[1].feat or {None}).pop()
				
				dist = word_to[1].id - word_from[1].id
				
				self.cur.execute('select id from links where name = ? and fword = ? and tword = ? and root = ? and ffeat = ? and tfeat = ? and dist = ?', (word_from[1].link, word_from[0].lower(), word_to[0].lower(), is_root, from_feat, to_feat, dist))
				row = self.cur.fetchone()
				if row is None:
					sql = '''
					insert into links (name, fword, tword, root, ffeat, tfeat, freq, dist,
					fpos, fnum, fgen, fcase, fpers, fanim, ftype, fmood, ftens, fdegr, 
					tpos, tnum, tgen, tcase, tpers, tanim, ttype, tmood, ttens, tdegr
					) values (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
					'''
					self.cur.execute(sql, (word_from[1].link, word_from[0].lower(), word_to[0].lower(), is_root, from_feat, to_feat, dist, fpos, fnum, fgen, fcase, fpers, fanim, ftype, fmood, ftens, fdegr, tpos, tnum, tgen, tcase, tpers, tanim, ttype, tmood, ttens, tdegr))
				else:
					self.cur.execute('update links set freq = freq + 1 where id = ?', row)
					
	def close(self):
		self.con.commit()
		self.con.close()
		
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

		'''
				
		L = Links('tmp/links')
		L.index(train_set)
		L.close()
		exit()
		'''
		
		'''
		
		L = Linker()
		L.train(train_set)	
#		results = L.test(test_set)
#		print('Accuracy = {0[0]:.3f}, precision = {0[1]:.3f}, recall = {0[2]:.3f}, F1 = {0[3]:.3f}'.format(results))
		'''
		L = None

		P = Parser(L)
		example = test_set[6] #6
		for word in example:
			print(word)
		P.parse(example)
