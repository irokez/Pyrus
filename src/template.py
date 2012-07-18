#!/usr/bin/env python3
'''
Created on Aug 7, 2011

@author: alexpak
'''
def print_stack(stack, padding = '\n', pad_with = '\t'):
	s = ''
	for expr in stack:
		if isinstance(expr, str):
			s += padding + '__s__ +="""' + expr.replace('"', '\\"') + '"""'
		else:
			if expr[0] == 'if':
				s += padding + 'if ' + expr[1] + ':'
				s += print_stack(expr[2], padding + pad_with, pad_with) or padding + pad_with + 'pass'
				s += padding + 'else:'
				s += print_stack(expr[3], padding + pad_with, pad_with) or padding + pad_with + 'pass'
			elif expr[0] == 'for':
				s += padding + 'for ' + expr[1] + ':'
				s += print_stack(expr[2], padding + pad_with, pad_with) or padding + pad_with + 'pass'
			elif expr[0] == 'print':
				s += padding + '__s__+=str(' + expr[1] + ')'
	return s

class Template:
	vars = {}
	
	def assign(self, key, val):
		self.vars[key] = val
	
	def __setattr__(self, key, val):
		self.assign(key, val)
		
	def __setitem__(self, key, val):
		self.assign(key, val)
	
	def transform(self, template):
		buffer = ''
		
		stack = []
		current_stack = stack
		stack_chain = []
		stack_chain.append(current_stack)
		expr = tuple()
		last_if = tuple()
		open_bracket = False
		for ch in template:
			if ch == '{':
				if open_bracket:
					current_stack.append('{')
					
				open_bracket = True
				current_stack.append(buffer)
				buffer = ''
			elif ch == '}' and len(buffer):
				if buffer[0:3] == 'if ':
					expr = ('if', buffer[3:], [], [])
					current_stack.append(expr)
					stack_chain.append(current_stack)
					current_stack = expr[2]
					last_if = expr
					
				elif buffer == 'else':
					if last_if[0] != 'if':
						exit('Expected IF for ELSE')

					current_stack = last_if[3]
					
				elif buffer[0:4] == 'for ':
					expr = ('for', buffer[4:], [])
					current_stack.append(expr)
					stack_chain.append(current_stack)
					current_stack = expr[2]
					
				elif buffer[0] == '$':
					expr = ('print', buffer[1:])
					current_stack.append(expr)

				elif buffer == 'end':
					current_stack = stack_chain.pop()
				
				else:
					if open_bracket:
						current_stack.append('{')

					current_stack.append(buffer + '}')
				
				open_bracket = False
				buffer = ''
			else:
				buffer += ch
		
		if buffer:		
			if open_bracket:
				current_stack.append('{')
			current_stack.append(buffer)

		source = '__s__ = ""' + print_stack(stack)
		
		exec(source, self.vars)
		return self.vars['__s__']
