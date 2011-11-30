#!/usr/bin/env python3
'''
Created on Nov 29, 2011

@author: alexpak
'''

if __name__ == '__main__':
	import glob
	from optparse import OptionParser
	import syntagrus
	import sys
	
	parser = OptionParser()
	parser.usage = '%prog [options]'
	parser.add_option('-t', '--train', action='store_const', const=True, dest='train', help='generate train file')
	parser.add_option('-T', '--test', action='store_const', const=True, dest='test', help='generate test file')
	parser.add_option('-n', '--number', action='store', dest='number', type='int', help='number of files to process')
	parser.add_option('-f', '--format', action='store', dest='format', type='string', help='output format')

	(options, args) = parser.parse_args()

	if not options.train and not options.test:
		print('Specify --train or --test', file=sys.stderr)
		exit()

	if not options.number:
		print('Specify number of files -n', file=sys.stderr)
		exit()

	if not len(args):
		files = glob.glob('res/*/*/*.tgt')
		corpus = []
		for file in files[0:options.number]:
			R = syntagrus.Reader()
			sentences = R.read(file)
			corpus.extend(sentences)
			del(R)

		fold_size = round(len(corpus) / 10)
		
		train_set = corpus[0:-fold_size]
		test_set = corpus[-fold_size:]
		
		print('{0} sentences'.format(len(corpus)), file=sys.stderr)
		
		del(corpus)
		
		a_set = test_set if options.test else train_set
		
		if options.format == 'malt':
			# Malt TAB format
			for sentence in a_set:
				for word in sentence:
					w = word[0] or 'FANTOM'
					p = '.'.join([word[1].pos] + sorted(word[1].feat))
					l = word[1].link if word[1].dom else 'ROOT'
					d = str(word[1].dom)
					print('\t'.join([w, p, d, l]))
				print('')
					
		else:
			# MSTParser format
			for sentence in a_set:
				wn = []
				pn = []
				ln = []
				dn = []
				for word in sentence:
					wn.append(word[0] or 'FANTOM')
					pn.append('-'.join([word[1].pos] + sorted(word[1].feat)))
					ln.append(word[1].link if word[1].dom else 'ROOT')
					dn.append(str(word[1].dom))
					
				print('\t'.join(wn))
				print('\t'.join(pn))
				print('\t'.join(ln))
				print('\t'.join(dn))
				print('')
