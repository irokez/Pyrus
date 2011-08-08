#!/usr/bin/env python3
'''
Created on Aug 3, 2011

@author: alexpak <irokez@gmail.com>
'''
import sys
import re

import rnc
import pos

sentences = []
#sentences.extend(rnc.Reader().read('tmp/fiction.xml'))
#sentences.extend(rnc.Reader().read('tmp/science.xml'))
#sentences.extend(rnc.Reader().read('tmp/laws.xml'))
sentences.extend(rnc.Reader().read('tmp/media1.xml'))
sentences.extend(rnc.Reader().read('tmp/media2.xml'))
sentences.extend(rnc.Reader().read('tmp/media3.xml'))

re_pos = re.compile('([\w-]+)(?:[^\w-]|$)'.format('|'.join(pos.tagset)))

tagger = pos.Tagger()

sentence_labels = []
sentence_words = []
for sentence in sentences:
	labels = []
	words = []
	for word in sentence:
		gr = word[1]['gr']
		m = re_pos.match(gr)
		if not m:
			print(gr, file = sys.stderr)
			
		pos = m.group(1)
		if pos == 'ANUM':
			pos = 'A-NUM'
			
		label = tagger.get_label_id(pos)
		if not label:
			print(gr, file = sys.stderr)
			
		labels.append(label)
		
		body = word[0].replace('`', '')
		words.append(body)
		
	sentence_labels.append(labels)
	sentence_words.append(words)
			
tagger.train(sentence_words, sentence_labels, True)
tagger.train(sentence_words, sentence_labels)
tagger.save('tmp/svm.model', 'tmp/ids.pickle')