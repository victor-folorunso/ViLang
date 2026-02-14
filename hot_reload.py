"""
Hot Reload Watcher for Vi Language
Watches .vi files and regenerates Dart code on changes
Direct AST → Dart pipeline
"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser import Parser
from codegen.dart_codegen import DartCodegen


class ViFileHandler(FileSystemEventHandler):
    """Handles .vi file changes"""
    
    def __init__(self, vi_file, app_dir, flutter_process):
        self.vi_file = Path(vi_file).resolve()
        self.app_dir = Path(app_dir)
        self.flutter_process = flutter_process
        self.last_modified = 0
        self.debounce_seconds = 0.5
    
    def on_modified(self, event):
        if event.src_path.endswith('.vi'):
            # Debounce rapid file changes
            current_time = time.time()
            if current_time - self.last_modified < self.debounce_seconds:
                return
            self.last_modified = current_time
            
            print(f"\n🔄 Detected change in {event.src_path}")
            self.regenerate_dart()
    
    def regenerate_dart(self):
        """Regenerate Dart code from Vi source - Direct AST → Dart"""
        try:
            # Parse Vi file to AST
            parser = Parser(str(self.vi_file))
            ast = parser.parse()
            
            # Generate Dart code directly from AST
            codegen = DartCodegen(ast)
            dart_code = codegen.generate_full_app()
            
            # Write to main.dart
            main_dart = self.app_dir / "lib" / "main.dart"
            main_dart.write_text(dart_code)
            
            print("✓ Dart code regenerated")
            
            # Trigger Flutter hot reload by sending 'r' to the process
            if self.flutter_process and self.flutter_process.poll() is None:
                self.flutter_process.stdin.write(b'r\n')
                self.flutter_process.stdin.flush()
                print("✓ Hot reload triggered")
            
        except Exception as e:
            print(f"❌ Error regenerating code: {e}")


class HotReloadWatcher:
    """Watches Vi files and triggers hot reload"""
    
    def __init__(self, vi_file, app_dir, flutter_process):
        self.vi_file = Path(vi_file).resolve()
        self.app_dir = Path(app_dir)
        self.flutter_process = flutter_process
        self.observer = None
    
    def start(self):
        """Start watching for file changes"""
        event_handler = ViFileHandler(self.vi_file, self.app_dir, self.flutter_process)
        self.observer = Observer()
        
        # Watch the directory containing the Vi file
        watch_dir = self.vi_file.parent
        self.observer.schedule(event_handler, str(watch_dir), recursive=False)
        
        self.observer.start()
        print(f"👁️  Watching {self.vi_file.name} for changes...")
        print("   Press Ctrl+C to stop")
    
    def stop(self):
        """Stop watching"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
