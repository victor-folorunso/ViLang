from pathlib import Path
import tempfile
from platform_bridge.executor import Executor
from codegen.dart_codegen import DartCodegen
from hot_reload import HotReloadWatcher

class Runtime:
    """Vi Runtime - Generates Dart and runs on emulator"""

    def __init__(self, ast, vi_file=None):
        self.ast = ast
        self.vi_file = vi_file
        self.app_dir = None

    def run(self, hot_reload=False):
        temp_dir = Path(tempfile.mkdtemp(prefix="vi_run_"))

        Ex = Executor()
        self.app_dir = Ex.create_project(temp_dir)
        Ex.pub_get(self.app_dir)
        
        # Generate Dart code directly from AST
        self.generate_dart_code()
        
        # Run the app
        if hot_reload and self.vi_file:
            flutter_process = Ex.run_app_interactive(self.app_dir, return_process=True)
            
            # Start hot reload watcher
            watcher = HotReloadWatcher(self.vi_file, self.app_dir, flutter_process)
            watcher.start()
            
            try:
                # Keep process running
                flutter_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping...")
                watcher.stop()
                flutter_process.terminate()
        else:
            Ex.run_app_interactive(self.app_dir)
    
    def generate_dart_code(self):
        """Generate Dart code directly from AST"""
        codegen = DartCodegen(self.ast)
        dart_code = codegen.generate_full_app()
        
        # Write to main.dart
        main_dart = self.app_dir / "lib" / "main.dart"
        main_dart.write_text(dart_code)
        
        print("✓ Dart code generated")
