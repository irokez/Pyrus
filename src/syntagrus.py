#!/usr/bin/env python3
'''
Created on Nov 21, 2011

@author: alexpak
'''
import os
import sqlite3
import xml.parsers.expat
import glob
from optparse import OptionParser
from collections import namedtuple

word_t = namedtuple('word_t', ['lemma', 'pos', 'feat', 'id', 'dom', 'link'])
feat_ru_en = {
	'ЕД': 'sg',
	'МН': 'pl',
	'ЖЕН': 'f',
	'МУЖ': 'm',
	'СРЕД': 'n',
	'ИМ': 'nom',
	'РОД': 'gen',
	'ДАТ': 'dat',
	'ВИН': 'acc',
	'ТВОР': 'ins',
	'ПР': 'prep',
	'ПАРТ': 'gen2',
	'МЕСТН': 'loc',
	'ОД': 'anim',
	'НЕОД': 'inan',
	'ИНФ': 'inf',
	'ПРИЧ': 'adjp',
	'ДЕЕПР': 'advp',
	'ПРОШ': 'pst',
	'НЕПРОШ': 'npst',
	'НАСТ': 'prs',
	'1-Л': '1p',
	'2-Л': '2p',
	'3-Л': '3p',
	'ИЗЪЯВ': 'real',
	'ПОВ': 'imp',
	'КР': 'shrt',
	'НЕСОВ': 'imperf',
	'СОВ': 'perf',
	'СТРАД': 'pass',
	'СЛ': 'compl',
	'СМЯГ': 'soft',
	'СРАВ': 'comp',
	'ПРЕВ': 'supl',
}

link_ru_en = {
	'предик': 'subj',
	'1-компл': 'obj',
	'2-компл': 'obj',
	'3-компл': 'obj',
	'4-компл': 'obj',
	'5-компл': 'obj',
	'опред': 'amod',
	'предл': 'prep',
	'обст': 'pobj',
}
{
	'огранич': '',      
	'квазиагент': '',       
	'сочин': '',      
	'соч-союзн': '',      
	'атриб': '',      
	'аппоз': '',      
	'подч-союзн': '',      
	'вводн': '',      
	'сент-соч': '',      
	'количест': '',      
	'разъяснит': '',       
	'присвяз': '',      
	'релят': '',      
	'сравн-союзн': '',      
	'примыкат': '',      
	'сравнит': '',      
	'соотнос': '',      
	'эксплет': '',      
	'аналит': '',      
	'пасс-анал': '',      
	'вспом': '',      
	'агент': '',      
	'кратн': '',      
	'инф-союзн': '',      
	'электив': '',      
	'композ': '',      
	'колич-огран': '',      
	'неакт-компл': '',      
	'пролепт': '',       
	'суб-копр': '',       
	'дат-субъект': '',      
	'длительн': '',      
	'об-аппоз': '',      
	'изъясн': '',      
	'компл-аппоз': '',      
	'оп-опред': '',      
	'1-несобст-компл': '',      
	'распред': '',      
	'уточн': '',      
	'нум-аппоз': '',      
	'ном-аппоз': '',      
	'2-несобст-компл': '',      
	'аппрокс-колич': '',      
	'колич-вспом': '',      
	'колич-копред': '',      
	'кратно-длительн': '',      
	'об-копр': '',      
	'эллипт': '',      
	'3-несобст-компл': '',       
	'4-несобст-компл': '',       
	'fictit': '',       
	'авт-аппоз': '',       
	'аддит': '',       
	'адр-присв': '',       
	'дистанц': '',       
	'несобст-агент': '',       
	'об-обст': '',       
	'обст-тавт': '',       
	'презентат': '',       
	'сент-предик': '',       
	'суб-обст': '',       
}

class Reader:
	def __init__(self):
		self._parser = xml.parsers.expat.ParserCreate()
		self._parser.StartElementHandler = self.start_element
		self._parser.EndElementHandler = self.end_element
		self._parser.CharacterDataHandler = self.char_data		
	
	def start_element(self, name, attr):
		if name == 'W':
			features = attr['FEAT'].split(' ') if 'FEAT' in attr else ['UNK']
			for i in range(0, len(features)):
				if features[i] in feat_ru_en:
					features[i] = feat_ru_en[features[i]]
					
			lemma = lemma=attr['LEMMA'].lower() if 'LEMMA' in attr else ''
			link = attr['LINK'] if 'LINK' in attr else None
#			if link in link_ru_en:
#				link = link_ru_en[link]
				
			dom = int(attr['DOM']) if attr['DOM'] != '_root' else 0
			pos = features[0]
			feat = set(features[1:])
			
			if 'adjp' in feat:
				pos = 'VADJ'
				feat -= {'adjp'}
				
			if 'advp' in feat:
				pos = 'VADV'
				feat -= {'advp'}
			
			if 'inf' in feat:
				pos = 'VINF'
				feat -= {'inf'}
			
			self._info = word_t(lemma=lemma, pos=pos, feat=feat, id=int(attr['ID']), dom=dom, link=link)
			self._cdata = ''
	
	def end_element(self, name):
		if name == 'S':
			self._sentences.append(self._sentence)
			self._sentence = []
		elif name == 'W':
			self._sentence.append((self._cdata, self._info))
			self._cdata = ''
	
	def char_data(self, content):
		self._cdata += content
		
	def read(self, filename):
		f = open(filename, encoding='windows-1251')
		content = f.read()
		f.close()
		content = content.replace('encoding="windows-1251"', 'encoding="utf-8"')
		
		self._sentences = []
		self._sentence = []
		self._cdata = ''
		self._info = ''
		
		self._parser.Parse(content)		
		
		return self._sentences

class Lexicon:
	def __init__(self, dbname):
		self.dbname = dbname
		db_exists = os.path.isfile(dbname)
		self.con = sqlite3.connect(dbname)
		self.cur = self.con.cursor()
		
		if not db_exists:
			self.create_db()		
	
	def create_db(self):
		sql = '''
        create table words(
        	id integer primary key autoincrement,
        	lemma text,
        	pos text,
        	form text,
        	info text,
        	freq integer
        );
        create index words_lemma_form_info on words(lemma, form, info);
        '''
		[self.cur.execute(st) for st in sql.split(';') if len(st.strip())]
		
	def index(self, filename):
		sentences = Reader().read(filename)
		for sentence in sentences:
			for word in sentence:
				feat = ' '.join(word[1].feat)
				self.cur.execute('select id from words where lemma = ? and form = ? and pos = ? and info = ?', (word[1].lemma, word[0], word[1].pos, feat))
				row = self.cur.fetchone()
				if row is None:
					self.cur.execute('insert into words (lemma, pos, form, info, freq) values (?, ?, ?, ?, 1)', (word[1].lemma, word[1].pos, word[0], feat))
				else:
					self.cur.execute('update words set freq = freq + 1 where id = ?', row)
					
	def close(self):
		self.con.commit()
		self.con.close()
	
if __name__ == '__main__':
	parser = OptionParser()
	parser.usage = '%prog [options] inputfile'
	parser.add_option('-L', '--construct-lexicon', action = 'store_const', const = True	, dest = 'lexicon', help = 'construct lexicon')

	(options, args) = parser.parse_args()
	
	if options.lexicon:
		L = Lexicon('tmp/lexicon')
		files = glob.glob('res/*/*/*.tgt')
		for file in files:
			L.index(file)
		
		L.close()

	#R = Reader()
	#sentences = R.read(args[0])
	#print(len(sentences))
	#print(sentences[0])
	