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

def recvall(the_socket,timeout=''):
	#setup to use non-blocking sockets
	#if no data arrives it assumes transaction is done
	#recv() returns a string
	the_socket.setblocking(0)
	total_data=[];data=''
	begin=time.time()
	if not timeout:
		timeout=1
	while 1:
		#if you got some data, then break after wait sec
		if total_data and time.time()-begin>timeout:
			break
		#if you got no data at all, wait a little longer
		elif time.time()-begin>timeout*2:
			break
		wait = 0
		try:
			data=the_socket.recv(4096)
			if data:
				total_data.append(data)
				begin = time.time()
				data = ''
				wait = 0
			else:
				time.sleep(0.1)
		except:
			pass
		#When a recv returns 0 bytes, other side has closed
	result = ''.join((data.decode('utf-8') for data in total_data))
	return result

import morph
import re

Tagger = morph.Tagger()
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 5000))

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
	'S': 'существительное',
	'A': 'прилагательное',
	'V': 'глагол',
	'ADV': 'наречие',
	'NID': 'инстранное',
	'NUM': 'числительное',
	'PR': 'предлог',
	'PART': 'частица',
	'CONJ': 'союз',
	'COM': 'коммуникативное',
	'INTJ': 'междометие',
	'P': 'P',
	'UNK': 'неизвестное',
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
	'gen2': 'второй род. падеж',
	'loc': 'локац. падеж',
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
		
		sentence = [[w] for w in re.split('\W+', text) if len(w)] if len(text) else []
		
		if len(sentence):
			labeled = Tagger.label(sentence)
			for w in range(0, len(sentence)):
				sentence[w] = (sentence[w][0], labeled[w][1], labeled[w][2])
				
			selected_feat = {'m', 'f', 'n', 'sg', 'pl', '1p', '2p', '3p', 'nom', 'gen', 'gen2', 'dat', 'acc', 'ins', 'prep', 'loc', 'real', 'imp', 'pass', 'comp', 'shrt'}		
			
			parser_input = []
			for word in sentence:
				w = word[0] or 'FANTOM'
				p = '.'.join([word[1]] + sorted(word[2] & selected_feat))
				parser_input.append('{0}\t{1}\n'.format(w, p))
	
			for word in parser_input:
				client_socket.send(bytes(word, 'utf-8'))
			
			client_socket.send(bytes('\n', 'utf-8'))
			data = recvall(client_socket).strip()
			#data = ''.join(parser_input).strip()
				
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
