#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Aug 7, 2011

@author: alexpak
'''

import cherrypy
import sys
import time
import cgi
import os

path = os.path.dirname(os.path.abspath(__file__)) + '/'

sys.path.append(path + '../src')

f = open(path + 'html/tagging.html')
content = f.read()
f.close()

import pos
import re
import template
tagger = pos.Tagger()
tagger.load(path + '../tmp/svm.model', path + '../tmp/ids.pickle')

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
		
		sentence = [word for word in re.split('\W+', text) if len(word.strip())]
		
		tagged = []
		for word, label in tagger.label(sentence):
			tagged.append((word, rus[tagger.get_label(label)]))
		
		time_total = time.time() - start
		words = len(sentence)
		words_per_sec = words / time_total

		T = template.Template()
		T.text = cgi.escape(text)
		T.tagged = tagged
		T.time_total = round(time_total, 2)
		T.words_per_sec = round(words_per_sec)
		T.words = words
		
		return T.transform(content)
	
	@cherrypy.expose
	def test(self):
		return content

cherrypy.server.socket_host = '0.0.0.0'
config = {
	'/': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': path + 'public/',
		'tools.encode.encoding': 'utf8'
	}
}

cherrypy.quickstart(HelloWorld(), config = config)
