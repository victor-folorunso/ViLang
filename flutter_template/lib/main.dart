import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:flutter/services.dart';

void main() {
  runApp(ViRuntime());
}

class ViRuntime extends StatelessWidget {
  const ViRuntime({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: ViApp(),
    );
  }
}

class ViApp extends StatefulWidget {
  const ViApp({super.key});

  @override
  State<ViApp> createState() => _ViAppState();
}

class _ViAppState extends State<ViApp> {
  Map<String, dynamic>? tree;

  @override
  void initState() {
    super.initState();
    loadTree();
  }

  Future<void> loadTree() async {
    String jsonString = await rootBundle.loadString('assets/vi_tree.json');
    setState(() {
      tree = jsonDecode(jsonString);
    });
  }

  @override
  Widget build(BuildContext context) {
    if (tree == null) {
      return Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      body: buildWidget(tree!),
    );
  }

  Widget buildWidget(Map<String, dynamic> node) {
    double? width = node['width'] == 'max' ? double.infinity : node['width']?.toDouble();
    double? height = node['height'] == 'max' ? double.infinity : node['height']?.toDouble();
    Color? color = parseColor(node['color']);

    List<Widget> children = [];
    if (node['children'] != null) {
      for (var child in node['children']) {
        children.add(buildWidget(child));
      }
    }

    return Container(
      width: width,
      height: height,
      color: color,
      child: children.isEmpty ? null : Center(child: children[0]),
    );
  }

  Color? parseColor(String? colorString) {
    if (colorString == null) return null;
    if (colorString == 'blue') return Colors.blue;
    if (colorString == 'red') return Colors.red;
    if (colorString == 'white') return Colors.white;
    return null;
  }
}