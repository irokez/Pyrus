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
import requests
import json

path = os.path.dirname(os.path.abspath(__file__)) + '/'

f = open(path + 'demo.html', 'rb')
content = f.read().decode()
f.close()

from pyrus.src import template
from yatk import ir
from yatk.ml.svm import SVM as Classifier
from red import pie

TTL = 60

r = pie.Redis()
cl = Classifier.load('test.svm')
index = ir.SentimentIndex.load('test.index', 'delta', 'bogram')
index.get_text = lambda x: x['text']

class HelloWorld:
	@cherrypy.expose
	def index(self, q = ''):
		start = time.time()
		q = q.strip()
		error = ''

		T = template.Template()

		if len(q):
			cached = r.get(q)

			if not cached:
				url = 'http://search.twitter.com/search.json'
				req = requests.get(url, params={'q': q})
				data = json.loads(req.text)

				if 'results' not in data:
					print('Error')
					print(data)
					exit()

				cached = json.dumps(data['results'])
				r.setex(q, TTL, cached)

			results = json.loads(cached)

			docs = []

			for msg in results:
				feats = index.weight(index.features(msg))
				docs.append(feats)

			labels = cl.predict(docs)
			output = []
			for n in range(len(results)):
				output.append((labels[n], results[n]['text']))

			end = time.time()

			T.q = cgi.escape(q)
			T.output = output			
			T.time_total = round(end - start, 1)
			T.msgs = len(output)
			T.msgs_per_sec = round(len(output) / (end - start), 1)

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
