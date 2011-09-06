#!/usr/bin/env python3

'''
Created on Sep 6, 2011

@author: alexpak
'''
import sys
sys.path.append('src')

import parsers
from parsers.cyk import CYK

rules = '''
    EX  = "(" EX ")" | N
    EX  = EX OP2 EX | OP1 EX
    N   = "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "0"
    OP2 = "+" | "-" | "/" | "*"
    OP1 = "+" | "-"
'''

grammar = parsers.read_rules(rules)

parser = CYK(grammar)
#parser.parse('1 + 2 * ( 3 - 6 )')
