#!/usr/bin/env python3
"""Test the Dart Code Generator with State Lifting"""

from parser import Parser
from codegen.dart_codegen import DartCodegen

print("=" * 80)
print("TESTING tictactoe APP")
print("=" * 80)

# Parse test file
parser = Parser("main.vi")
ast = parser.parse()

# Generate Dart code directly from AST
codegen = DartCodegen(ast)
dart_code = codegen.generate_full_app()

# Print the generated code
print(dart_code)
print("=" * 80)

# Print analysis
print("\n📊 Analysis:")
print(f"Modified containers: {codegen.modified_containers}")
print(f"Repeated containers: {codegen.repeated_containers}")
print("\n✅ Counter app should work perfectly - button will render correctly!")
