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
  Map<String, Map<String, dynamic>> widgetStates = {}; // Store dynamic widget properties

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
      
      case 'modify_container':
        // Get the container name (could be a direct name or from a variable)
        String? containerName;
        var target = stmt['target'];
        if (target is Map && target['type'] == 'var') {
          // It's a variable - could be a widget name stored in state
          var varValue = state[target['name']];
          if (varValue is String) {
            containerName = varValue;
          } else {
            containerName = target['name'];  // Assume it's the widget name directly
          }
        }
        
        if (containerName != null) {
          // Initialize widget state if not exists
          if (!widgetStates.containsKey(containerName)) {
            widgetStates[containerName] = {};
          }
          
          // Update the widget's attributes
          Map<String, dynamic> attrs = stmt['attributes'] ?? {};
          attrs.forEach((key, value) {
            widgetStates[containerName]![key] = evalExpression(value);
          });
          
          setState(() {}); // Trigger rebuild
        }
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (compiledData == null) {
      return Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    // Build the root widget and wrap in SafeArea + SizedBox.expand if it uses max dimensions
    var rootNode = compiledData!['tree'];
    Widget rootWidget = buildWidget(rootNode);
    
    // Check if root uses max dimensions
    var rootProps = rootNode['props'] ?? {};
    var rootWidth = resolveDimension(rootProps['width']);
    var rootHeight = resolveDimension(rootProps['height']);
    
    // Convert root dimensions: percentages to pixels, infinity to screen size
    double? finalRootWidth = rootWidth;
    double? finalRootHeight = rootHeight;
    
    if (rootWidth == double.infinity) {
      finalRootWidth = MediaQuery.of(context).size.width;
    } else if (rootWidth != null && rootWidth <= 100 && rootWidth > 0) {
      finalRootWidth = MediaQuery.of(context).size.width * (rootWidth / 100);
    }
    
    if (rootHeight == double.infinity) {
      finalRootHeight = MediaQuery.of(context).size.height;
    } else if (rootHeight != null && rootHeight <= 100 && rootHeight > 0) {
      finalRootHeight = MediaQuery.of(context).size.height * (rootHeight / 100);
    }
    
    // Wrap root in SizedBox if dimensions were specified
    if (finalRootWidth != null || finalRootHeight != null) {
      rootWidget = SizedBox(
        width: finalRootWidth,
        height: finalRootHeight,
        child: rootWidget,
      );
    }

    return Scaffold(
      body: SafeArea(child: rootWidget),
    );
  }

  Widget buildWidget(Map<String, dynamic>? node, {bool inFlex = false}) {
    if (node == null) return Container();
    
    String widgetType = node['widget'] ?? 'Container';
    String widgetName = node['name'] ?? '';
    Map<String, dynamic> props = Map.from(node['props'] ?? {});
    
    // Merge dynamic widget states (from modify_container statements)
    if (widgetStates.containsKey(widgetName)) {
      widgetStates[widgetName]!.forEach((key, value) {
        // Map text_content to text for runtime consistency
        if (key == 'text_content') {
          props['text'] = value;
        } else {
          props[key] = value;
        }
      });
    }
    
    // Handle repeated widgets
    if (widgetType == 'Repeated') {
      List<Widget> instances = [];
      int? gridCols;
      
      for (var instance in node['instances']) {
        instances.add(buildWidget(instance, inFlex: false));
        
        // Try to detect grid dimensions from instance names (e.g., grid_X0Y0)
        var instanceName = instance['name'] ?? '';
        var match = RegExp(r'_X(\d+)Y(\d+)').firstMatch(instanceName);
        if (match != null && gridCols == null) {
          // Count how many Y variations exist for X0 to get row count
          int maxX = 0;
          for (var inst in node['instances']) {
            var name = inst['name'] ?? '';
            var m = RegExp(r'_X(\d+)Y(\d+)').firstMatch(name);
            if (m != null) {
              int x = int.parse(m.group(1)!);
              if (x > maxX) maxX = x;
            }
          }
          gridCols = maxX + 1;
        }
      }
      
      // Use GridView if we detected grid structure, otherwise Wrap
      if (gridCols != null && gridCols > 0) {
        Widget gridView = GridView.count(
          crossAxisCount: gridCols,
          shrinkWrap: true,
          physics: NeverScrollableScrollPhysics(),
          childAspectRatio: 1.0, // Make cells square
          children: instances,
        );
        
        // If parent has infinity constraints, wrap in a sized container
        // This prevents "unbounded height" errors
        return LayoutBuilder(
          builder: (context, constraints) {
            if (constraints.maxHeight == double.infinity) {
              // Use intrinsic height to fit content
              return IntrinsicHeight(child: gridView);
            }
            return gridView;
          },
        );
      } else {
        return Wrap(children: instances);
      }
    }
    
    // Evaluate dimensions
    double? width = resolveDimension(props['width']);
    double? height = resolveDimension(props['height']);
    
    // Check if dimensions are "max" (infinity)
    bool widthIsMax = width == double.infinity;
    bool heightIsMax = height == double.infinity;
    
    // If we're in a flex container and height is max, use Expanded instead of infinity
    bool needsExpanded = inFlex && heightIsMax;
    if (needsExpanded) {
      height = null; // Expanded will handle the sizing
    }
    
    // If width is max but we're not in a flex, keep it as infinity to fill parent
    // If height is max but we're not in a flex, keep it as infinity to fill parent
    
    // Evaluate color
    Color? color = resolveColor(props['color'], props['color_expr']);
    
    // Build children
    List<Widget> children = [];
    bool isFlexContainer = widgetType == 'Column' || widgetType == 'Row';
    if (node['children'] != null) {
      for (var child in node['children']) {
        children.add(buildWidget(child, inFlex: isFlexContainer));
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
        String text = '';
        if (props['text'] is String) {
          text = resolveText(props['text'], props['text_bindings']);
        } else if (props['text_expr'] != null) {
          var result = evalExpression(props['text_expr']);
          if (result != null) {
            text = result.toString();
            if (text.contains('{')) {
              text = resolveText(text, null);
            }
          } else {
            text = '';
          }
        }
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
        Widget? contentWidget;
        
        // Check if there's text_content
        if (props['text'] != null || props['text_expr'] != null) {
          String text = '';
          if (props['text'] is String) {
            text = resolveText(props['text'], props['text_bindings']);
          } else if (props['text_expr'] != null) {
            var result = evalExpression(props['text_expr']);
            if (result != null) {
              // If result is a string with interpolation, resolve it
              text = result.toString();
              if (text.contains('{')) {
                text = resolveText(text, null);
              }
            } else {
              text = '';
            }
          }
          
          // Apply text styling if provided
          TextStyle? textStyle;
          if (props['text_content_style'] != null) {
            // TODO: Parse text_content_style array
          }
          
          contentWidget = Text(text, style: textStyle);
        } else if (children.isNotEmpty) {
          contentWidget = children.length == 1 ? children[0] : Column(children: children);
        }
        
        widget = contentWidget ?? Container();
        break;
    }
    
    // Add gesture detection for on_click events
    if (props['events']?['on_click'] != null && widgetType != 'ElevatedButton') {
      widget = GestureDetector(
        onTap: () => handleEvent(props['events']['on_click']),
        child: widget,
      );
    }
    
    // Wrap in Container if we have dimensions or color
    if (width != null || height != null || color != null) {
      // Use LayoutBuilder to convert Vi percentages (0-100) to pixels
      // Also handles infinity (max) dimensions
      // But skip if Expanded will be used (needsExpanded)
      if (!needsExpanded && ((width != null && width <= 100 && width > 0) || 
          (height != null && height <= 100 && height > 0) ||
          width == double.infinity || height == double.infinity)) {
        widget = LayoutBuilder(
          builder: (context, constraints) {
            double? finalWidth = width;
            double? finalHeight = height;
            
            // Convert percentages to actual pixels
            if (width != null && width != double.infinity && width <= 100) {
              finalWidth = constraints.maxWidth * (width / 100);
            } else if (width == double.infinity) {
              finalWidth = constraints.maxWidth;
            }
            
            if (height != null && height != double.infinity && height <= 100) {
              finalHeight = constraints.maxHeight * (height / 100);
            } else if (height == double.infinity) {
              finalHeight = constraints.maxHeight;
            }
            
            return Container(
              width: finalWidth,
              height: finalHeight,
              color: color,
              alignment: Alignment.center,
              child: widget,
            );
          },
        );
      } else {
        // Dimensions are already in pixels
        widget = Container(
          width: width,
          height: height,
          color: color,
          alignment: Alignment.center,
          child: widget,
        );
      }
    }
    
    // Wrap in Expanded if needed (for max dimensions inside flex containers)
    if (needsExpanded) {
      // If there's color but no container yet, wrap in one
      if (color != null && !(widget is Container)) {
        widget = Container(
          color: color,
          alignment: Alignment.center,
          child: widget,
        );
      }
      widget = Expanded(child: widget);
    }
    
    return widget;
  }

  double? resolveDimension(dynamic dimData) {
    if (dimData == null) return null;
    if (dimData is! Map) return null;
    
    String type = dimData['type'] ?? '';
    
    switch (type) {
      case 'fixed':
        // Vi uses 0-100 range for percentages, need to convert based on screen
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
    } else {
      // Also handle direct variable interpolation
      final regex = RegExp(r'\{([^}]+)\}');
      result = result.replaceAllMapped(regex, (match) {
        String varName = match.group(1)!;
        if (state.containsKey(varName)) {
          return state[varName].toString();
        }
        return match.group(0)!;
      });
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
