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
    EX  = B1 EX B2 | N
    B1  = "("
    B2  = ")"
    EX  = EX OP2 EX | OP1 EX
    N   = "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "0"
    OP2 = "+" | "-" | "/" | "*"
    OP1 = "+" | "-"
'''

#rules = '''
#    EX  = EX OP EX | N
#    N   = "1" | "2" | "3"
#    OP = "+" | "-"
#'''

grammar = parsers.read_rules(rules)

parser = CYK(grammar)
#result = parser.parse('1 + 2 * ( 3 - 6 ) + 9 + 0 / 2')
result = parser.parse('1 + 2 + 3')
#parser.parse('1 + 2')
tree = parser.build_tree()
parser.print_tree(tree)

'''
(EX (EX 1)
    (OP +)
    (N 2))
'''