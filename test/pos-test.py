#!/usr/bin/env python3
'''
Created on Aug 3, 2011

@author: alexpak <irokez@gmail.com>
'''
import sys
import pos

sentence = sys.argv[1].split(' ')

tagger = pos.Tagger()
tagger.load('tmp/svm.model', 'tmp/ids.pickle')

rus = {
	'S': 'сущ.', 
	'A': 'прил.', 
	'NUM': 'числ.', 
	'A-NUM': 'числ.-прил.', 
	'V': 'глаг.', 
	'ADV': 'нареч.', 
	'PRAEDIC': 'предикатив', 
	'PARENTH': 'вводное', 
	'S-PRO': 'местоим. сущ.', 
	'A-PRO': 'местоим. прил.', 
	'ADV-PRO': 'местоим. нареч.', 
	'PRAEDIC-PRO': 'местоим. предик.', 
	'PR': 'предлог', 
	'CONJ': 'союз', 
	'PART': 'частица', 
	'INTJ': 'межд.', 
	'INIT': 'инит', 
	'NONLEX': 'нонлекс'
}

tagged = []
for word, label in tagger.label(sentence):
	tagged.append((word, rus[tagger.get_label(label)]))
	
print(tagged)