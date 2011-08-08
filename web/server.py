#!/usr/bin/env python3
'''
Created on Aug 7, 2011

@author: alexpak
'''

import cherrypy
import sys
import time

sys.path.append('src')

f = open('web/html/tagging.html')
content = f.read()
f.close()

import pos
import re
import template
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

class HelloWorld:
	@cherrypy.expose
	def index(self, text = ''):

		start = time.time()
		
		sentence = re.split('\W+', text)
		
		tagged = []
		for word, label in tagger.label(sentence):
			tagged.append((word, rus[tagger.get_label(label)]))
		
		time_total = time.time() - start
		words = len(sentence)
		words_per_sec = words / time_total

		T = template.Template()
		T.text = text
		T.tagged = tagged
		T.time_total = round(time_total, 2)
		T.words_per_sec = round(words_per_sec)
		T.words = words
		
		return T.transform(content)
	
	@cherrypy.expose
	def test(self):
		return 'test'

cherrypy.quickstart(HelloWorld())