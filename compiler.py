from pathlib import Path
from platform_bridge.executor import Executor
from codegen.dart_codegen import DartCodegen

class Compiler:
    """Vi Compiler - Creates standalone Flutter apps"""
    
    def __init__(self, ast, target, output_dir=None):
        self.ast = ast
        self.target = target
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "build"

    def create(self):
        print(f"Creating Vi app for {self.target}...")
        
        # Create Flutter project
        Ex = Executor()
        app_dir = Ex.create_project(self.output_dir, project_name="vi_app")
        Ex.pub_get(app_dir)
        
        # Generate Dart code directly from AST
        self.generate_dart_code(app_dir)
        
        # Build for target platform
        if self.target == "android":
            Ex.build_apk(app_dir)
        elif self.target == "ios":
            Ex.build_ios(app_dir)
        elif self.target == "web":
            Ex.build_web(app_dir)
        
        print(f"✓ Build complete! Output: {app_dir}")
    
    def generate_dart_code(self, app_dir):
        """Generate Dart code directly from AST"""
        codegen = DartCodegen(self.ast)
        dart_code = codegen.generate_full_app()
        
        # Write to main.dart
        main_dart = app_dir / "lib" / "main.dart"
        main_dart.write_text(dart_code)
        
        print("✓ Dart code generated")
