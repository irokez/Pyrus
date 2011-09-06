WHITE_SPACE = {' ', '\t'}
LINE_BREAK = {'\n', '\r'}

class RuleError(Exception):
    def __init__(self, msg, line, pos):
        self.msg = msg
        self.line = line
        self.pos = pos

    def __str__(self):
        return repr('{0} at {1}:{2}'.format(self.msg, self.line, self.pos))

def read_rules(str):
    rules = []
    rule = []
    token = ''
    quoted = False
    line_num = 0
    char_num = 0
    for ch in str:
        if ch in WHITE_SPACE | LINE_BREAK:
            if len(token):
                rule.append(token)
                token = ''
                
            if ch in LINE_BREAK:
                if quoted:
                    raise RuleError('Unexpected line break', line_num, char_num)
                
                line_num += 1
                char_num = 0
                if len(rule):
                    rules.append(rule)
                    rule = []

        elif ch == '=' and not quoted:
            if len(token):
                rule.append(token)
                token = ''

            if len(rule) > 1:
                raise RuleError('Unexpected "="', line_num, char_num)
        
        elif ch == '"':
            if quoted:
                rule.append(token)
                token = ''
                
            quoted = not quoted
        
        elif ch == '|' and not quoted:
            if len(token):
                rule.append(token)
                token = ''

            if len(rule) < 1:
                raise RuleError('Unexpected "|"', line_num, char_num)
                
            rules.append(rule)
            rule = [rule[0]]
            
        else:
            token += ch

        char_num += 1
        
    return rules
        