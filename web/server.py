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

f = open(path + 'html/tagging.html', 'rb')
content = f.read().decode()
f.close()

import re
import template
import socket
import time

def recvall(sock):
	output = ''
	while True:
		data = sock.recv(4096)
		if not data:
			break
		output += data.decode('utf-8')
	return output

import morph
import re

Tagger = morph.Tagger()

def get_color(pos):
	if pos[0] == 'S':
		return 'blue'
	elif pos[0] == 'V':
		return 'green'
	elif pos[0] == 'A':
		return 'orange'
	else:
		return 'gray'

categories = {
	'S': 'сущ.',
	'A': 'прил.',
	'V': 'глагол',
	'VINF': 'инф.',
	'VADJ': 'прич.',
	'VADV': 'дееп.',
	'ADV': 'нар.',
	'NID': 'инoстр.',
	'NUM': 'числ.',
	'PR': 'предлог',
	'PART': 'част.',
	'CONJ': 'союз',
	'COM': 'ком.',
	'INTJ': 'межд.',
	'P': 'P',
	'UNK': '???',
	'm': 'муж. род',
	'f': 'жен. род',
	'n': 'ср. род',
	'sg': 'ед. число',
	'pl': 'мн. число',
	'nom': 'им. падеж',
	'gen': 'род. падеж',
	'dat': 'дат. падеж',
	'acc': 'вин. падеж',
	'ins': 'твор. падеж',
	'prep': 'пред. падеж',
	'gen2': '2й род. падеж',
	'loc': 'мест. падеж',
	'anim': 'одуш.',
	'inan': 'неодуш.',
	'1p': '1е лицо',
	'2p': '2е лицо',
	'3p': '3е лицо',
	'perf': 'соверш.',
	'imperf': 'несоверш.',
	'real': 'действ.',
	'imp': 'повелит.',
	'pass': 'страд.',
	'pst': 'прош. время',
	'npst': 'непрош. время',
	'prs': 'наст. время',
	'comp': 'сравн. степень',
	'supl': 'превосх. степень',
	'shrt': 'кратк.'
}
def pos_to_human(pos):
	loc = []
	for feat in pos.split('.'):
		if feat in categories:
			loc.append(categories[feat])
		else:
			loc.append(feat)

	return loc

class HelloWorld:
	@cherrypy.expose
	def index(self, text = ''):

		start = time.time()
		text = text.strip()
		T = template.Template()
		T.text = cgi.escape(text)
		error = ''
		
		sentence = [[w] for w in re.split('\W+', text) if len(w)] if len(text) else []
		
		if 0 < len(sentence) < 25:
				
			labeled = Tagger.label(sentence)
			for w in range(0, len(sentence)):
				sentence[w] = (sentence[w][0], labeled[w][1], labeled[w][2])
				
			selected_feat = {'m', 'f', 'n', 'sg', 'pl', '1p', '2p', '3p', 'nom', 'gen', 'gen2', 'dat', 'acc', 'ins', 'prep', 'loc', 'real', 'imp', 'pass', 'comp', 'shrt'}		
			
			parser_input = []
			for word in sentence:
				w = word[0] or 'FANTOM'
				p = '.'.join([word[1]] + sorted(word[2] & selected_feat))
				parser_input.append('{0}\t{1}\n'.format(w, p))

			client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client_socket.connect(("localhost", 5000))
			for word in parser_input:
				client_socket.send(bytes(word, 'utf-8'))
			
			client_socket.send(bytes('\n', 'utf-8'))
			data = recvall(client_socket).strip()
			client_socket.close()
				
			time_total = time.time() - start
			words = len(sentence)
			words_per_sec = words / time_total
			
			edges = []
			nodes = [(0, 'ROOT', 'red')]
			
			tagged = [tuple(row.split('\t')) for row in data.split('\n')]
			n = 0
			for word in tagged:
				n += 1
				if len(word) < 4:
					continue
				
				nodes.append((n, word[0], get_color(word[1])))
				
			n = 0
			for word in tagged:
				n += 1
				if len(word) < 4:
					continue
				head = int(word[2])
				if len(tagged) < head:
					head = 0
				
				try:
					edges.append((n, head, word[3]))
				finally:
					pass

			print(tagged, file=sys.stderr)
			T.tagged = [(word[0], ', '.join(pos_to_human(word[1]))) for word in tagged]
			T.edges = edges
			T.nodes = nodes
			T.time_total = round(time_total, 2)
			T.words_per_sec = round(words_per_sec)
			T.words = words
		elif len(sentence) > 25:
			error = 'Sentence is too long, looks like "War and Peace"'

		T.error = error
		
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
