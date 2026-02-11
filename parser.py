"""
Vi Language Compiler - Complete single-file implementation
Parses .vi files into JSON for Flutter runtime
"""

import os
import re
import json
from typing import List, Dict, Any, Optional, Set, Tuple


# ============================================================================
# MATERIAL DESIGN COLORS
# ============================================================================

MATERIAL_COLORS = {
    'red': {50: 0xFFFFEBEE, 100: 0xFFFFCDD2, 200: 0xFFEF9A9A, 300: 0xFFE57373,
            400: 0xFFEF5350, 500: 0xFFF44336, 600: 0xFFE53935, 700: 0xFFD32F2F,
            800: 0xFFC62828, 900: 0xFFB71C1C},
    'pink': {50: 0xFFFCE4EC, 100: 0xFFF8BBD0, 200: 0xFFF48FB1, 300: 0xFFF06292,
             400: 0xFFEC407A, 500: 0xFFE91E63, 600: 0xFFD81B60, 700: 0xFFC2185B,
             800: 0xFFAD1457, 900: 0xFF880E4F},
    'purple': {50: 0xFFF3E5F5, 100: 0xFFE1BEE7, 200: 0xFFCE93D8, 300: 0xFFBA68C8,
               400: 0xFFAB47BC, 500: 0xFF9C27B0, 600: 0xFF8E24AA, 700: 0xFF7B1FA2,
               800: 0xFF6A1B9A, 900: 0xFF4A148C},
    'blue': {50: 0xFFE3F2FD, 100: 0xFFBBDEFB, 200: 0xFF90CAF9, 300: 0xFF64B5F6,
             400: 0xFF42A5F5, 500: 0xFF2196F3, 600: 0xFF1E88E5, 700: 0xFF1976D2,
             800: 0xFF1565C0, 900: 0xFF0D47A1},
    'green': {50: 0xFFE8F5E9, 100: 0xFFC8E6C9, 200: 0xFFA5D6A7, 300: 0xFF81C784,
              400: 0xFF66BB6A, 500: 0xFF4CAF50, 600: 0xFF43A047, 700: 0xFF388E3C,
              800: 0xFF2E7D32, 900: 0xFF1B5E20},
    'yellow': {50: 0xFFFFFDE7, 100: 0xFFFFF9C4, 200: 0xFFFFF59D, 300: 0xFFFFF176,
               400: 0xFFFFEE58, 500: 0xFFFFEB3B, 600: 0xFFFDD835, 700: 0xFFFBC02D,
               800: 0xFFF9A825, 900: 0xFFF57F17},
    'orange': {50: 0xFFFFF3E0, 100: 0xFFFFE0B2, 200: 0xFFFFCC80, 300: 0xFFFFB74D,
               400: 0xFFFFA726, 500: 0xFFFF9800, 600: 0xFFFB8C00, 700: 0xFFF57C00,
               800: 0xFFEF6C00, 900: 0xFFE65100},
    'gray': {50: 0xFFFAFAFA, 100: 0xFFF5F5F5, 200: 0xFFEEEEEE, 300: 0xFFE0E0E0,
             400: 0xFFBDBDBD, 500: 0xFF9E9E9E, 600: 0xFF757575, 700: 0xFF616161,
             800: 0xFF424242, 900: 0xFF212121},
    'white': {500: 0xFFFFFFFF},
    'black': {500: 0xFF000000},
}


# ============================================================================
# LEXER
# ============================================================================

def remove_comments_with_lines(text: str) -> Tuple[str, Dict[int, int]]:
    """Remove comments but preserve line mapping
    Returns: (stripped_text, line_map) where line_map[stripped_line] = original_line
    """
    lines = text.split('\n')
    stripped_lines = []
    line_map = {}  # stripped_line_num -> original_line_num
    
    i = 0
    while i < len(lines):
        line = lines[i]
        # Remove inline comments
        cleaned = re.sub(r'<#.*?#>', '', line)
        
        # Check for multi-line comment start
        if '<#' in line and '#>' not in line:
            # Multi-line comment start
            j = i + 1
            while j < len(lines) and '#>' not in lines[j]:
                j += 1
            # Skip all comment lines but keep the line count
            for k in range(i, min(j + 1, len(lines))):
                stripped_lines.append('')
                line_map[len(stripped_lines)] = k + 1
            i = j + 1
        else:
            stripped_lines.append(cleaned)
            line_map[len(stripped_lines)] = i + 1
            i += 1
    
    return '\n'.join(stripped_lines), line_map


def tokenize(source: str) -> List[Dict[str, Any]]:
    """Tokenize Vi source code"""
    source, line_map = remove_comments_with_lines(source)
    tokens = []
    lines = source.split('\n')
    indent_stack = [0]
    keywords = {'main', 'from', 'import', 'if', 'else', 'for', 'in', 'return', 'true', 'false', 'and', 'or', 'not', 'all'}
    
    for line_num, line in enumerate(lines, 1):
        original_line = line_map.get(line_num, line_num)  # Map to original line number
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
    
    # Get the last original line number
    last_line = line_map.get(len(lines), len(lines))
    
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append({'type': 'DEDENT', 'value': None, 'line': last_line, 'col': 0})
    
    tokens.append({'type': 'EOF', 'value': None, 'line': last_line, 'col': 0})
    return tokens


# ============================================================================
# PARSER
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
            raise SyntaxError(f"Expected {expected_type}, got {token['type']} at line {token['line']}")
        pos[0] += 1
        return token
    
    def skip_newlines():
        while peek()['type'] == 'NEWLINE':
            consume()
    
    def skip_whitespace():
        """Skip newlines, indents, and dedents in expression contexts"""
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
        
        # Handle if-first ternary: if (condition) then_value else else_value
        if token['type'] == 'KEYWORD' and token['value'] == 'if':
            consume()
            skip_whitespace()
            if peek()['type'] == 'LPAREN':
                consume('LPAREN')
            condition = parse_or()
            if peek()['type'] == 'RPAREN':
                consume('RPAREN')
            skip_whitespace()
            then_expr = parse_ternary()  # Parse the 'then' value (could be nested ternary)
            skip_whitespace()
            if peek()['type'] == 'KEYWORD' and peek()['value'] == 'else':
                consume()
                skip_whitespace()
                else_expr = parse_ternary()  # Parse the 'else' value
                return {'type': 'ternary', 'condition': condition, 'then': then_expr, 'else': else_expr}
            else:
                raise SyntaxError(f"Expected 'else' after if-expression at line {peek()['line']}")
        
        if token['type'] == 'IDENTIFIER':
            consume()
            return {'type': 'var', 'name': token['value']}
        
        if token['type'] == 'LBRACKET':
            consume()
            elements = []
            while peek()['type'] not in ['RBRACKET', 'EOF']:
                skip_whitespace()  # Skip newlines, indents, dedents
                
                # Check if we hit the closing bracket after whitespace
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
        
        # Show context in error message
        context = []
        for i in range(-2, 3):
            idx = pos[0] + i
            if 0 <= idx < len(tokens):
                marker = ' --> ' if i == 0 else '     '
                t = tokens[idx]
                context.append(f"{marker}Line {t['line']}: {t['type']} {t.get('value', '')}")
        context_str = '\n'.join(context)
        raise SyntaxError(f"Unexpected token {token['type']} at line {token['line']}\n\nContext:\n{context_str}\n\nHint: If this is inside an array or expression with line breaks, check your indentation.")
    
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
            
            # If we hit a DEDENT, we're done with this container
            if peek()['type'] == 'DEDENT':
                break
            
            if peek()['type'] == 'IDENTIFIER':
                attr_name = consume('IDENTIFIER')['value']
                
                if peek()['type'] == 'ASSIGN':
                    consume('ASSIGN')
                    # Check if this is a comma-separated list (implicit array)
                    first_val = parse_expression()
                    if peek()['type'] == 'COMMA':
                        # Parse as array without brackets
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
                        skip_newlines()
                else:
                    skip_newlines()
            else:
                # Unexpected token in container body - skip it to recover
                consume()
                skip_newlines()
        
        if peek()['type'] == 'DEDENT':
            consume('DEDENT')
        
        return container
    
    ast = {'imports': [], 'variables': {}, 'functions': {}, 'containers': {}, 'main_container': None}
    
    skip_newlines()
    
    while peek()['type'] != 'EOF':
        token = peek()
        
        if token['type'] == 'KEYWORD' and token['value'] == 'from':
            consume()
            path = consume('STRING')
            consume('KEYWORD')
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
            ast['imports'].append({'source': path['value'], 'items': items})
            skip_newlines()
        
        elif token['type'] == 'KEYWORD' and token['value'] == 'import':
            consume()
            path = consume('STRING')
            ast['imports'].append({'source': path['value'], 'items': '*'})
            skip_newlines()
        
        elif token['type'] == 'IDENTIFIER':
            name = consume()['value']
            
            if peek()['type'] == 'ASSIGN':
                consume()
                value = parse_expression()
                ast['variables'][name] = {'value': value}
                skip_newlines()
            
            elif peek()['type'] == 'LPAREN':
                consume()
                params = []
                while peek()['type'] != 'RPAREN':
                    if peek()['type'] != 'IDENTIFIER':
                        raise SyntaxError(f"Function '{name}' definition expects parameter names (identifiers), but got {peek()['type']} at line {peek()['line']}. If this is a function call inside a container, check your indentation.")
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
                while peek()['type'] not in ['DEDENT', 'EOF']:
                    if peek()['type'] == 'NEWLINE':
                        skip_newlines()
                        continue
                    
                    stmt_token = peek()
                    
                    if stmt_token['type'] == 'KEYWORD' and stmt_token['value'] == 'return':
                        consume()
                        ret_value = parse_expression()
                        body.append({'type': 'return', 'value': ret_value})
                        skip_newlines()
                    
                    elif stmt_token['type'] == 'KEYWORD' and stmt_token['value'] == 'if':
                        consume()
                        if peek()['type'] == 'LPAREN':
                            consume('LPAREN')
                        condition = parse_expression()
                        if peek()['type'] == 'RPAREN':
                            consume('RPAREN')
                        consume('COLON')
                        skip_newlines()
                        consume('INDENT')
                        then_body = []
                        while peek()['type'] not in ['DEDENT', 'EOF']:
                            if peek()['type'] == 'NEWLINE':
                                skip_newlines()
                                continue
                            
                            # Handle nested if statements
                            if peek()['type'] == 'KEYWORD' and peek()['value'] == 'if':
                                consume()
                                if peek()['type'] == 'LPAREN':
                                    consume('LPAREN')
                                nested_cond = parse_expression()
                                if peek()['type'] == 'RPAREN':
                                    consume('RPAREN')
                                consume('COLON')
                                skip_newlines()
                                consume('INDENT')
                                nested_then = []
                                while peek()['type'] not in ['DEDENT', 'EOF']:
                                    if peek()['type'] == 'NEWLINE':
                                        skip_newlines()
                                        continue
                                    if peek()['type'] == 'IDENTIFIER' and peek(1)['type'] == 'COLON':
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
                                        nested_then.append({'type': 'modify_container', 'target': {'type': 'var', 'name': target_name}, 'attributes': mod_attrs})
                                    else:
                                        expr = parse_expression()
                                        if peek()['type'] == 'ASSIGN':
                                            consume()
                                            val = parse_expression()
                                            nested_then.append({'type': 'assign', 'target': expr, 'value': val})
                                        else:
                                            nested_then.append({'type': 'expr_stmt', 'expr': expr})
                                    skip_newlines()
                                consume('DEDENT')
                                nested_else = []
                                if peek()['type'] == 'KEYWORD' and peek()['value'] == 'else':
                                    consume()
                                    consume('COLON')
                                    skip_newlines()
                                    consume('INDENT')
                                    while peek()['type'] not in ['DEDENT', 'EOF']:
                                        if peek()['type'] == 'NEWLINE':
                                            skip_newlines()
                                            continue
                                        expr = parse_expression()
                                        if peek()['type'] == 'ASSIGN':
                                            consume()
                                            val = parse_expression()
                                            nested_else.append({'type': 'assign', 'target': expr, 'value': val})
                                        else:
                                            nested_else.append({'type': 'expr_stmt', 'expr': expr})
                                        skip_newlines()
                                    consume('DEDENT')
                                then_body.append({'type': 'if', 'condition': nested_cond, 'then': nested_then, 'else': nested_else})
                                skip_newlines()
                                continue
                            
                            # Handle nested for loops
                            if peek()['type'] == 'KEYWORD' and peek()['value'] == 'for':
                                consume()
                                loop_var = consume('IDENTIFIER')['value']
                                consume('KEYWORD')  # 'in'
                                loop_iter = parse_expression()
                                consume('COLON')
                                skip_newlines()
                                consume('INDENT')
                                loop_body = []
                                while peek()['type'] not in ['DEDENT', 'EOF']:
                                    if peek()['type'] == 'NEWLINE':
                                        skip_newlines()
                                        continue
                                    if peek()['type'] == 'IDENTIFIER' and peek(1)['type'] == 'COLON':
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
                                        loop_body.append({'type': 'modify_container', 'target': {'type': 'var', 'name': target_name}, 'attributes': mod_attrs})
                                    else:
                                        expr = parse_expression()
                                        if peek()['type'] == 'ASSIGN':
                                            consume()
                                            val = parse_expression()
                                            loop_body.append({'type': 'assign', 'target': expr, 'value': val})
                                        else:
                                            loop_body.append({'type': 'expr_stmt', 'expr': expr})
                                    skip_newlines()
                                consume('DEDENT')
                                then_body.append({'type': 'for', 'var': loop_var, 'iterable': loop_iter, 'body': loop_body})
                                skip_newlines()
                                continue
                            
                            if peek()['type'] == 'IDENTIFIER' and peek(1)['type'] == 'COLON':
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
                                then_body.append({'type': 'modify_container', 'target': {'type': 'var', 'name': target_name}, 'attributes': mod_attrs})
                            else:
                                target_expr = parse_expression()
                                if peek()['type'] == 'ASSIGN':
                                    consume()
                                    value_expr = parse_expression()
                                    then_body.append({'type': 'assign', 'target': target_expr, 'value': value_expr})
                                else:
                                    then_body.append({'type': 'expr_stmt', 'expr': target_expr})
                            skip_newlines()
                        consume('DEDENT')
                        
                        else_body = []
                        if peek()['type'] == 'KEYWORD' and peek()['value'] == 'else':
                            consume()
                            consume('COLON')
                            skip_newlines()
                            consume('INDENT')
                            while peek()['type'] not in ['DEDENT', 'EOF']:
                                if peek()['type'] == 'NEWLINE':
                                    skip_newlines()
                                    continue
                                target_expr = parse_expression()
                                if peek()['type'] == 'ASSIGN':
                                    consume()
                                    value_expr = parse_expression()
                                    else_body.append({'type': 'assign', 'target': target_expr, 'value': value_expr})
                                else:
                                    else_body.append({'type': 'expr_stmt', 'expr': target_expr})
                                skip_newlines()
                            consume('DEDENT')
                        
                        body.append({'type': 'if', 'condition': condition, 'then': then_body, 'else': else_body})
                        skip_newlines()
                    
                    elif stmt_token['type'] == 'KEYWORD' and stmt_token['value'] == 'for':
                        consume()
                        var_name = consume('IDENTIFIER')['value']
                        consume('KEYWORD')
                        iterable = parse_expression()
                        consume('COLON')
                        skip_newlines()
                        consume('INDENT')
                        for_body = []
                        while peek()['type'] not in ['DEDENT', 'EOF']:
                            if peek()['type'] == 'NEWLINE':
                                skip_newlines()
                                continue
                            
                            # Handle nested if statements
                            if peek()['type'] == 'KEYWORD' and peek()['value'] == 'if':
                                consume()
                                if peek()['type'] == 'LPAREN':
                                    consume('LPAREN')
                                nested_cond = parse_expression()
                                if peek()['type'] == 'RPAREN':
                                    consume('RPAREN')
                                consume('COLON')
                                skip_newlines()
                                consume('INDENT')
                                nested_then = []
                                while peek()['type'] not in ['DEDENT', 'EOF']:
                                    if peek()['type'] == 'NEWLINE':
                                        skip_newlines()
                                        continue
                                    if peek()['type'] == 'IDENTIFIER' and peek(1)['type'] == 'COLON':
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
                                        nested_then.append({'type': 'modify_container', 'target': {'type': 'var', 'name': target_name}, 'attributes': mod_attrs})
                                    else:
                                        expr = parse_expression()
                                        if peek()['type'] == 'ASSIGN':
                                            consume()
                                            val = parse_expression()
                                            nested_then.append({'type': 'assign', 'target': expr, 'value': val})
                                        else:
                                            nested_then.append({'type': 'expr_stmt', 'expr': expr})
                                    skip_newlines()
                                consume('DEDENT')
                                nested_else = []
                                if peek()['type'] == 'KEYWORD' and peek()['value'] == 'else':
                                    consume()
                                    consume('COLON')
                                    skip_newlines()
                                    consume('INDENT')
                                    while peek()['type'] not in ['DEDENT', 'EOF']:
                                        if peek()['type'] == 'NEWLINE':
                                            skip_newlines()
                                            continue
                                        expr = parse_expression()
                                        if peek()['type'] == 'ASSIGN':
                                            consume()
                                            val = parse_expression()
                                            nested_else.append({'type': 'assign', 'target': expr, 'value': val})
                                        else:
                                            nested_else.append({'type': 'expr_stmt', 'expr': expr})
                                        skip_newlines()
                                    consume('DEDENT')
                                for_body.append({'type': 'if', 'condition': nested_cond, 'then': nested_then, 'else': nested_else})
                                skip_newlines()
                                continue
                            
                            # Handle nested for loops
                            if peek()['type'] == 'KEYWORD' and peek()['value'] == 'for':
                                consume()
                                loop_var = consume('IDENTIFIER')['value']
                                consume('KEYWORD')  # 'in'
                                loop_iter = parse_expression()
                                consume('COLON')
                                skip_newlines()
                                consume('INDENT')
                                inner_body = []
                                while peek()['type'] not in ['DEDENT', 'EOF']:
                                    if peek()['type'] == 'NEWLINE':
                                        skip_newlines()
                                        continue
                                    if peek()['type'] == 'IDENTIFIER' and peek(1)['type'] == 'COLON':
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
                                        inner_body.append({'type': 'modify_container', 'target': {'type': 'var', 'name': target_name}, 'attributes': mod_attrs})
                                    else:
                                        expr = parse_expression()
                                        if peek()['type'] == 'ASSIGN':
                                            consume()
                                            val = parse_expression()
                                            inner_body.append({'type': 'assign', 'target': expr, 'value': val})
                                        else:
                                            inner_body.append({'type': 'expr_stmt', 'expr': expr})
                                    skip_newlines()
                                consume('DEDENT')
                                for_body.append({'type': 'for', 'var': loop_var, 'iterable': loop_iter, 'body': inner_body})
                                skip_newlines()
                                continue
                            
                            if peek()['type'] == 'IDENTIFIER' and peek(1)['type'] == 'COLON':
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
                                for_body.append({'type': 'modify_container', 'target': {'type': 'var', 'name': target_name}, 'attributes': mod_attrs})
                            else:
                                target_expr = parse_expression()
                                if peek()['type'] == 'ASSIGN':
                                    consume()
                                    value_expr = parse_expression()
                                    for_body.append({'type': 'assign', 'target': target_expr, 'value': value_expr})
                                else:
                                    for_body.append({'type': 'expr_stmt', 'expr': target_expr})
                            skip_newlines()
                        consume('DEDENT')
                        body.append({'type': 'for', 'var': var_name, 'iterable': iterable, 'body': for_body})
                        skip_newlines()
                    
                    else:
                        target_expr = parse_expression()
                        if peek()['type'] == 'ASSIGN':
                            consume()
                            value_expr = parse_expression()
                            body.append({'type': 'assign', 'target': target_expr, 'value': value_expr})
                        else:
                            body.append({'type': 'expr_stmt', 'expr': target_expr})
                        skip_newlines()
                
                consume('DEDENT')
                ast['functions'][name] = {'params': params, 'body': body}
            
            elif peek()['type'] == 'COLON':
                consume()
                skip_newlines()
                
                is_main = False
                container = parse_container_body()
                ast['containers'][name] = container
            else:
                skip_newlines()
        
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
    """Resolve imports and merge ASTs"""
    if not ast['imports']:
        return ast
    
    for import_node in ast['imports']:
        source = import_node['source']
        items = import_node['items']
        
        file_path = source.replace('\\', os.sep)
        if not os.path.isabs(file_path):
            file_path = os.path.join(base_path, file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tokens = tokenize(code)
            imported_ast = parse(tokens)
            import_base = os.path.dirname(file_path)
            imported_ast = resolve_imports(imported_ast, import_base)
            
            if items == '*':
                ast['variables'].update(imported_ast['variables'])
                ast['functions'].update(imported_ast['functions'])
                ast['containers'].update(imported_ast['containers'])
            else:
                for item in items:
                    if item in imported_ast['variables']:
                        ast['variables'][item] = imported_ast['variables'][item]
                    elif item in imported_ast['functions']:
                        ast['functions'][item] = imported_ast['functions'][item]
                    elif item in imported_ast['containers']:
                        ast['containers'][item] = imported_ast['containers'][item]
        except:
            pass
    
    ast['imports'] = []
    return ast


# ============================================================================
# CODE GENERATOR
# ============================================================================

def resolve_color(color_expr: Any) -> Optional[int]:
    """Resolve color to ARGB integer"""
    if isinstance(color_expr, dict):
        if color_expr.get('type') == 'var':
            color_name = color_expr['name']
            if color_name in MATERIAL_COLORS:
                return MATERIAL_COLORS[color_name][500]
        return None
    return None


def resolve_dimension(dim_expr: Any) -> Dict:
    """Resolve dimension to runtime format"""
    if isinstance(dim_expr, dict):
        if dim_expr.get('type') == 'literal':
            if dim_expr.get('value_type') == 'number':
                return {"type": "fixed", "value": dim_expr['value']}
            elif dim_expr.get('value_type') == 'string' and dim_expr['value'] == 'max':
                return {"type": "infinity"}
        if dim_expr.get('type') == 'var' and dim_expr['name'] == 'max':
            return {"type": "infinity"}
        return {"type": "expression", "expr": compile_expression(dim_expr)}
    return {"type": "auto"}


def extract_text_bindings(text: str) -> List[str]:
    """Extract variable bindings from text"""
    bindings = []
    pattern = r'(?<!\{)\{([^{}]+)\}(?!\})'
    matches = re.findall(pattern, text)
    for match in matches:
        root = match.split('.')[0].split('[')[0].strip()
        if root not in bindings:
            bindings.append(root)
    return bindings


def compile_expression(expr: Any) -> Dict:
    """Compile expression to runtime format"""
    if not isinstance(expr, dict):
        return {"type": "literal", "value": expr}
    
    expr_type = expr.get('type')
    
    if expr_type == 'literal':
        return {"type": "literal", "value": expr['value'], "value_type": expr['value_type']}
    elif expr_type == 'var':
        return {"type": "var", "name": expr['name']}
    elif expr_type == 'binary_op':
        return {"type": "binary_op", "op": expr['op'], "left": compile_expression(expr['left']), "right": compile_expression(expr['right'])}
    elif expr_type == 'unary_op':
        return {"type": "unary_op", "op": expr['op'], "operand": compile_expression(expr['operand'])}
    elif expr_type == 'member':
        return {"type": "member", "object": compile_expression(expr['object']), "field": expr['field']}
    elif expr_type == 'index':
        return {"type": "index", "object": compile_expression(expr['object']), "index": compile_expression(expr['index'])}
    elif expr_type == 'call':
        return {"type": "call", "function": compile_expression(expr['function']), "args": [compile_expression(arg) for arg in expr.get('args', [])]}
    elif expr_type == 'method_call':
        return {"type": "method_call", "object": compile_expression(expr['object']), "method": expr['method'], "args": [compile_expression(arg) for arg in expr.get('args', [])]}
    elif expr_type == 'ternary':
        return {"type": "ternary", "condition": compile_expression(expr['condition']), "then": compile_expression(expr['then']), "else": compile_expression(expr['else'])}
    elif expr_type == 'array':
        return {"type": "array", "elements": [compile_expression(elem) for elem in expr.get('elements', [])]}
    elif expr_type == 'kvpair':
        return {"type": "kvpair", "key": expr['key'], "value": compile_expression(expr['value'])}
    elif expr_type == 'object':
        return {"type": "object", "properties": {k: compile_expression(v) for k, v in expr.get('properties', {}).items()}}
    
    return expr


def compile_statement(stmt: Dict) -> Dict:
    """Compile statement to runtime format"""
    stmt_type = stmt.get('type')
    
    if stmt_type == 'assign':
        return {"type": "assign", "target": compile_expression(stmt['target']), "value": compile_expression(stmt['value'])}
    elif stmt_type == 'return':
        return {"type": "return", "value": compile_expression(stmt['value'])}
    elif stmt_type == 'if':
        return {"type": "if", "condition": compile_expression(stmt['condition']), 
                "then": [compile_statement(s) for s in stmt['then']], 
                "else": [compile_statement(s) for s in stmt['else']] if stmt.get('else') else []}
    elif stmt_type == 'for':
        return {"type": "for", "var": stmt['var'], "iterable": compile_expression(stmt['iterable']), "body": [compile_statement(s) for s in stmt['body']]}
    elif stmt_type == 'expr_stmt':
        return {"type": "expr_stmt", "expr": compile_expression(stmt['expr'])}
    elif stmt_type == 'modify_container':
        return {"type": "modify_container", "target": compile_expression(stmt['target']), "attributes": {k: compile_expression(v) for k, v in stmt['attributes'].items()}}
    
    return stmt


# Type requirements mapping
TYPE_REQUIREMENTS = {
    'button': {
        'required': ['text_content'],
        'description': 'Interactive button component',
        'example': '''button_name:
  type = button
  text_content = "Click Me"
  color = blue
  on_click: handle_click()'''
    },
    'input': {
        'required': ['placeholder'],
        'description': 'Text input field',
        'example': '''input_name:
  type = input
  placeholder = "Enter your name..."
  width = 80'''
    },
    'icon': {
        'required': ['icon'],
        'description': 'Icon display component',
        'example': '''icon_name:
  type = icon
  icon = "check_circle"
  color = green'''
    },
    'search_bar': {
        'required': ['placeholder'],
        'description': 'Search input component',
        'example': '''search_name:
  type = search_bar
  placeholder = "Search..."
  width = max'''
    },
    'link': {
        'required': ['text_content'],
        'description': 'Clickable link component',
        'example': '''link_name:
  type = link
  text_content = "Visit Website"
  on_click: visit("https://example.com")'''
    }
}

def validate_type_requirements(container_name: str, component_type: str, attrs: Dict) -> None:
    """Validate that required attributes for a type are present"""
    if component_type not in TYPE_REQUIREMENTS:
        return  # Unknown type, let it pass (could be custom or future type)
    
    requirements = TYPE_REQUIREMENTS[component_type]
    missing = []
    
    for req_attr in requirements['required']:
        if req_attr not in attrs:
            missing.append(req_attr)
    
    if missing:
        missing_list = '\n  • '.join(missing)
        error_msg = f"""Container '{container_name}' has type='{component_type}' but is missing required attributes:

Required attributes missing:
  • {missing_list}

Description: {requirements['description']}

Example usage:
{requirements['example']}
"""
        raise SyntaxError(error_msg)

def generate_widget(name: str, container: Dict, ast: Dict, context: Optional[Dict] = None) -> Dict:
    """Generate widget from container"""
    attrs = container['attributes']
    
    if 'repeat_by' in attrs:
        return expand_repeat_by(name, container, ast)
    
    widget_type = "Container"
    component_type = None
    
    if 'type' in attrs:
        type_val = attrs['type']
        if isinstance(type_val, dict) and type_val.get('type') == 'literal':
            component_type = type_val['value']
            
            # Validate required attributes for this type
            validate_type_requirements(name, component_type, attrs)
            
            if component_type == 'button':
                widget_type = "ElevatedButton"
            elif component_type == 'input':
                widget_type = "TextField"
            elif component_type == 'icon':
                widget_type = "Icon"
            elif component_type == 'search_bar':
                widget_type = "SearchBar"
            elif component_type == 'link':
                widget_type = "InkWell"  # Clickable link
            elif component_type == 'scroller':
                widget_type = "SingleChildScrollView"
    
    if attrs.get('scrollable'):
        if isinstance(attrs['scrollable'], dict) and attrs['scrollable'].get('value'):
            widget_type = "ListView"
    
    if 'children' in attrs or container.get('children_def'):
        widget_type = "Column"
    
    widget = {"name": name, "widget": widget_type, "props": {}}
    
    if 'width' in attrs:
        widget['props']['width'] = resolve_dimension(attrs['width'])
    if 'height' in attrs:
        widget['props']['height'] = resolve_dimension(attrs['height'])
    
    if 'color' in attrs:
        color_expr = attrs['color']
        if isinstance(color_expr, dict) and color_expr.get('type') == 'index':
            obj = color_expr['object']
            idx = color_expr['index']
            if obj.get('type') == 'var' and idx.get('type') == 'literal' and idx.get('value_type') == 'number':
                color_name = obj['name']
                shade = int(idx['value'])
                if color_name in MATERIAL_COLORS and shade in MATERIAL_COLORS[color_name]:
                    widget['props']['color'] = MATERIAL_COLORS[color_name][shade]
        else:
            color_val = resolve_color(color_expr)
            if color_val is not None:
                widget['props']['color'] = color_val
            else:
                widget['props']['color_expr'] = compile_expression(color_expr)
    
    if 'text_content' in attrs:
        text_expr = attrs['text_content']
        if isinstance(text_expr, dict) and text_expr.get('type') == 'literal':
            text_val = text_expr['value']
            widget['props']['text'] = text_val
            bindings = extract_text_bindings(text_val)
            if bindings:
                widget['props']['text_bindings'] = bindings
        else:
            widget['props']['text_expr'] = compile_expression(text_expr)
    
    for attr_name, attr_value in attrs.items():
        if attr_name in ['width', 'height', 'color', 'text_content', 'children', 'repeat_by', 'type']:
            continue
        
        if attr_name.startswith('on_'):
            if 'events' not in widget['props']:
                widget['props']['events'] = {}
            widget['props']['events'][attr_name] = compile_expression(attr_value)
        else:
            widget['props'][attr_name] = compile_expression(attr_value)
    
    children = []
    if 'children' in attrs:
        children_expr = attrs['children']
        if isinstance(children_expr, dict) and children_expr.get('type') == 'array':
            for elem in children_expr['elements']:
                if elem.get('type') == 'var':
                    child_name = elem['name']
                    if child_name in ast['containers']:
                        children.append(generate_widget(child_name, ast['containers'][child_name], ast, context))
                elif elem.get('type') == 'call':
                    func_name = elem['function'].get('name')
                    if func_name in ast['containers']:
                        template = ast['containers'][func_name]
                        child_widget = generate_widget(func_name, template, ast, context)
                        child_widget['param_bindings'] = {
                            template.get('params', [])[i] if i < len(template.get('params', [])) else f"arg{i}": compile_expression(elem['args'][i])
                            for i in range(len(elem.get('args', [])))
                        }
                        children.append(child_widget)
                elif elem.get('type') == 'member':
                    obj_name = elem['object']['name']
                    field_name = elem['field']
                    if obj_name in ast['containers']:
                        parent_container = ast['containers'][obj_name]
                        for nested in parent_container.get('children_def', []):
                            if nested['name'] == field_name:
                                children.append(generate_widget(f"{obj_name}.{field_name}", nested, ast, context))
                                break
    
    if container.get('children_def'):
        for child_def in container['children_def']:
            children.append(generate_widget(child_def['name'], child_def, ast, context))
    
    if children:
        widget['children'] = children
    
    return widget


def expand_repeat_by(name: str, container: Dict, ast: Dict) -> Dict:
    """Expand repeat_by into multiple widgets"""
    repeat_expr = container['attributes']['repeat_by']
    
    if repeat_expr.get('type') != 'array':
        return generate_widget(name, container, ast)
    
    dimensions = []
    for elem in repeat_expr['elements']:
        if elem.get('type') == 'literal' and elem.get('value_type') == 'number':
            dimensions.append(int(elem['value']))
        elif elem.get('type') == 'call':
            dimensions.append(compile_expression(elem))
    
    if len(dimensions) not in [2, 3]:
        return generate_widget(name, container, ast)
    
    widgets = []
    
    if len(dimensions) == 2:
        if all(isinstance(d, int) for d in dimensions):
            rows, cols = dimensions
            for x in range(cols):
                for y in range(rows):
                    instance_container = {'attributes': {**container['attributes']}, 'children_def': container.get('children_def', [])}
                    del instance_container['attributes']['repeat_by']
                    instance_widget = generate_widget(f"{name}_X{x}Y{y}", instance_container, ast)
                    instance_widget['repeat_index'] = {'x': x, 'y': y}
                    widgets.append(instance_widget)
        else:
            return {
                "name": name, 
                "widget": "DynamicRepeated", 
                "repeat_expr": [compile_expression(d) if isinstance(d, dict) else {"type": "literal", "value": d, "value_type": "number"} for d in dimensions],
                "template": generate_widget(f"{name}_template", {'attributes': {k: v for k, v in container['attributes'].items() if k != 'repeat_by'}, 'children_def': container.get('children_def', [])}, ast)
            }
    else:
        if all(isinstance(d, int) for d in dimensions):
            cols, rows, depth = dimensions
            for x in range(cols):
                for y in range(rows):
                    for z in range(depth):
                        instance_container = {'attributes': {**container['attributes']}, 'children_def': container.get('children_def', [])}
                        del instance_container['attributes']['repeat_by']
                        instance_widget = generate_widget(f"{name}_X{x}Y{y}Z{z}", instance_container, ast)
                        instance_widget['repeat_index'] = {'x': x, 'y': y, 'z': z}
                        widgets.append(instance_widget)
        else:
            return {
                "name": name,
                "widget": "DynamicRepeated",
                "repeat_expr": [compile_expression(d) if isinstance(d, dict) else {"type": "literal", "value": d, "value_type": "number"} for d in dimensions],
                "template": generate_widget(f"{name}_template", {'attributes': {k: v for k, v in container['attributes'].items() if k != 'repeat_by'}, 'children_def': container.get('children_def', [])}, ast)
            }
    
    return {"name": name, "widget": "Repeated", "instances": widgets}


def generate(ast: Dict) -> Dict:
    """Generate final JSON output"""
    output = {
        "state": {var_name: {"initial": compile_expression(var_node['value'])} for var_name, var_node in ast['variables'].items()},
        "functions": {func_name: {"params": func_node['params'], "body": [compile_statement(stmt) for stmt in func_node['body']]} for func_name, func_node in ast['functions'].items()},
        "tree": generate_widget(ast['main_container'], ast['containers'][ast['main_container']], ast) if ast['main_container'] else None
    }
    return output


# ============================================================================
# MAIN COMPILER
# ============================================================================

class Parser:
    """Vi Language Parser"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.tree = None
    
    def parse(self):
        """Parse .vi file to JSON"""
        print(f"Compiling '{self.filepath}'...")
        
        with open(self.filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tokens = tokenize(source)
        ast = parse(tokens)
        
        base_path = os.path.dirname(os.path.abspath(self.filepath))
        ast = resolve_imports(ast, base_path)
        
        self.tree = generate(ast)
        
        print(f"✓ Compilation complete!")
        return self.tree
