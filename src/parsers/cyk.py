'''
Created on Sep 6, 2011

@author: alexpak
'''

from collections import defaultdict

class CYK:
    literals = set()
    nonterminal = set()
    rules = []
    
    index = defaultdict(set)
    rindex = defaultdict(set)
    
    def __init__(self, grammar):
        candidates = set()
        for rule in grammar:
            self.rules.append(rule)
            self.nonterminal.add(rule[0])
            
            if len(rule) == 2:
                candidates.add(rule[1])
                
        self.literals = candidates - self.nonterminal
        
        for n in range(0, len(self.rules)):
            rule = self.rules[n]
            if len(rule) == 2:
                self.rindex[rule[1]].add(n)
                
            self.index[rule[0]].add(n)
            
    def tokenize(self, str):
        return str.split(' ')

    def parse(self, str):
        tokens = self.tokenize(str)
        
        P = {};
        len_tokens = len(tokens)
        
        # returns positions of matching components or empty list
        def match(rule, start, length):
            if len(rule) == 1:
                result = [length] if rule[0] in P[start][length] else []
            else:
                result = []
                for l in range(1, length):
                    if start + l > len_tokens:
                        break

                    if rule[0] not in P[start][l]:
                        continue
                    
                    tail = match(rule[1:], start + l, length - l)
                    if not len(tail):
                        continue
                    result = [l] + tail
                    break
                    
            return result
        
        # start at the leafs
        for p in range(0, len_tokens):
            tokenset = set(tokens[p])
            P[p] = {1: defaultdict(set)}
            while len(tokenset):
                new_tokenset = set()
                for token in tokenset:
                    for n in self.rindex[token]:
                        rule = self.rules[n]
                        P[p][1][rule[0]].add(n)
                        new_tokenset.add(rule[0])
                        
                tokenset = new_tokenset
                    
        for l in range(2, len_tokens + 1): # length
            for p in range(0, len_tokens): # position
                P[p][l] = defaultdict(set)
                for n in range(0, len(self.rules)):
                    rule = self.rules[n]
                    matching = match(rule[1:], p, l)
                    if matching:
                        P[p][l][rule[0]].add((n, tuple(matching)))
        
        self.P = P
        self.tokens = tokens
        
        return len(P[0][len_tokens])
    
    def build_tree(self):
        def build(head, start, length):
            for matching in self.P[start][length][head]:
                if type(matching) == tuple:
                    rule_n, lengths = matching
                    rule = self.rules[rule_n]
                    root = [head]
                    start = start
                    for i in range(0, len(rule) - 1):
                        root.append(build(rule[i + 1], start, lengths[i]))
                        start += lengths[i]
                else:
                    rule = self.rules[matching]
                    if rule[1] in self.literals:
                        root = [head, rule[1]]
                    else:
                        root = [head, build(rule[1], start, length)]
                    
                return tuple(root)
            
        return build('EX', 0, len(self.tokens))
    
    def print_tree(self, tree, padding = '', pad_with = '\t'):
        if len(tree) == 2 and tree[1] in self.literals:
            print('{0}({1} "{2}")'.format(padding, tree[0], tree[1]))
        else:
            print('{0}({1}'.format(padding, tree[0]))
            for branch in tree[1:]:
                self.print_tree(branch, padding + pad_with, pad_with)
            print('{0})'.format(padding))