"""
Vi Language Parser - Enhanced
Parses .vi files into Abstract Syntax Tree
Features: nested functions, URL imports, implicit arrays, 'to' syntax
"""

import os
import re
import urllib.request
import tempfile
from typing import List, Dict, Any, Optional, Set, Tuple


# ============================================================================
# LEXER
# ============================================================================

def remove_comments_with_lines(text: str) -> Tuple[str, Dict[int, int]]:
    """Remove comments but preserve line mapping"""
    lines = text.split('\n')
    stripped_lines = []
    line_map = {}
    
    i = 0
    in_comment = False
    
    while i < len(lines):
        line = lines[i]
        cleaned = []
        j = 0
        
        while j < len(line):
            if in_comment:
                # Look for comment end
                if j + 1 < len(line) and line[j:j+2] == '#>':
                    in_comment = False
                    j += 2
                else:
                    j += 1
            else:
                # Look for comment start
                if j + 1 < len(line) and line[j:j+2] == '<#':
                    in_comment = True
                    # Check if comment ends on same line
                    end_pos = line.find('#>', j + 2)
                    if end_pos != -1:
                        in_comment = False
                        j = end_pos + 2
                    else:
                        j += 2
                else:
                    cleaned.append(line[j])
                    j += 1
        
        stripped_lines.append(''.join(cleaned) if not in_comment else '')
        line_map[len(stripped_lines)] = i + 1
        i += 1
    
    return '\n'.join(stripped_lines), line_map


def tokenize(source: str) -> List[Dict[str, Any]]:
    """Tokenize Vi source code"""
    source, line_map = remove_comments_with_lines(source)
    tokens = []
    lines = source.split('\n')
    indent_stack = [0]
    keywords = {'main', 'from', 'import', 'if', 'else', 'for', 'in', 'while', 'return', 'true', 'false', 'and', 'or', 'not', 'all', 'range', 'to'}
    
    for line_num, line in enumerate(lines, 1):
        original_line = line_map.get(line_num, line_num)
        if not line.strip():
            continue
        
        indent_level = len(line) - len(line.lstrip())
        stripped = line.strip()
        
        if not stripped:
            continue
        
        if indent_level > indent_stack[-1]:
            indent_stack.append(indent_level)
            tokens.append({'type': 'INDENT', 'value': None, 'line': original_line, 'col': 0})
        elif indent_level < indent_stack[-1]:
            while indent_stack[-1] > indent_level:
                indent_stack.pop()
                tokens.append({'type': 'DEDENT', 'value': None, 'line': original_line, 'col': 0})
        
        col = indent_level
        i = 0
        
        while i < len(stripped):
            char = stripped[i]
            
            if char in ' \t':
                i += 1
                col += 1
                continue
            
            if char.isdigit() or (char == '-' and i + 1 < len(stripped) and stripped[i + 1].isdigit()):
                num_str = ''
                if char == '-':
                    num_str += char
                    i += 1
                while i < len(stripped) and (stripped[i].isdigit() or stripped[i] == '.'):
                    num_str += stripped[i]
                    i += 1
                tokens.append({'type': 'NUMBER', 'value': float(num_str) if '.' in num_str else int(num_str), 'line': original_line, 'col': col})
                col += len(num_str)
                continue
            
            if char in '"\'':
                quote = char
                string_val = ''
                i += 1
                while i < len(stripped) and stripped[i] != quote:
                    if stripped[i] == '\\' and i + 1 < len(stripped):
                        i += 1
                        string_val += stripped[i]
                    elif stripped[i] == '{' and i + 1 < len(stripped) and stripped[i + 1] == '{':
                        # Handle {{}} escape for literal braces
                        string_val += '{'
                        i += 2
                        continue
                    elif stripped[i] == '}' and i + 1 < len(stripped) and stripped[i + 1] == '}':
                        # Handle {{}} escape for literal braces
                        string_val += '}'
                        i += 2
                        continue
                    else:
                        string_val += stripped[i]
                    i += 1
                i += 1
                tokens.append({'type': 'STRING', 'value': string_val, 'line': original_line, 'col': col})
                col += len(string_val) + 2
                continue
            
            if char.isalpha() or char == '_':
                ident = ''
                while i < len(stripped) and (stripped[i].isalnum() or stripped[i] == '_'):
                    ident += stripped[i]
                    i += 1
                
                token_type = 'KEYWORD' if ident in keywords else 'IDENTIFIER'
                tokens.append({'type': token_type, 'value': ident, 'line': original_line, 'col': col})
                col += len(ident)
                continue
            
            two_char_ops = {'>=': 'GTE', '<=': 'LTE', '==': 'EQ', '!=': 'NEQ'}
            if i + 1 < len(stripped) and stripped[i:i+2] in two_char_ops:
                tokens.append({'type': two_char_ops[stripped[i:i+2]], 'value': stripped[i:i+2], 'line': original_line, 'col': col})
                i += 2
                col += 2
                continue
            
            single_char = {'=': 'ASSIGN', '+': 'PLUS', '-': 'MINUS', '*': 'MULTIPLY', '/': 'DIVIDE',
                          '!': 'NOT', '>': 'GT', '<': 'LT', ':': 'COLON', ',': 'COMMA', '.': 'DOT',
                          '(': 'LPAREN', ')': 'RPAREN', '[': 'LBRACKET', ']': 'RBRACKET',
                          '{': 'LBRACE', '}': 'RBRACE'}
            
            if char in single_char:
                tokens.append({'type': single_char[char], 'value': char, 'line': original_line, 'col': col})
                i += 1
                col += 1
                continue
            
            i += 1
            col += 1
        
        tokens.append({'type': 'NEWLINE', 'value': None, 'line': original_line, 'col': col})
    
    last_line = line_map.get(len(lines), len(lines))
    
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append({'type': 'DEDENT', 'value': None, 'line': last_line, 'col': 0})
    
    tokens.append({'type': 'EOF', 'value': None, 'line': last_line, 'col': 0})
    return tokens

# ============================================================================
# PARSER - Builds AST with full control flow
# ============================================================================

def parse(tokens: List[Dict]) -> Dict:
    """Parse tokens into AST"""
    pos = [0]
    
    def peek(offset=0):
        idx = pos[0] + offset
        return tokens[idx] if idx < len(tokens) else tokens[-1]
    
    def consume(expected_type=None):
        token = peek()
        if expected_type and token['type'] != expected_type:
            # Build context for better error messages
            context = []
            for i in range(-2, 3):
                idx = pos[0] + i
                if 0 <= idx < len(tokens):
                    marker = ' >>> ' if i == 0 else '     '
                    t = tokens[idx]
                    context.append(f"{marker}Line {t['line']}: {t['type']} = {t.get('value', '')}")
            context_str = '\n'.join(context)
            raise SyntaxError(
                f"Expected {expected_type}, got {token['type']} at line {token['line']}\n"
                f"\nContext:\n{context_str}"
            )
        pos[0] += 1
        return token
    
    def skip_newlines():
        while peek()['type'] == 'NEWLINE':
            consume()
    
    def skip_whitespace():
        while peek()['type'] in ['NEWLINE', 'INDENT', 'DEDENT']:
            consume()
    
    def parse_expression():
        return parse_ternary()
    
    def parse_ternary():
        expr = parse_or()
        if peek()['type'] == 'KEYWORD' and peek()['value'] == 'if':
            consume()
            skip_whitespace()
            if peek()['type'] == 'LPAREN':
                consume('LPAREN')
            condition = parse_or()
            if peek()['type'] == 'RPAREN':
                consume('RPAREN')
            skip_whitespace()
            if peek()['type'] == 'KEYWORD' and peek()['value'] == 'else':
                consume()
                skip_whitespace()
                else_expr = parse_ternary()
                return {'type': 'ternary', 'condition': condition, 'then': expr, 'else': else_expr}
        return expr
    
    def parse_or():
        left = parse_and()
        while peek()['type'] == 'KEYWORD' and peek()['value'] == 'or':
            consume()
            right = parse_and()
            left = {'type': 'binary_op', 'op': 'or', 'left': left, 'right': right}
        return left
    
    def parse_and():
        left = parse_comparison()
        while peek()['type'] == 'KEYWORD' and peek()['value'] == 'and':
            consume()
            right = parse_comparison()
            left = {'type': 'binary_op', 'op': 'and', 'left': left, 'right': right}
        return left
    
    def parse_comparison():
        left = parse_additive()
        while peek()['type'] in ['GT', 'LT', 'GTE', 'LTE', 'EQ', 'NEQ']:
            op = consume()
            right = parse_additive()
            left = {'type': 'binary_op', 'op': op['value'], 'left': left, 'right': right}
        return left
    
    def parse_additive():
        left = parse_multiplicative()
        while peek()['type'] in ['PLUS', 'MINUS']:
            op = consume()
            right = parse_multiplicative()
            left = {'type': 'binary_op', 'op': op['value'], 'left': left, 'right': right}
        return left
    
    def parse_multiplicative():
        left = parse_unary()
        while peek()['type'] in ['MULTIPLY', 'DIVIDE']:
            op = consume()
            right = parse_unary()
            left = {'type': 'binary_op', 'op': op['value'], 'left': left, 'right': right}
        return left
    
    def parse_unary():
        if peek()['type'] in ['NOT', 'MINUS']:
            op = consume()
            operand = parse_unary()
            return {'type': 'unary_op', 'op': op['value'] if op['type'] != 'NOT' else 'not', 'operand': operand}
        return parse_postfix()
    
    def parse_postfix():
        expr = parse_primary()
        while True:
            if peek()['type'] == 'DOT':
                consume()
                field = consume('IDENTIFIER')
                expr = {'type': 'member', 'object': expr, 'field': field['value']}
            elif peek()['type'] == 'LBRACKET':
                consume()
                index = parse_expression()
                consume('RBRACKET')
                expr = {'type': 'index', 'object': expr, 'index': index}
            elif peek()['type'] == 'LPAREN':
                consume()
                args = []
                while peek()['type'] not in ['RPAREN', 'EOF']:
                    args.append(parse_expression())
                    if peek()['type'] == 'COMMA':
                        consume()
                consume('RPAREN')
                if expr.get('type') == 'member':
                    expr = {'type': 'method_call', 'object': expr['object'], 'method': expr['field'], 'args': args}
                else:
                    expr = {'type': 'call', 'function': expr, 'args': args}
            else:
                break
        return expr
    
    def parse_primary():
        token = peek()
        
        if token['type'] == 'NUMBER':
            consume()
            return {'type': 'literal', 'value': token['value'], 'value_type': 'number'}
        
        if token['type'] == 'STRING':
            consume()
            return {'type': 'literal', 'value': token['value'], 'value_type': 'string'}
        
        if token['type'] == 'KEYWORD' and token['value'] in ['true', 'false']:
            consume()
            return {'type': 'literal', 'value': token['value'] == 'true', 'value_type': 'boolean'}
        
        if token['type'] == 'KEYWORD' and token['value'] == 'not':
            consume()
            operand = parse_unary()
            return {'type': 'unary_op', 'op': 'not', 'operand': operand}
        
        if token['type'] == 'IDENTIFIER':
            consume()
            return {'type': 'var', 'name': token['value']}
        
        if token['type'] == 'LBRACKET':
            consume()
            elements = []
            while peek()['type'] not in ['RBRACKET', 'EOF']:
                skip_whitespace()
                if peek()['type'] == 'RBRACKET':
                    break
                if peek()['type'] == 'IDENTIFIER' and peek(1)['type'] == 'COLON' and peek(2)['type'] not in ['NEWLINE', 'INDENT']:
                    key = consume('IDENTIFIER')['value']
                    consume('COLON')
                    skip_whitespace()
                    value = parse_expression()
                    elements.append({'type': 'kvpair', 'key': key, 'value': value})
                else:
                    elements.append(parse_expression())
                skip_whitespace()
                if peek()['type'] == 'COMMA':
                    consume()
                skip_whitespace()
            consume('RBRACKET')
            return {'type': 'array', 'elements': elements}
        
        if token['type'] == 'LPAREN':
            consume()
            skip_whitespace()
            expr = parse_expression()
            skip_whitespace()
            consume('RPAREN')
            return expr
        
        if token['type'] == 'LBRACE':
            consume()
            properties = {}
            while peek()['type'] not in ['RBRACE', 'EOF']:
                skip_whitespace()
                if peek()['type'] == 'RBRACE':
                    break
                key = consume('IDENTIFIER')['value']
                consume('COLON')
                skip_whitespace()
                value = parse_expression()
                properties[key] = value
                skip_whitespace()
                if peek()['type'] == 'COMMA':
                    consume()
                skip_whitespace()
            consume('RBRACE')
            return {'type': 'object', 'properties': properties}
        
        context = []
        for i in range(-2, 3):
            idx = pos[0] + i
            if 0 <= idx < len(tokens):
                marker = ' --> ' if i == 0 else '     '
                t = tokens[idx]
                context.append(f"{marker}Line {t['line']}: {t['type']} {t.get('value', '')}")
        context_str = '\n'.join(context)
        raise SyntaxError(f"Unexpected token {token['type']} at line {token['line']}\n\nContext:\n{context_str}")
    
    def parse_statement():
        """Parse a statement - full control flow support including nested functions"""
        token = peek()
        
        # Nested function definition: name(params):
        if token['type'] == 'IDENTIFIER' and peek(1)['type'] == 'LPAREN':
            # Check if this is a function call or definition
            # Definition has COLON after RPAREN, call doesn't
            saved_pos = pos[0]
            consume('IDENTIFIER')
            consume('LPAREN')
            paren_depth = 1
            while paren_depth > 0 and peek()['type'] != 'EOF':
                if peek()['type'] == 'LPAREN':
                    paren_depth += 1
                elif peek()['type'] == 'RPAREN':
                    paren_depth -= 1
                consume()
            
            is_func_def = peek()['type'] == 'COLON'
            pos[0] = saved_pos
            
            if is_func_def:
                # Parse nested function definition
                fname = consume('IDENTIFIER')['value']
                consume('LPAREN')
                params = []
                while peek()['type'] != 'RPAREN':
                    if peek()['type'] != 'IDENTIFIER':
                        raise SyntaxError(f"Function '{fname}' expects parameter names")
                    params.append(consume('IDENTIFIER')['value'])
                    if peek()['type'] == 'COMMA':
                        consume()
                consume('RPAREN')
                consume('COLON')
                skip_newlines()
                
                if peek()['type'] != 'INDENT':
                    func_body = []
                else:
                    consume('INDENT')
                    func_body = []
                    while peek()['type'] not in ['DEDENT', 'EOF']:
                        if peek()['type'] == 'NEWLINE':
                            skip_newlines()
                            continue
                        func_body.append(parse_statement())
                        skip_newlines()
                    consume('DEDENT')
                
                return {'type': 'function_def', 'name': fname, 'params': params, 'body': func_body}
        
        # Return statement
        if token['type'] == 'KEYWORD' and token['value'] == 'return':
            consume()
            value = parse_expression()
            return {'type': 'return', 'value': value}
        
        # If statement
        if token['type'] == 'KEYWORD' and token['value'] == 'if':
            consume()
            if peek()['type'] == 'LPAREN':
                consume('LPAREN')
            condition = parse_expression()
            if peek()['type'] == 'RPAREN':
                consume('RPAREN')
            consume('COLON')
            skip_newlines()
            
            # Parse then block
            consume('INDENT')
            then_body = []
            while peek()['type'] not in ['DEDENT', 'EOF']:
                if peek()['type'] == 'NEWLINE':
                    skip_newlines()
                    continue
                then_body.append(parse_statement())
                skip_newlines()
            consume('DEDENT')
            
            # Parse else/elif blocks
            else_body = []
            if peek()['type'] == 'KEYWORD' and peek()['value'] == 'else':
                consume()
                if peek()['type'] == 'KEYWORD' and peek()['value'] == 'if':
                    # else if -> recursively parse as nested if
                    else_body = [parse_statement()]
                else:
                    # plain else
                    consume('COLON')
                    skip_newlines()
                    consume('INDENT')
                    while peek()['type'] not in ['DEDENT', 'EOF']:
                        if peek()['type'] == 'NEWLINE':
                            skip_newlines()
                            continue
                        else_body.append(parse_statement())
                        skip_newlines()
                    consume('DEDENT')
            
            return {'type': 'if', 'condition': condition, 'then': then_body, 'else': else_body}
        
        # For loop
        if token['type'] == 'KEYWORD' and token['value'] == 'for':
            consume()
            var_name = consume('IDENTIFIER')['value']
            consume('KEYWORD')  # 'in'
            iterable = parse_expression()
            consume('COLON')
            skip_newlines()
            
            consume('INDENT')
            for_body = []
            while peek()['type'] not in ['DEDENT', 'EOF']:
                if peek()['type'] == 'NEWLINE':
                    skip_newlines()
                    continue
                for_body.append(parse_statement())
                skip_newlines()
            consume('DEDENT')
            
            return {'type': 'for', 'var': var_name, 'iterable': iterable, 'body': for_body}
        
        # While loop
        if token['type'] == 'KEYWORD' and token['value'] == 'while':
            consume()
            if peek()['type'] == 'LPAREN':
                consume('LPAREN')
            condition = parse_expression()
            if peek()['type'] == 'RPAREN':
                consume('RPAREN')
            consume('COLON')
            skip_newlines()

            consume('INDENT')
            while_body = []
            while peek()['type'] not in ['DEDENT', 'EOF']:
                if peek()['type'] == 'NEWLINE':
                    skip_newlines()
                    continue
                while_body.append(parse_statement())
                skip_newlines()
            consume('DEDENT')

            return {'type': 'while', 'condition': condition, 'body': while_body}

        # Container modification: container_name: attribute = value
        if token['type'] == 'IDENTIFIER' and peek(1)['type'] == 'COLON':
            target_name = consume('IDENTIFIER')['value']
            consume('COLON')
            skip_newlines()
            
            mod_attrs = {}
            if peek()['type'] == 'INDENT':
                consume('INDENT')
                while peek()['type'] not in ['DEDENT', 'EOF']:
                    if peek()['type'] == 'NEWLINE':
                        skip_newlines()
                        continue
                    attr_name = consume('IDENTIFIER')['value']
                    consume('ASSIGN')
                    attr_value = parse_expression()
                    mod_attrs[attr_name] = attr_value
                    skip_newlines()
                consume('DEDENT')
            
            return {'type': 'modify_container', 'target': {'type': 'var', 'name': target_name}, 'attributes': mod_attrs}
        
        # Expression statement or assignment
        target_expr = parse_expression()
        if peek()['type'] == 'ASSIGN':
            consume()
            # Check for implicit array: a = 1, 2, 3 (no brackets)
            value_expr = parse_expression()
            # If next token is comma and not in brackets/parens, create array
            if peek()['type'] == 'COMMA':
                elements = [value_expr]
                while peek()['type'] == 'COMMA':
                    consume()
                    skip_newlines()
                    elements.append(parse_expression())
                value_expr = {'type': 'array', 'elements': elements}
            return {'type': 'assign', 'target': target_expr, 'value': value_expr}
        else:
            return {'type': 'expr_stmt', 'expr': target_expr}
    
    def parse_container_body():
        """Parse container attributes and nested containers"""
        container = {'attributes': {}, 'children_def': []}
        
        if peek()['type'] != 'INDENT':
            return container
        
        consume('INDENT')
        
        while peek()['type'] not in ['DEDENT', 'EOF']:
            if peek()['type'] == 'NEWLINE':
                skip_newlines()
                continue
            
            if peek()['type'] == 'DEDENT':
                break
            
            if peek()['type'] == 'IDENTIFIER':
                attr_name = consume('IDENTIFIER')['value']
                
                if peek()['type'] == 'ASSIGN':
                    consume('ASSIGN')
                    first_val = parse_expression()
                    
                    # Check for "X to Y" syntax for ranges
                    if peek()['type'] == 'KEYWORD' and peek()['value'] == 'to':
                        consume()  # consume 'to'
                        second_val = parse_expression()
                        # Create array [X, Y]
                        attr_value = {'type': 'array', 'elements': [first_val, second_val]}
                    elif peek()['type'] == 'COMMA':
                        # Implicit array: attr = val1, val2, val3
                        elements = [first_val]
                        while peek()['type'] == 'COMMA':
                            consume('COMMA')
                            skip_newlines()
                            elements.append(parse_expression())
                        attr_value = {'type': 'array', 'elements': elements}
                    else:
                        attr_value = first_val
                    
                    container['attributes'][attr_name] = attr_value
                    skip_newlines()
                
                elif peek()['type'] == 'COLON':
                    consume('COLON')
                    skip_newlines()
                    if peek()['type'] == 'INDENT':
                        nested = parse_container_body()
                        nested['name'] = attr_name
                        container['children_def'].append(nested)
                    else:
                        # Inline value syntax: on_click: func() or attr: value
                        if peek()['type'] not in ['NEWLINE', 'DEDENT', 'EOF']:
                            attr_value = parse_expression()
                            container['attributes'][attr_name] = attr_value
                        skip_newlines()
                else:
                    skip_newlines()
            else:
                consume()
                skip_newlines()
        
        if peek()['type'] == 'DEDENT':
            consume('DEDENT')
        
        return container
    
    # Build AST
    ast = {
        'imports': [],
        'variables': {},
        'functions': {},
        'containers': {},
        'main_container': None,
        'config': {}
    }
    
    skip_newlines()
    
    while peek()['type'] != 'EOF':
        token = peek()
        
        # Handle imports
        if token['type'] == 'KEYWORD' and token['value'] == 'from':
            consume()
            path_token = peek()
            if path_token['type'] == 'STRING':
                path = consume('STRING')['value']
            else:
                # Allow identifier for URL imports
                path = consume('IDENTIFIER')['value']
            
            consume('KEYWORD')  # 'import'
            items = []
            if peek()['type'] == 'MULTIPLY':
                consume()
                items = '*'
            else:
                while True:
                    items.append(consume('IDENTIFIER')['value'])
                    if peek()['type'] != 'COMMA':
                        break
                    consume()
            ast['imports'].append({'source': path, 'items': items})
            skip_newlines()
        
        elif token['type'] == 'KEYWORD' and token['value'] == 'import':
            consume()
            path_token = peek()
            if path_token['type'] == 'STRING':
                path = consume('STRING')['value']
            else:
                # Allow identifier for URL imports
                path = consume('IDENTIFIER')['value']
            ast['imports'].append({'source': path, 'items': '*'})
            skip_newlines()
        
        # Handle variable assignment
        elif token['type'] == 'IDENTIFIER':
            name = consume()['value']
            
            if peek()['type'] == 'ASSIGN':
                consume()
                value = parse_expression()
                # Check for implicit array
                if peek()['type'] == 'COMMA':
                    elements = [value]
                    while peek()['type'] == 'COMMA':
                        consume()
                        skip_newlines()
                        elements.append(parse_expression())
                    value = {'type': 'array', 'elements': elements}
                ast['variables'][name] = {'value': value}
                skip_newlines()
            
            # Handle comma-separated containers with same style
            elif peek()['type'] == 'COMMA':
                names = [name]
                while peek()['type'] == 'COMMA':
                    consume()
                    skip_newlines()
                    names.append(consume('IDENTIFIER')['value'])
                
                consume('COLON')
                skip_newlines()
                container = parse_container_body()
                
                # Apply same body to all containers
                for cname in names:
                    ast['containers'][cname] = {
                        'attributes': container['attributes'].copy(),
                        'children_def': container['children_def'].copy()
                    }
                skip_newlines()
            
            # Handle function definition
            elif peek()['type'] == 'LPAREN':
                consume()
                params = []
                while peek()['type'] != 'RPAREN':
                    if peek()['type'] != 'IDENTIFIER':
                        raise SyntaxError(f"Function '{name}' expects parameter names")
                    params.append(consume('IDENTIFIER')['value'])
                    if peek()['type'] == 'COMMA':
                        consume()
                consume('RPAREN')
                consume('COLON')
                skip_newlines()
                
                if peek()['type'] != 'INDENT':
                    ast['functions'][name] = {'params': params, 'body': []}
                    continue
                
                consume('INDENT')
                body = []
                
                # Parse function body with full statement support
                while peek()['type'] not in ['DEDENT', 'EOF']:
                    if peek()['type'] == 'NEWLINE':
                        skip_newlines()
                        continue
                    body.append(parse_statement())
                    skip_newlines()
                
                consume('DEDENT')
                ast['functions'][name] = {'params': params, 'body': body}
            
            # Handle container definition
            elif peek()['type'] == 'COLON':
                consume()
                skip_newlines()
                container = parse_container_body()
                if name == 'config':
                    ast['config'] = container
                else:
                    ast['containers'][name] = container
            else:
                skip_newlines()
        
        # Handle main container
        elif token['type'] == 'KEYWORD' and token['value'] == 'main':
            consume()
            name = consume('IDENTIFIER')['value']
            consume('COLON')
            skip_newlines()
            container = parse_container_body()
            ast['containers'][name] = container
            ast['main_container'] = name
        
        else:
            skip_newlines()
            if peek()['type'] not in ['NEWLINE', 'EOF']:
                consume()
    
    return ast


# ============================================================================
# IMPORT RESOLVER
# ============================================================================

def resolve_imports(ast: Dict, base_path: str) -> Dict:
    """Resolve imports and merge ASTs - supports file paths and URLs"""
    if not ast['imports']:
        return ast
    
    for import_node in ast['imports']:
        source = import_node['source']
        items = import_node['items']
        
        # Check if source is a URL
        is_url = source.startswith('http://') or source.startswith('https://')
        
        if is_url:
            # Download from URL
            try:
                response = urllib.request.urlopen(source)
                code = response.read().decode('utf-8')
                file_path = None  # No local file path for URLs
            except Exception as e:
                raise ImportError(f"Cannot import from URL '{source}': {e}")
        else:
            # Local file path
            file_path = source.replace('\\', os.sep)
            if not os.path.isabs(file_path):
                file_path = os.path.join(base_path, file_path)
            
            if not os.path.exists(file_path):
                raise ImportError(f"Cannot import '{source}': File not found at {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
            except Exception as e:
                raise ImportError(f"Cannot import '{source}': {e}")
        
        try:
            tokens = tokenize(code)
            imported_ast = parse(tokens)
        except Exception as e:
            raise ImportError(f"Cannot import '{source}': Parse error - {e}")
        
        # For local files, resolve their imports too
        if file_path:
            import_base = os.path.dirname(file_path)
            imported_ast = resolve_imports(imported_ast, import_base)
        else:
            # For URLs, can't resolve relative imports
            imported_ast = resolve_imports(imported_ast, '')
        
        if items == '*':
            ast['variables'].update(imported_ast['variables'])
            ast['functions'].update(imported_ast['functions'])
            ast['containers'].update(imported_ast['containers'])
        else:
            for item in items:
                found = False
                if item in imported_ast['variables']:
                    ast['variables'][item] = imported_ast['variables'][item]
                    found = True
                elif item in imported_ast['functions']:
                    ast['functions'][item] = imported_ast['functions'][item]
                    found = True
                elif item in imported_ast['containers']:
                    ast['containers'][item] = imported_ast['containers'][item]
                    found = True
                
                if not found:
                    raise ImportError(f"Cannot import '{item}' from '{source}': Item not found in file")
    
    ast['imports'] = []
    return ast


# ============================================================================
# AST VALIDATION
# ============================================================================

def validate_ast(ast: Dict) -> None:
    """Validate AST for common errors before codegen"""
    errors = []
    warnings = []
    
    # Check main container exists
    if ast['main_container'] and ast['main_container'] not in ast['containers']:
        errors.append(f"Main container '{ast['main_container']}' is not defined")
    
    # Check for undefined container references in children arrays
    for cname, container in ast['containers'].items():
        children = container['attributes'].get('children')
        if children and children.get('type') == 'array':
            for elem in children.get('elements', []):
                if elem.get('type') == 'var':
                    ref = elem['name']
                    if ref not in ast['containers']:
                        warnings.append(f"Container '{cname}' references undefined child '{ref}'")
                elif elem.get('type') == 'call':
                    # Parameterized container call
                    func = elem.get('function', {})
                    if func.get('type') == 'var':
                        ref = func['name']
                        if ref not in ast['containers'] and ref not in ast['functions']:
                            warnings.append(f"Container '{cname}' references undefined child '{ref}'")
    
    # Check for undefined function calls
    def check_calls(stmts, context):
        for stmt in stmts:
            if stmt.get('type') == 'expr_stmt':
                expr = stmt.get('expr', {})
                if expr.get('type') == 'call':
                    func = expr.get('function', {})
                    if func.get('type') == 'var':
                        fname = func['name']
                        # Check built-in functions
                        builtins = {'go_to', 'go_back', 'visit', 'play', 'wait_sec', 'random', 'length'}
                        if fname not in ast['functions'] and fname not in builtins:
                            warnings.append(f"{context}: Undefined function '{fname}' called")
            for key in ('then', 'else', 'body'):
                check_calls(stmt.get(key, []), context)
    
    for fname, fnode in ast['functions'].items():
        check_calls(fnode['body'], f"Function '{fname}'")
    
    # Check for circular container references (simple check)
    def find_refs(cname, visited=None):
        if visited is None:
            visited = set()
        if cname in visited:
            return True  # Circular
        visited.add(cname)
        container = ast['containers'].get(cname, {})
        children = container['attributes'].get('children')
        if children and children.get('type') == 'array':
            for elem in children.get('elements', []):
                if elem.get('type') == 'var':
                    if find_refs(elem['name'], visited.copy()):
                        return True
        return False
    
    for cname in ast['containers']:
        if find_refs(cname):
            errors.append(f"Circular container reference detected involving '{cname}'")
    
    # Print errors and warnings
    if warnings:
        print("\n⚠️  Warnings:")
        for w in warnings:
            print(f"  - {w}")
    
    if errors:
        print("\n❌ Errors:")
        for e in errors:
            print(f"  - {e}")
        raise ValueError("AST validation failed. Fix the errors above.")


# ============================================================================
# PARSER CLASS
# ============================================================================

class Parser:
    """Vi Language Parser - produces complete AST"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.ast = None
    
    def parse(self):
        """Parse .vi file to AST"""
        print(f"Parsing '{self.filepath}'...")
        
        with open(self.filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tokens = tokenize(source)
        ast = parse(tokens)
        
        base_path = os.path.dirname(os.path.abspath(self.filepath))
        ast = resolve_imports(ast, base_path)
        
        # Validate AST
        validate_ast(ast)
        
        self.ast = ast
        print(f"✓ Parsing complete!")
        return self.ast