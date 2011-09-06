'''
Created on Sep 6, 2011

@author: alexpak
'''

from collections import defaultdict

class CYK:
    literals = set()
    nonterminal = set()
    rules = defaultdict(list)
    
    def __init__(self, grammar):
        candidates= set()
        for rule in grammar:
            self.rules[rule[0]].append(rule[1:])
            self.nonterminal.add(rule[0])
            
            if len(rule) == 2:
                candidates.add(rule[1])
                
        self.literals = candidates - self.nonterminal
        
    def tokenize(self, str):
        return str.split(' ')

    def parse(self, str):
        tokens = self.tokenize(str)