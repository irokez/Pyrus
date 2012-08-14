#!/usr/bin/env python3

import sys
import requests
import json
from yatk import ir
from yatk.ml.svm import SVM as Classifier
# from yatk.ml.nb import NaiveBayes as Classifier
from red import pie

if len(sys.argv) < 2:
	print('Enter query')
	exit()

TTL = 60

r = pie.Redis()
q = sys.argv[1]
cached = r.get(q)

if not cached:
	url = 'http://search.twitter.com/search.json'
	req = requests.get(url, params={'q': sys.argv[1]})
	data = json.loads(req.text)

	if 'results' not in data:
		print('Error')
		print(data)
		exit()

	cached = json.dumps(data['results'])
	r.setex(q, TTL, cached)

results = json.loads(cached)

cl = Classifier.load('test.svm')
index = ir.SentimentIndex.load('test.index', 'delta', 'bogram')
index.get_text = lambda x: x['text']

docs = []

for msg in results:
	feats = index.weight(index.features(msg))
	docs.append(feats)

labels = cl.predict(docs)
for n in range(len(results)):
	print('{0}.\t{1}\t{2}'.format(n + 1, labels[n], results[n]['text']))