"""
Vi to Dart Code Generator - With State Lifting
Generates Flutter/Dart code directly from AST
Automatically handles modify_container by lifting state
"""

import re


class DartCodegen:
    """Generates complete Flutter app from Vi AST with automatic state lifting"""

    def __init__(self, ast):
        self.ast = ast
        self.modified_containers = {}   # {container_name: {property: True}}
        self.repeated_containers = {}   # {container_name: (rows, cols, count)}
        self.param_container_map = {}   # {func_name: {param_name: container_name}}
        self.current_func = None        # function currently being generated
        self.local_vars_declared = {}   # {func_name: set(var_names)} — tracks first-use declarations
        self.cell_var_map = {}          # {var_name: (container_name, index_var)} — for-loop cell vars
        self.in_repeat_context = False  # True when generating code inside a repeated widget
        self.analyze()

    # =========================================================================
    # ANALYSIS
    # =========================================================================

    def analyze(self):
        """Full analysis pass: repeated containers → param map → modifications"""

        # 1. Find repeated containers
        for name, container in self.ast['containers'].items():
            repeat_expr = container['attributes'].get('repeat_by')
            if repeat_expr and repeat_expr.get('type') == 'array':
                dims = [
                    int(e['value']) for e in repeat_expr['elements']
                    if e.get('type') == 'literal' and e.get('value_type') == 'number'
                ]
                if len(dims) == 2:
                    rows, cols = dims
                    self.repeated_containers[name] = (rows, cols, rows * cols)

        # 2. Build param → container map from event handlers on repeated containers
        for cname, container in self.ast['containers'].items():
            if cname not in self.repeated_containers:
                continue
            on_click = container['attributes'].get('on_click')
            if on_click and on_click.get('type') == 'call':
                func_ref = on_click.get('function', {})
                func_name = func_ref.get('name') if func_ref.get('type') == 'var' else None
                if func_name and func_name in self.ast['functions']:
                    params = self.ast['functions'][func_name]['params']
                    if params:
                        self.param_container_map.setdefault(func_name, {})[params[0]] = cname

        # 3. Scan functions for modify_container to determine which state lists are needed
        def scan(stmts, func_name):
            for stmt in stmts:
                if stmt.get('type') == 'modify_container':
                    target = stmt['target']
                    cname = None
                    if target.get('type') == 'var':
                        var = target['name']
                        # resolve via param map
                        cname = self.param_container_map.get(func_name, {}).get(var, var)
                    elif target.get('type') == 'member':
                        cname = self._base_name(target)
                    if cname:
                        self.modified_containers.setdefault(cname, {})
                        for attr in stmt['attributes']:
                            self.modified_containers[cname][attr] = True
                for child_key in ('then', 'else', 'body'):
                    scan(stmt.get(child_key, []), func_name)

        for fname, fnode in self.ast['functions'].items():
            scan(fnode['body'], fname)

        # 4. Build call graph — functions called by other functions should not wrap in setState
        self.called_by_functions = set()
        def find_calls(stmts, current_fname):
            for stmt in stmts:
                if stmt.get('type') == 'expr_stmt':
                    expr = stmt.get('expr', {})
                    if expr.get('type') == 'call':
                        fname = expr.get('function', {}).get('name')
                        if fname and fname in self.ast['functions'] and fname != current_fname:
                            self.called_by_functions.add(fname)
                for key in ('then', 'else', 'body'):
                    find_calls(stmt.get(key, []), current_fname)
        for fname, fnode in self.ast['functions'].items():
            find_calls(fnode['body'], fname)

    def _base_name(self, expr):
        """Walk member-access chain to get the root var name"""
        while expr.get('type') == 'member':
            expr = expr['object']
        return expr.get('name') if expr.get('type') == 'var' else None

    # =========================================================================
    # TOP-LEVEL CODE GENERATION
    # =========================================================================

    def generate_full_app(self):
        parts = [
            "import 'package:flutter/material.dart';",
            "import 'dart:math';",
            "",
            "void main() {",
            "  runApp(const MaterialApp(",
            "    home: ViApp(),",
            "    debugShowCheckedModeBanner: false,",
            "  ));",
            "}",
            "",
        ]
        parts.extend(self.generate_app_widget())
        return "\n".join(parts)

    def generate_app_widget(self):
        lines = []

        lines += [
            "class ViApp extends StatefulWidget {",
            "  const ViApp({super.key});",
            "",
            "  @override",
            "  State<ViApp> createState() => _ViAppState();",
            "}",
            "",
            "class _ViAppState extends State<ViApp> {",
        ]

        # Global state variables
        for vname, vnode in self.ast['variables'].items():
            vtype = self.infer_type(vnode['value'])
            init = self.generate_expr(vnode['value'])
            lines.append(f"  {vtype} {vname} = {init};")
        if self.ast['variables']:
            lines.append("")

        # State lists for modified repeated containers
        for cname, (rows, cols, count) in self.repeated_containers.items():
            if cname in self.modified_containers:
                for prop in self.modified_containers[cname]:
                    dtype = self._list_elem_type(prop)
                    default = self._list_default(prop)
                    lines.append(f"  List<{dtype}> {cname}_{prop} = List.filled({count}, {default}, growable: false);")
                lines.append("")

        # Functions
        for fname, fnode in self.ast['functions'].items():
            lines.extend(self.generate_function(fname, fnode))
            lines.append("")

        # build()
        lines += ["  @override", "  Widget build(BuildContext context) {"]
        if self.ast['main_container']:
            mn = self.ast['main_container']
            widget = self.generate_widget(mn, self.ast['containers'][mn], indent=2)
            lines += [
                "    return Scaffold(",
                "      body: SafeArea(",
                f"        child: {widget},",
                "      ),",
                "    );",
            ]
        else:
            lines.append("    return Scaffold(body: Center(child: Text('No main container')));")
        lines += ["  }", "}"]

        return lines

    def _list_elem_type(self, prop):
        return {'text_content': 'String', 'visibility': 'bool', 'color': 'Color?', 'text_content_style': 'TextStyle?'}.get(prop, 'dynamic')

    def _list_default(self, prop):
        return {'text_content': '""', 'visibility': 'true', 'color': 'null', 'text_content_style': 'null'}.get(prop, 'null')

    # =========================================================================
    # FUNCTION GENERATION
    # =========================================================================

    def generate_function(self, func_name, func_node):
        lines = []
        params = func_node['params']

        prev_func = self.current_func
        self.current_func = func_name
        self.local_vars_declared[func_name] = set()

        # Use typed params: int for cell params, dynamic otherwise
        param_strs = []
        for p in params:
            if func_name in self.param_container_map and p in self.param_container_map[func_name]:
                param_strs.append(f"int {p}")
            else:
                param_strs.append(f"dynamic {p}")
        param_str = ", ".join(param_strs)

        has_state = self._has_state_changes(func_node['body'])
        is_internal = func_name in self.called_by_functions
        is_async = self._has_async_calls(func_node['body'])
        func_type = "Future<void>" if is_async else "void"

        lines.append(f"  {func_type} {func_name}({param_str}) {'async ' if is_async else ''}{{")
        if has_state and not is_internal:
            lines.append("    setState(() {")
            for stmt in func_node['body']:
                lines.extend(self.generate_statement(stmt, indent=3))
            lines.append("    });")
        else:
            for stmt in func_node['body']:
                lines.extend(self.generate_statement(stmt, indent=2))
        lines.append("  }")

        self.current_func = prev_func
        return lines

    def _has_state_changes(self, stmts):
        for stmt in stmts:
            if stmt.get('type') in ('assign', 'modify_container'):
                return True
            for key in ('then', 'else', 'body'):
                if self._has_state_changes(stmt.get(key, [])):
                    return True
        return False
    
    def _has_async_calls(self, stmts):
        """Check if function body contains wait_sec calls"""
        for stmt in stmts:
            if stmt.get('type') == 'expr_stmt':
                if self._expr_has_wait(stmt.get('expr')):
                    return True
            for key in ('then', 'else', 'body', 'value'):
                if isinstance(stmt.get(key), list):
                    if self._has_async_calls(stmt.get(key, [])):
                        return True
        return False
    
    def _expr_has_wait(self, expr):
        """Check if expression contains wait_sec call"""
        if not isinstance(expr, dict):
            return False
        if expr.get('type') == 'call':
            func = expr.get('function', {})
            if func.get('type') == 'var' and func.get('name') == 'wait_sec':
                return True
        for key in ('left', 'right', 'operand', 'object', 'function', 'condition', 'then', 'else'):
            val = expr.get(key)
            if isinstance(val, dict) and self._expr_has_wait(val):
                return True
        if 'args' in expr:
            for arg in expr.get('args', []):
                if self._expr_has_wait(arg):
                    return True
        return False

    # =========================================================================
    # STATEMENT GENERATION
    # =========================================================================

    def generate_statement(self, stmt, indent=0):
        ind = "  " * indent
        lines = []
        t = stmt.get('type')

        if t == 'assign':
            target_expr = stmt['target']
            value = self.generate_expr(stmt['value'])

            if target_expr.get('type') == 'var':
                vname = target_expr['name']
                is_global = vname in self.ast['variables']
                func_params = self.ast['functions'].get(self.current_func, {}).get('params', [])
                is_param = vname in func_params
                declared = self.local_vars_declared.get(self.current_func, set())

                if not is_global and not is_param and vname not in declared:
                    dtype = self.infer_type(stmt['value'])
                    lines.append(f"{ind}{dtype} {vname} = {value};")
                    declared.add(vname)
                    self.local_vars_declared[self.current_func] = declared
                    return lines

            target = self.generate_expr(target_expr)
            lines.append(f"{ind}{target} = {value};")

        elif t == 'expr_stmt':
            lines.append(f"{ind}{self.generate_expr(stmt['expr'])};")

        elif t == 'return':
            lines.append(f"{ind}return {self.generate_expr(stmt['value'])};")

        elif t == 'if':
            cond = self.generate_expr(stmt['condition'])
            lines.append(f"{ind}if ({cond}) {{")
            for s in stmt['then']:
                lines.extend(self.generate_statement(s, indent + 1))
            if stmt.get('else'):
                lines.append(f"{ind}}} else {{")
                for s in stmt['else']:
                    lines.extend(self.generate_statement(s, indent + 1))
            lines.append(f"{ind}}}")

        elif t == 'for':
            var_name = stmt['var']
            iterable_expr = stmt['iterable']

            # Special case: for x in container.children
            if (iterable_expr.get('type') == 'member'
                    and iterable_expr['field'] == 'children'
                    and iterable_expr['object'].get('type') == 'var'):
                cname = iterable_expr['object']['name']
                if cname in self.repeated_containers:
                    _, _, count = self.repeated_containers[cname]
                    idx_var = f"{var_name}Idx"
                    lines.append(f"{ind}for (int {idx_var} = 0; {idx_var} < {count}; {idx_var}++) {{")
                    # Register var → (container, index_var) for body generation
                    prev = self.cell_var_map.get(var_name)
                    self.cell_var_map[var_name] = (cname, idx_var)
                    for s in stmt['body']:
                        lines.extend(self.generate_statement(s, indent + 1))
                    # Restore
                    if prev is None:
                        self.cell_var_map.pop(var_name, None)
                    else:
                        self.cell_var_map[var_name] = prev
                    lines.append(f"{ind}}}")
                    return lines

            # Regular for loop
            iterable = self.generate_expr(iterable_expr)
            lines.append(f"{ind}for (var {var_name} in {iterable}) {{")
            for s in stmt['body']:
                lines.extend(self.generate_statement(s, indent + 1))
            lines.append(f"{ind}}}")

        elif t == 'modify_container':
            target = stmt['target']

            if target.get('type') == 'var':
                vname = target['name']

                # Check for-loop cell var
                if vname in self.cell_var_map:
                    cname, idx_var = self.cell_var_map[vname]
                    for attr, val_expr in stmt['attributes'].items():
                        # Special handling for text_content_style - convert to TextStyle
                        if attr == 'text_content_style' and val_expr.get('type') == 'array':
                            val = self._generate_text_style_from_expr(val_expr)
                        else:
                            val = self.generate_expr(val_expr)
                        lines.append(f"{ind}{cname}_{attr}[{idx_var}] = {val};")

                # Check function param cell var
                elif self.current_func and vname in self.param_container_map.get(self.current_func, {}):
                    cname = self.param_container_map[self.current_func][vname]
                    for attr, val_expr in stmt['attributes'].items():
                        # Special handling for text_content_style - convert to TextStyle
                        if attr == 'text_content_style' and val_expr.get('type') == 'array':
                            val = self._generate_text_style_from_expr(val_expr)
                        else:
                            val = self.generate_expr(val_expr)
                        lines.append(f"{ind}{cname}_{attr}[{vname}] = {val};")

                else:
                    # Non-repeated container modification (state variables)
                    for attr, val_expr in stmt['attributes'].items():
                        val = self.generate_expr(val_expr)
                        lines.append(f"{ind}// modify {vname}.{attr} = {val};")

            elif target.get('type') == 'member':
                # grid.X0Y0 direct access
                cname = self._base_name(target)
                if cname in self.repeated_containers:
                    idx = self._cell_index_from_member(target)
                    for attr, val_expr in stmt['attributes'].items():
                        # Special handling for text_content_style - convert to TextStyle
                        if attr == 'text_content_style' and val_expr.get('type') == 'array':
                            val = self._generate_text_style_from_expr(val_expr)
                        else:
                            val = self.generate_expr(val_expr)
                        lines.append(f"{ind}{cname}_{attr}[{idx}] = {val};")

        return lines

    def _cell_index_from_member(self, expr):
        """grid.X1Y2 → flat index (2*cols + 1)"""
        if expr.get('type') == 'member':
            field = expr['field']
            m = re.match(r'X(\d+)Y(\d+)', field)
            if m:
                x, y = int(m.group(1)), int(m.group(2))
                base = self._base_name(expr)
                if base in self.repeated_containers:
                    _, cols, _ = self.repeated_containers[base]
                    return str(y * cols + x)
        return '0'

    # =========================================================================
    # EXPRESSION GENERATION
    # =========================================================================

    def generate_expr(self, expr):
        if expr is None:
            return "null"
        if not isinstance(expr, dict):
            if isinstance(expr, bool):
                return "true" if expr else "false"
            if isinstance(expr, str):
                return f'"{expr}"'
            return str(expr)

        t = expr.get('type')

        if t == 'literal':
            v, vt = expr['value'], expr.get('value_type')
            if vt == 'string':
                if '{' in v:
                    return '"' + re.sub(r'\{([^}]+)\}', r'${\1}', v) + '"'
                return f'"{v}"'
            if vt == 'boolean':
                return 'true' if v else 'false'
            return str(v)

        if t == 'var':
            return expr['name']

        if t == 'binary_op':
            l = self.generate_expr(expr['left'])
            r = self.generate_expr(expr['right'])
            op = {'and': '&&', 'or': '||'}.get(expr['op'], expr['op'])
            return f"({l} {op} {r})"

        if t == 'unary_op':
            op = '!' if expr['op'] == 'not' else expr['op']
            return f"{op}{self.generate_expr(expr['operand'])}"

        if t == 'call':
            func = expr.get('function', {})
            args = [self.generate_expr(a) for a in expr.get('args', [])]
            fname = func.get('name') if func.get('type') == 'var' else None
            if fname == 'length' and args:
                return f"{args[0]}.length"
            if fname == 'rgb' and len(args) == 3:
                return f"const Color.fromRGBO({args[0]}, {args[1]}, {args[2]}, 1.0)"
            # Built-in functions
            if fname == 'random' and len(args) == 2:
                return f"(Random().nextInt({args[1]} - {args[0]} + 1) + {args[0]})"
            if fname == 'wait_sec' and len(args) == 1:
                return f"await Future.delayed(Duration(seconds: {args[0]}))"
            if fname == 'visit' and len(args) == 1:
                # TODO: Implement proper navigation with Navigator.push when multiple screens exist
                return f"print('Navigate to: ' + {args[0]}.toString())"
            if fname == 'play' and len(args) == 1:
                # TODO: Implement media playback with audioplayers package
                return f"print('Play media: ' + {args[0]}.toString())"
            return f"{self.generate_expr(func)}({', '.join(args)})"

        if t == 'member':
            obj_expr = expr['object']
            field = expr['field']
            
            # Special case: repeat_by.index -> index (when in repeat context)
            if (self.in_repeat_context and obj_expr.get('type') == 'var' 
                and obj_expr['name'] == 'repeat_by' and field == 'index'):
                return 'index'

            # pattern: cell_var.property  (for-loop or param cell reference)
            if obj_expr.get('type') == 'var':
                vname = obj_expr['name']

                # for-loop cell var
                if vname in self.cell_var_map:
                    cname, idx_var = self.cell_var_map[vname]
                    if cname in self.modified_containers and field in self.modified_containers[cname]:
                        return f"{cname}_{field}[{idx_var}]"

                # function param cell var
                if self.current_func and vname in self.param_container_map.get(self.current_func, {}):
                    cname = self.param_container_map[self.current_func][vname]
                    if cname in self.modified_containers and field in self.modified_containers[cname]:
                        return f"{cname}_{field}[{vname}]"

            # pattern: grid.X1Y2.property  (direct cell property access)
            if obj_expr.get('type') == 'member':
                inner_obj = obj_expr['object']
                inner_field = obj_expr['field']
                if inner_obj.get('type') == 'var':
                    cname = inner_obj['name']
                    if cname in self.repeated_containers:
                        m = re.match(r'X(\d+)Y(\d+)', inner_field)
                        if m:
                            x, y = int(m.group(1)), int(m.group(2))
                            _, cols, _ = self.repeated_containers[cname]
                            idx = y * cols + x
                            return f"{cname}_{field}[{idx}]"

            return f"{self.generate_expr(obj_expr)}.{field}"

        if t == 'index':
            return f"{self.generate_expr(expr['object'])}[{self.generate_expr(expr['index'])}]"

        if t == 'ternary':
            c = self.generate_expr(expr['condition'])
            th = self.generate_expr(expr['then'])
            el = self.generate_expr(expr['else'])
            return f"({c} ? {th} : {el})"

        if t == 'array':
            elems = [self.generate_expr(e) for e in expr.get('elements', [])]
            return f"[{', '.join(elems)}]"

        if t == 'object':
            pairs = [f'"{k}": {self.generate_expr(v)}' for k, v in expr.get('properties', {}).items()]
            return "{" + ', '.join(pairs) + "}"

        if t == 'method_call':
            obj = self.generate_expr(expr['object'])
            args = [self.generate_expr(a) for a in expr.get('args', [])]
            method = expr['method']
            # Array methods
            if method == 'add':
                return f"{obj}.add({', '.join(args)})"
            if method == 'remove':
                return f"{obj}.remove({', '.join(args)})"
            if method == 'index':
                return f"{obj}.indexOf({', '.join(args)})"
            return f"{obj}.{method}({', '.join(args)})"

        return "null"

    # =========================================================================
    # WIDGET GENERATION
    # =========================================================================

    def generate_widget(self, name, container, indent=0):
        attrs = container['attributes']
        if 'repeat_by' in attrs:
            return self.generate_repeated_widget(name, container, indent)
        wtype = self.determine_widget_type(container)
        if wtype == 'Column':
            return self.generate_column_widget(name, container, indent)
        if wtype == 'Text':
            return self.generate_text_widget(name, container, indent)
        if wtype == 'ElevatedButton':
            return self.generate_button_widget(name, container, indent)
        if wtype == 'TextField':
            return self.generate_textfield_widget(name, container, indent)
        if wtype == 'ListView':
            return self.generate_listview_widget(name, container, indent)
        return self.generate_container_widget(name, container, indent)

    def determine_widget_type(self, container):
        attrs = container['attributes']
        if 'type' in attrs:
            tv = attrs['type']
            # Handle both literal strings and var names for type
            type_value = None
            if tv.get('type') == 'literal':
                type_value = tv['value']
            elif tv.get('type') == 'var':
                type_value = tv['name']
            
            if type_value:
                m = {'button': 'ElevatedButton', 'input': 'TextField'}
                if type_value in m:
                    return m[type_value]
        if 'scrollable' in attrs:
            sv = attrs['scrollable']
            if sv.get('type') == 'literal' and sv.get('value'):
                return 'ListView'
        if 'children' in attrs or container.get('children_def'):
            return 'Column'
        if 'text_content' in attrs:
            return 'Text'
        return 'Container'

    def generate_column_widget(self, name, container, indent):
        attrs = container['attributes']
        children = self.collect_children(name, container)
        if not children:
            return "Container()"

        ind, ind2 = "  " * indent, "  " * (indent + 1)
        main_ax, cross_ax = self._column_alignment(attrs.get('align_children'))

        def _is_max_height(cc):
            h = cc.get('attributes', {}).get('height')
            if not h:
                return False
            return (h.get('type') == 'var' and h.get('name') == 'max') or \
                   (h.get('type') == 'literal' and h.get('value') == 'max')

        has_expanded_child = any(_is_max_height(cc) for _, cc in children)
        main_size = "MainAxisSize.max" if has_expanded_child else "MainAxisSize.min"

        widget = (f"Column(\n{ind2}mainAxisAlignment: {main_ax},\n"
                  f"{ind2}crossAxisAlignment: {cross_ax},\n"
                  f"{ind2}mainAxisSize: {main_size},\n{ind2}children: [\n")
        for i, (cn, cc) in enumerate(children):
            cw = self.generate_widget(cn, cc, indent + 1)
            if _is_max_height(cc):
                cw = f"Expanded(\n{ind2}  child: {cw},\n{ind2})"
            widget += f"{ind2}  {cw}"
            if i < len(children) - 1:
                widget += ","
            widget += "\n"
        widget += f"{ind2}],\n{ind})"
        return self.wrap_with_props(widget, name, attrs, indent)

    def _column_alignment(self, align_expr):
        val = self._align_val(align_expr)
        if val in ('center', 'centre'):
            return 'MainAxisAlignment.center', 'CrossAxisAlignment.center'
        if val == 'left':
            return 'MainAxisAlignment.start', 'CrossAxisAlignment.start'
        if val == 'right':
            return 'MainAxisAlignment.start', 'CrossAxisAlignment.end'
        return 'MainAxisAlignment.start', 'CrossAxisAlignment.start'

    def _align_val(self, expr):
        if not expr:
            return None
        if expr.get('type') == 'var':
            return expr['name']
        if expr.get('type') == 'literal':
            return str(expr['value'])
        return None

    def generate_text_widget(self, name, container, indent):
        attrs = container['attributes']
        text_content = attrs.get('text_content')

        # If this is a repeated container with tracked text_content, read from state
        if (name in self.repeated_containers and name in self.modified_containers
                and 'text_content' in self.modified_containers[name]):
            text_str = f"{name}_text_content[index]"
        else:
            text_str = self.generate_expr(text_content) if text_content else '""'

        style = self.generate_text_style(attrs)
        widget = f"Text({text_str}{', style: ' + style if style else ''})"
        return self.wrap_with_props(widget, name, attrs, indent)

    def generate_text_style(self, attrs):
        """Build TextStyle(...) string from text_content_style attribute"""
        style_expr = attrs.get('text_content_style')
        if not style_expr or style_expr.get('type') != 'array':
            return None
        return self._generate_text_style_from_expr(style_expr)
    
    def _generate_text_style_from_expr(self, style_expr):
        """Convert text_content_style array expression to TextStyle(...) string"""
        if not style_expr or style_expr.get('type') != 'array':
            return None
        parts = []
        for elem in style_expr.get('elements', []):
            if elem.get('type') != 'kvpair':
                continue
            key, val = elem['key'], elem['value']
            if key == 'font':
                vn = val.get('name', '') if val.get('type') == 'var' else ''
                if vn == 'bold':
                    parts.append('fontWeight: FontWeight.bold')
                elif vn == 'italic':
                    parts.append('fontStyle: FontStyle.italic')
            elif key == 'font_size':
                size = val.get('value', 14) if val.get('type') == 'literal' else self.generate_expr(val)
                parts.append(f'fontSize: {float(size) if isinstance(size, (int, float)) else size}')
            elif key == 'color':
                # Handle color - could be simple value or ternary expression
                if val.get('type') == 'ternary':
                    # For ternary, generate the full expression
                    c = self.generate_expr(val)
                else:
                    c = self.resolve_color(val)
                if c:
                    parts.append(f'color: {c}')
        return f"TextStyle({', '.join(parts)})" if parts else None

    def generate_button_widget(self, name, container, indent):
        attrs = container['attributes']
        text_str = self.generate_expr(attrs.get('text_content')) if 'text_content' in attrs else '"Button"'
        style = self.generate_text_style(attrs)
        text_widget = f"Text({text_str}{', style: ' + style if style else ''})"
        on_click = attrs.get('on_click')
        on_press = f"() => {self.generate_expr(on_click)}" if on_click else "null"
        ind, ind2 = "  " * indent, "  " * (indent + 1)

        # Build ElevatedButton.styleFrom so color/shape render correctly
        btn_style_parts = []
        color = self.resolve_color(attrs.get('color'))
        if color:
            btn_style_parts.append(f"backgroundColor: {color}")
        shape = attrs.get('shape')
        if shape and shape.get('type') == 'var':
            sname = shape['name']
            if sname == 'sqircle':
                btn_style_parts.append("shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16))")
            elif sname == 'circle':
                btn_style_parts.append("shape: const CircleBorder()")
        w = self.resolve_dimension(attrs.get('width'))
        h = self.resolve_dimension(attrs.get('height'))
        if w and h:
            btn_style_parts.append(f"minimumSize: Size({w}, {h})")
            btn_style_parts.append(f"maximumSize: Size({w}, {h})")

        style_str = f"ElevatedButton.styleFrom({', '.join(btn_style_parts)})" if btn_style_parts else None
        button = f"ElevatedButton(\n{ind2}onPressed: {on_press},\n"
        if style_str:
            button += f"{ind2}style: {style_str},\n"
        button += f"{ind2}child: {text_widget},\n{ind})"

        # Apply alignment only (skip Container wrapping — color/shape already on button)
        align_self = attrs.get('align_self')
        if align_self:
            alignment = self._resolve_align_self(align_self)
            if alignment:
                button = f"Align(\n{ind2}alignment: {alignment},\n{ind2}child: {button},\n{ind})"
        margin = attrs.get('margin')
        if margin:
            margin_val = self._resolve_margin(margin)
            if margin_val:
                button = f"Padding(\n{ind2}padding: {margin_val},\n{ind2}child: {button},\n{ind})"
        return button

    def generate_textfield_widget(self, name, container, indent):
        attrs = container['attributes']
        ph = self.generate_expr(attrs.get('placeholder')) if 'placeholder' in attrs else '"Enter text"'
        ind, ind2, ind3 = "  " * indent, "  " * (indent + 1), "  " * (indent + 2)
        return f"TextField(\n{ind2}decoration: InputDecoration(\n{ind3}hintText: {ph},\n{ind2}),\n{ind})"

    def generate_listview_widget(self, name, container, indent):
        children = self.collect_children(name, container)
        if not children:
            return "ListView()"
        ind, ind2 = "  " * indent, "  " * (indent + 1)
        widget = f"ListView(\n{ind2}children: [\n"
        for i, (cn, cc) in enumerate(children):
            cw = self.generate_widget(cn, cc, indent + 2)
            widget += f"{ind2}  {cw}"
            if i < len(children) - 1:
                widget += ","
            widget += "\n"
        widget += f"{ind2}],\n{ind})"
        return widget

    def generate_container_widget(self, name, container, indent):
        attrs = container['attributes']
        children = self.collect_children(name, container)
        ind, ind2 = "  " * indent, "  " * (indent + 1)
        props = []
        w = self.resolve_dimension(attrs.get('width'))
        h = self.resolve_dimension(attrs.get('height'))
        deco = self.build_decoration(attrs)
        color = self.resolve_color(attrs.get('color')) if not deco else None
        if w:
            props.append(f"width: {w}")
        if h:
            props.append(f"height: {h}")
        if deco:
            props.append(f"decoration: {deco}")
        elif color:
            props.append(f"color: {color}")
        if children:
            cw = self.generate_widget(children[0][0], children[0][1], indent + 1)
            props.append(f"child: {cw}")
        if not props:
            return "Container()"
        code = "Container(\n"
        for i, p in enumerate(props):
            code += f"{ind2}{p}"
            if i < len(props) - 1:
                code += ","
            code += "\n"
        code += f"{ind})"
        return code

    def generate_repeated_widget(self, name, container, indent):
        attrs = container['attributes']
        repeat_expr = attrs.get('repeat_by')
        if not repeat_expr or repeat_expr.get('type') != 'array':
            return self.generate_container_widget(name, container, indent)

        dims = [int(e['value']) for e in repeat_expr['elements']
                if e.get('type') == 'literal' and e.get('value_type') == 'number']
        if len(dims) != 2:
            return self.generate_container_widget(name, container, indent)

        rows, cols = dims
        count = rows * cols
        template_attrs = {k: v for k, v in attrs.items() if k != 'repeat_by'}
        has_state = name in self.modified_containers

        ind, ind2, ind3 = "  " * indent, "  " * (indent + 1), "  " * (indent + 2)
        code = (f"GridView.count(\n{ind2}crossAxisCount: {cols},\n"
                f"{ind2}shrinkWrap: true,\n"
                f"{ind2}physics: const NeverScrollableScrollPhysics(),\n"
                f"{ind2}childAspectRatio: 1.0,\n"
                f"{ind2}children: List.generate({count}, (index) {{\n"
                f"{ind3}return ")
        code += self.generate_cell_widget(name, template_attrs, has_state, indent + 3)
        code += f";\n{ind2}}}),\n{ind})"
        return code

    def generate_cell_widget(self, container_name, attrs, has_state, indent):
        ind, ind2 = "  " * indent, "  " * (indent + 1)
        
        # Mark that we're in a repeat context
        prev_repeat = self.in_repeat_context
        self.in_repeat_context = True

        # Text content — read from state list if tracked
        if 'text_content' in attrs:
            if has_state and 'text_content' in self.modified_containers.get(container_name, {}):
                text_str = f"{container_name}_text_content[index]"
            else:
                text_str = self.generate_expr(attrs['text_content'])
            
            # Check if text_content_style is tracked in state
            if has_state and 'text_content_style' in self.modified_containers.get(container_name, {}):
                # Use dynamic style from state list
                style = f"{container_name}_text_content_style[index]"
            else:
                # Use static style from template
                style = self.generate_text_style(attrs)
            
            text_widget = f"Text({text_str}{', style: ' + style if style else ''})"
            inner = (f"Center(child: Column(\n{ind2}mainAxisAlignment: MainAxisAlignment.center,\n"
                     f"{ind2}crossAxisAlignment: CrossAxisAlignment.center,\n"
                     f"{ind2}mainAxisSize: MainAxisSize.min,\n"
                     f"{ind2}children: [{text_widget}],\n{ind}))")
        else:
            inner = None

        deco = self.build_decoration(attrs)
        color = self.resolve_color(attrs.get('color')) if not deco else None

        cell_props = []
        if deco:
            cell_props.append(f"decoration: {deco}")
        elif color:
            cell_props.append(f"color: {color}")
        if inner:
            cell_props.append(f"child: {inner}")

        if cell_props:
            cell = "Container(\n"
            for i, p in enumerate(cell_props):
                cell += f"{ind2}{p}"
                if i < len(cell_props) - 1:
                    cell += ","
                cell += "\n"
            cell += f"{ind})"
        else:
            cell = "Container()"

        # Wrap in GestureDetector if on_click is set
        on_click = attrs.get('on_click')
        if on_click:
            handler = self._cell_handler(on_click)
            gesture = (f"GestureDetector(\n{ind2}onTap: {handler},\n"
                       f"{ind2}child: {cell},\n{ind})")
            self.in_repeat_context = prev_repeat
            return gesture
        
        self.in_repeat_context = prev_repeat
        return cell

    def _cell_handler(self, on_click_expr):
        if on_click_expr.get('type') == 'call':
            fname = on_click_expr['function'].get('name', 'unknown')
            return f"() => {fname}(index)"
        return "null"

    # =========================================================================
    # HELPERS
    # =========================================================================

    def wrap_with_props(self, widget_code, name, attrs, indent):
        """Wrap widget in Container / Align as needed"""
        ind, ind2 = "  " * indent, "  " * (indent + 1)
        
        # Handle visibility first
        visibility = attrs.get('visibility')
        if visibility:
            vis_val = self.generate_expr(visibility)
            widget_code = f"Visibility(\n{ind2}visible: {vis_val},\n{ind2}child: {widget_code},\n{ind})"
        
        w = self.resolve_dimension(attrs.get('width'))
        h = self.resolve_dimension(attrs.get('height'))
        deco = self.build_decoration(attrs)
        color = self.resolve_color(attrs.get('color')) if not deco else None

        if w or h or deco or color:
            props = []
            if w:
                props.append(f"width: {w}")
            if h:
                props.append(f"height: {h}")
            if deco:
                props.append(f"decoration: {deco}")
            elif color:
                props.append(f"color: {color}")
            props.append(f"child: {widget_code}")
            wrapper = "Container(\n"
            for i, p in enumerate(props):
                wrapper += f"{ind2}{p}"
                if i < len(props) - 1:
                    wrapper += ","
                wrapper += "\n"
            wrapper += f"{ind})"
            widget_code = wrapper

        align_self = attrs.get('align_self')
        if align_self:
            alignment = self._resolve_align_self(align_self)
            if alignment:
                widget_code = f"Align(\n{ind2}alignment: {alignment},\n{ind2}child: {widget_code},\n{ind})"
        
        # Handle margin
        margin = attrs.get('margin')
        if margin:
            margin_val = self._resolve_margin(margin)
            if margin_val:
                widget_code = f"Padding(\n{ind2}padding: {margin_val},\n{ind2}child: {widget_code},\n{ind})"

        return widget_code
    
    def _resolve_margin(self, expr):
        """Convert margin expression to EdgeInsets"""
        if expr.get('type') == 'literal' and expr.get('value_type') == 'number':
            return f"EdgeInsets.all({expr['value']})"
        if expr.get('type') == 'array':
            elems = expr.get('elements', [])
            if len(elems) == 4:
                vals = [self.generate_expr(e) for e in elems]
                return f"EdgeInsets.fromLTRB({vals[3]}, {vals[0]}, {vals[1]}, {vals[2]})"
        return None

    def _resolve_align_self(self, expr):
        val = self._align_val(expr)
        return {
            'center': 'Alignment.center', 'centre': 'Alignment.center',
            'top': 'Alignment.topCenter', 'bottom': 'Alignment.bottomCenter',
            'left': 'Alignment.centerLeft', 'right': 'Alignment.centerRight',
        }.get(val)

    def build_decoration(self, attrs):
        """Build BoxDecoration string if shape is set"""
        shape = attrs.get('shape')
        if not shape or shape.get('type') != 'var':
            return None
        sname = shape['name']
        if sname == 'sqircle':
            border = 'borderRadius: BorderRadius.circular(16)'
        elif sname == 'circle':
            border = 'shape: BoxShape.circle'
        else:
            return None
        color = self.resolve_color(attrs.get('color'))
        color_part = f"color: {color}, " if color else ""
        return f"BoxDecoration({color_part}{border})"

    def collect_children(self, name, container):
        children = []
        children_expr = container['attributes'].get('children')
        if children_expr and children_expr.get('type') == 'array':
            for elem in children_expr['elements']:
                if elem.get('type') == 'var':
                    cn = elem['name']
                    if cn in self.ast['containers']:
                        children.append((cn, self.ast['containers'][cn]))
        for child_def in container.get('children_def', []):
            children.append((child_def['name'], child_def))
        return children

    def resolve_dimension(self, dim_expr):
        if not dim_expr:
            return None
        if dim_expr.get('type') == 'literal':
            if dim_expr.get('value_type') == 'number':
                return f"MediaQuery.of(context).size.width * {dim_expr['value'] / 100}"
            if dim_expr.get('value_type') == 'string' and dim_expr['value'] == 'max':
                return "double.infinity"
        if dim_expr.get('type') == 'var' and dim_expr['name'] == 'max':
            return "double.infinity"
        return None

    def resolve_color(self, color_expr):
        if not color_expr:
            return None
        if color_expr.get('type') == 'var':
            return {
                'red': 'Colors.red', 'blue': 'Colors.blue', 'green': 'Colors.green',
                'yellow': 'Colors.yellow', 'purple': 'Colors.purple', 'orange': 'Colors.orange',
                'pink': 'Colors.pink', 'white': 'Colors.white', 'black': 'Colors.black',
                'gray': 'Colors.grey',
            }.get(color_expr['name'])
        if color_expr.get('type') == 'index':
            obj, idx = color_expr['object'], color_expr['index']
            if obj.get('type') == 'var' and idx.get('type') == 'literal':
                base = {
                    'red': 'Colors.red', 'blue': 'Colors.blue', 'green': 'Colors.green',
                    'yellow': 'Colors.yellow', 'purple': 'Colors.purple', 'orange': 'Colors.orange',
                    'pink': 'Colors.pink', 'gray': 'Colors.grey',
                }.get(obj['name'], 'Colors.grey')
                return f"{base}[{int(idx['value'])}]"
        if color_expr.get('type') == 'call':
            func = color_expr.get('function', {})
            if func.get('type') == 'var' and func['name'] == 'rgb':
                args = [self.generate_expr(a) for a in color_expr.get('args', [])]
                if len(args) == 3:
                    return f"const Color.fromRGBO({args[0]}, {args[1]}, {args[2]}, 1.0)"
        return None

    def infer_type(self, expr):
        if not isinstance(expr, dict):
            if isinstance(expr, bool): return "bool"
            if isinstance(expr, int): return "int"
            if isinstance(expr, float): return "double"
            if isinstance(expr, str): return "String"
            return "dynamic"
        t = expr.get('type')
        if t == 'literal':
            vt = expr.get('value_type')
            if vt == 'boolean': return "bool"
            if vt == 'number':
                return "int" if isinstance(expr['value'], int) else "double"
            if vt == 'string': return "String"
        if t == 'array': return "List"
        if t == 'object': return "Map<String, dynamic>"
        return "dynamic"
