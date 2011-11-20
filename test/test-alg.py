#!/usr/bin/env python3
'''
Created on Aug 19, 2011

@author: alexpak
'''

import sys
sys.path.append('src')

from alg import Vector as V

a = V([1, 2, 3, 4])
b = a + 3
c = b + 4
d = c - a
f = V([1, 1, 1, 1])
f += a
print(a)
print(b)
print(c)
print(d)
print(f)