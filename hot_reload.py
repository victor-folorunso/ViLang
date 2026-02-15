"""
Hot Restart Watcher for Vi Language
Watches .vi files and triggers a full Flutter hot restart on changes.
Hot restart is used (not hot reload) because Vi regenerates the entire
main.dart on every save — hot reload can't safely patch a fully changed tree.
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
            current_time = time.time()
            if current_time - self.last_modified < self.debounce_seconds:
                return
            self.last_modified = current_time
            
            print(f"\n🔄 Detected change in {event.src_path}")
            self.regenerate_and_restart()
    
    def regenerate_and_restart(self):
        """Regenerate Dart code from Vi source then hot restart Flutter"""
        try:
            parser = Parser(str(self.vi_file))
            ast = parser.parse()
            
            codegen = DartCodegen(ast)
            dart_code = codegen.generate_full_app()
            
            main_dart = self.app_dir / "lib" / "main.dart"
            main_dart.write_text(dart_code)
            
            print("✓ Dart code regenerated")
            
            if self.flutter_process and self.flutter_process.poll() is None:
                # Capital R = hot restart (full VM reboot, clears all state)
                self.flutter_process.stdin.write('R\n')
                self.flutter_process.stdin.flush()
                print("✓ Hot restart triggered")
            
        except Exception as e:
            print(f"❌ Error regenerating code: {e}")


class HotRestartWatcher:
    """Watches Vi files and triggers hot restart on change"""
    
    def __init__(self, vi_file, app_dir, flutter_process):
        self.vi_file = Path(vi_file).resolve()
        self.app_dir = Path(app_dir)
        self.flutter_process = flutter_process
        self.observer = None
    
    def start(self):
        event_handler = ViFileHandler(self.vi_file, self.app_dir, self.flutter_process)
        self.observer = Observer()
        
        watch_dir = self.vi_file.parent
        self.observer.schedule(event_handler, str(watch_dir), recursive=False)
        
        self.observer.start()
        print(f"  Watching {self.vi_file.name} for changes (hot restart on save)...")
        print("   Press Ctrl+C to stop")
    
    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
