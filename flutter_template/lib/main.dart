import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:flutter/services.dart';
import 'dart:math' as math;

void main() {
  runApp(ViRuntime());
}

class ViRuntime extends StatelessWidget {
  const ViRuntime({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: ViApp(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class ViApp extends StatefulWidget {
  const ViApp({super.key});

  @override
  State<ViApp> createState() => _ViAppState();
}

class _ViAppState extends State<ViApp> {
  Map<String, dynamic>? compiledData;
  Map<String, dynamic> state = {};
  Map<String, Function> functions = {};

  @override
  void initState() {
    super.initState();
    loadTree();
  }

  Future<void> loadTree() async {
    String jsonString = await rootBundle.loadString('assets/vi_tree.json');
    compiledData = jsonDecode(jsonString);
    
    // Initialize state
    if (compiledData!['state'] != null) {
      (compiledData!['state'] as Map<String, dynamic>).forEach((key, value) {
        state[key] = evalExpression(value['initial']);
      });
    }
    
    // Initialize functions
    if (compiledData!['functions'] != null) {
      (compiledData!['functions'] as Map<String, dynamic>).forEach((key, value) {
        functions[key] = () => executeFunction(value);
      });
    }
    
    setState(() {});
  }

  dynamic evalExpression(dynamic expr) {
    if (expr == null) return null;
    if (expr is! Map) return expr;
    
    String type = expr['type'] ?? '';
    
    switch (type) {
      case 'literal':
        return expr['value'];
      
      case 'var':
        return state[expr['name']];
      
      case 'binary_op':
        var left = evalExpression(expr['left']);
        var right = evalExpression(expr['right']);
        switch (expr['op']) {
          case '+': return left + right;
          case '-': return left - right;
          case '*': return left * right;
          case '/': return left / right;
          case '>': return left > right;
          case '<': return left < right;
          case '>=': return left >= right;
          case '<=': return left <= right;
          case '==': return left == right;
          case '!=': return left != right;
          case 'and': return left && right;
          case 'or': return left || right;
          default: return null;
        }
      
      case 'unary_op':
        var operand = evalExpression(expr['operand']);
        switch (expr['op']) {
          case '!': return !operand;
          case '-': return -operand;
          default: return null;
        }
      
      case 'member':
        var obj = evalExpression(expr['object']);
        if (obj is Map) return obj[expr['field']];
        return null;
      
      case 'index':
        var obj = evalExpression(expr['object']);
        var idx = evalExpression(expr['index']);
        if (obj is List) return obj[idx];
        if (obj is Map) return obj[idx];
        return null;
      
      case 'call':
        String funcName = expr['function']['name'];
        if (functions.containsKey(funcName)) {
          return functions[funcName]!();
        }
        return null;
      
      case 'ternary':
        var condition = evalExpression(expr['condition']);
        return condition ? evalExpression(expr['then']) : evalExpression(expr['else']);
      
      case 'array':
        return (expr['elements'] as List).map((e) => evalExpression(e)).toList();
      
      default:
        return null;
    }
  }

  void executeFunction(Map<String, dynamic> funcDef) {
    List<dynamic> body = funcDef['body'] ?? [];
    for (var stmt in body) {
      executeStatement(stmt);
    }
  }

  void executeStatement(Map<String, dynamic> stmt) {
    String type = stmt['type'] ?? '';
    
    switch (type) {
      case 'assign':
        String varName = stmt['target']['name'];
        dynamic value = evalExpression(stmt['value']);
        setState(() {
          state[varName] = value;
        });
        break;
      
      case 'return':
        // Handle return if needed
        break;
      
      case 'if':
        bool condition = evalExpression(stmt['condition']);
        List<dynamic> branch = condition ? stmt['then'] : (stmt['else'] ?? []);
        for (var s in branch) {
          executeStatement(s);
        }
        break;
      
      case 'for':
        String varName = stmt['var'];
        List iterable = evalExpression(stmt['iterable']);
        for (var item in iterable) {
          state[varName] = item;
          for (var s in stmt['body']) {
            executeStatement(s);
          }
        }
        break;
      
      case 'expr_stmt':
        evalExpression(stmt['expr']);
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (compiledData == null) {
      return Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      body: buildWidget(compiledData!['tree']),
    );
  }

  Widget buildWidget(Map<String, dynamic>? node) {
    if (node == null) return Container();
    
    String widgetType = node['widget'] ?? 'Container';
    Map<String, dynamic> props = node['props'] ?? {};
    
    // Handle repeated widgets
    if (widgetType == 'Repeated') {
      List<Widget> instances = [];
      for (var instance in node['instances']) {
        instances.add(buildWidget(instance));
      }
      return Wrap(children: instances);
    }
    
    // Evaluate dimensions
    double? width = resolveDimension(props['width']);
    double? height = resolveDimension(props['height']);
    
    // Evaluate color
    Color? color = resolveColor(props['color'], props['color_expr']);
    
    // Build children
    List<Widget> children = [];
    if (node['children'] != null) {
      for (var child in node['children']) {
        children.add(buildWidget(child));
      }
    }
    
    // Build based on widget type
    Widget widget;
    
    switch (widgetType) {
      case 'Column':
        widget = Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: children,
        );
        break;
      
      case 'Row':
        widget = Row(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: children,
        );
        break;
      
      case 'ListView':
        widget = ListView(
          children: children,
        );
        break;
      
      case 'ElevatedButton':
        String text = resolveText(props['text'], props['text_bindings']);
        widget = ElevatedButton(
          onPressed: props['events']?['on_click'] != null 
            ? () => handleEvent(props['events']['on_click'])
            : null,
          child: Text(text),
        );
        break;
      
      case 'TextField':
        widget = TextField(
          decoration: InputDecoration(
            hintText: props['placeholder'] != null ? evalExpression(props['placeholder']) : null,
          ),
        );
        break;
      
      default:
        // Container
        widget = children.isEmpty 
          ? Container() 
          : (children.length == 1 ? children[0] : Column(children: children));
        break;
    }
    
    // Wrap in Container if we have dimensions or color
    if (width != null || height != null || color != null) {
      widget = Container(
        width: width,
        height: height,
        color: color,
        child: widget,
      );
    }
    
    return widget;
  }

  double? resolveDimension(dynamic dimData) {
    if (dimData == null) return null;
    if (dimData is! Map) return null;
    
    String type = dimData['type'] ?? '';
    
    switch (type) {
      case 'fixed':
        return (dimData['value'] as num).toDouble();
      case 'infinity':
        return double.infinity;
      case 'expression':
        var result = evalExpression(dimData['expr']);
        return result is num ? result.toDouble() : null;
      default:
        return null;
    }
  }

  Color? resolveColor(dynamic colorValue, dynamic colorExpr) {
    if (colorValue != null && colorValue is int) {
      return Color(colorValue);
    }
    
    if (colorExpr != null) {
      var result = evalExpression(colorExpr);
      if (result is int) return Color(result);
    }
    
    return null;
  }

  String resolveText(dynamic text, dynamic bindings) {
    if (text == null) return '';
    
    String result = text.toString();
    
    if (bindings != null && bindings is List) {
      for (String varName in bindings) {
        if (state.containsKey(varName)) {
          result = result.replaceAll('{$varName}', state[varName].toString());
        }
      }
    }
    
    return result;
  }

  void handleEvent(dynamic eventExpr) {
    if (eventExpr == null) return;
    
    if (eventExpr is Map && eventExpr['type'] == 'call') {
      String funcName = eventExpr['function']['name'];
      if (functions.containsKey(funcName)) {
        setState(() {
          functions[funcName]!();
        });
      }
    }
  }
}
