#!/usr/bin/env python3
'''
Created on Aug 5, 2011

@author: alexpak <irokez@gmail.com>
'''

import sys
import re

if len(sys.argv) < 2:
	print('Usage: convert-rnc.py inputfile > outputfile')
	exit()
	
skip_lines = [
	'<\?xml version="1.0" encoding="windows-1251"\?><html><head>',
	'</head>',
	'<body>'
]
re_skip = re.compile('|'.join(skip_lines))
re_del = re.compile('<p[^>]+>|</td><td>|</td></tr><tr><td>')
re_fix1 = re.compile('</se>\s?<se>')
re_fix2 = re.compile('<se><se>')
	
print('<?xml version="1.0" encoding="utf-8" ?>')
print('<corpus>')
f = open(sys.argv[1], 'rb')
for line in f:
	line = line.decode('cp1251')

	if re_skip.search(line):
		continue
	
	line = re_del.sub('', line)
	line = re_fix1.sub('</se>', line)
	line = re_fix2.sub('<se>', line)
	
	print(line, end = '')
f.close()
print('</corpus>')