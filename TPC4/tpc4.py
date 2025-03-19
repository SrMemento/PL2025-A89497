import sys
import re

def parse_tokens(input_code):
    TOKEN_TYPES = [
        ('KW_SELECT',   r'\bselect\b'),
        ('KW_WHERE',    r'\bwhere\b'),
        ('KW_LIMIT',    r'\bLIMIT\b'),
        ('VAR',         r'\?[a-zA-Z_]\w*'),
        ('ID',          r'[a-zA-Z_][\w:]*'),
        ('NUM',         r'\d+'),
        ('TEXT',        r'"[^"]*"'),
        ('LANG',        r'@[a-zA-Z]+'),
        ('BRACKET',     r'[{}()]'),
        ('OPERATOR',    r'[<>]'),
        ('PUNCTUATION', r'\.'),
        ('LINE_BREAK',  r'\n'),
        ('WHITESPACE',  r'[ \t]+'),
        ('INVALID',     r'.'),
    ]
    
    combined_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES)
    tokens_found = []
    current_line = 1
    
    for match in re.finditer(combined_regex, input_code):
        groups = match.groupdict()
        
        if groups['KW_SELECT']:
            token = ('SELECT', 'select', current_line, match.span())
        elif groups['KW_WHERE']:
            token = ('WHERE', 'where', current_line, match.span())
        elif groups['KW_LIMIT']:
            token = ('LIMIT', 'LIMIT', current_line, match.span())
        elif groups['VAR']:
            token = ('VARIABLE', groups['VAR'], current_line, match.span())
        elif groups['ID']:
            token = ('IDENTIFIER', groups['ID'], current_line, match.span())
        elif groups['NUM']:
            token = ('NUMBER', int(groups['NUM']), current_line, match.span())
        elif groups['TEXT']:
            token = ('STRING', groups['TEXT'], current_line, match.span())
        elif groups['LANG']:
            token = ('LANG_TAG', groups['LANG'], current_line, match.span())
        elif groups['BRACKET']:
            token = ('SYMBOL', groups['BRACKET'], current_line, match.span())
        elif groups['OPERATOR']:
            token = ('COMPARATOR', groups['OPERATOR'], current_line, match.span())
        elif groups['PUNCTUATION']:
            token = ('DOT', groups['PUNCTUATION'], current_line, match.span())
        elif groups['LINE_BREAK']:
            current_line += 1
            continue
        elif groups['WHITESPACE']:
            continue
        else:
            token = ('ERRO', match.group(), current_line, match.span())
        
        tokens_found.append(token)
    
    return tokens_found

def run(arg_count, arg_list):
    if arg_count != 2:
        print("Usage: tpc4.py <input_file>")
        return
    
    target_file = arg_list[1]
    try:
        with open(target_file, "r") as f:
            content = f.read()
            print("\nINPUT QUERY:\n" + content + "\n")
            for tok in parse_tokens(content):
                print(tok)
    except IOError:
        print(f"Error: File '{target_file}' not found")

if __name__ == "__main__":
    run(len(sys.argv), sys.argv)
