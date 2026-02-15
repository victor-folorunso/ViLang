from pathlib import Path
import tempfile
from platform_bridge.executor import Executor
from codegen.dart_codegen import DartCodegen
from hot_reload import HotRestartWatcher

class Runtime:
    """Vi Runtime - Generates Dart and runs on emulator"""

    def __init__(self, ast, vi_file=None):
        self.ast = ast
        self.vi_file = vi_file
        self.app_dir = None

    def run(self):
        temp_dir = Path(tempfile.mkdtemp(prefix="vi_run_"))

        Ex = Executor()
        self.app_dir = Ex.create_project(temp_dir)
        Ex.pub_get(self.app_dir)
        
        self.generate_dart_code()
        
        flutter_process = Ex.run_app_interactive(self.app_dir, return_process=True)
        
        watcher = HotRestartWatcher(self.vi_file, self.app_dir, flutter_process)
        watcher.start()
        
        try:
            flutter_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            watcher.stop()
            flutter_process.terminate()

    def generate_dart_code(self):
        """Generate Dart code directly from AST"""
        codegen = DartCodegen(self.ast)
        dart_code = codegen.generate_full_app()

        main_dart = self.app_dir / "lib" / "main.dart"
        main_dart.write_text(dart_code)
        print("✓ Dart code generated")

        if codegen.config_icon:
            self._setup_app_icon(codegen.config_icon)

    def _setup_app_icon(self, icon_path_expr):
        """Configure flutter_launcher_icons for the project"""
        import shutil

        # Resolve icon path relative to .vi file
        raw = icon_path_expr.get('value', '') if icon_path_expr.get('type') == 'literal' else ''
        if not raw:
            return

        icon_src = Path(raw) if Path(raw).is_absolute() else \
                   Path(self.vi_file).parent / raw.replace('\\', '/')

        if not icon_src.exists():
            print(f"⚠️  Icon not found: {icon_src}")
            return

        # Copy to project assets
        assets_dir = self.app_dir / 'assets'
        assets_dir.mkdir(exist_ok=True)
        dest = assets_dir / 'icon.png'
        shutil.copy2(icon_src, dest)

        # Append flutter_launcher_icons to pubspec.yaml
        pubspec = self.app_dir / 'pubspec.yaml'
        content = pubspec.read_text()

        if 'flutter_launcher_icons' not in content:
            content += "\nflutter_launcher_icons:\n  android: true\n  ios: true\n  image_path: \"assets/icon.png\"\n"
            # Add dependency
            content = content.replace(
                'dependencies:\n  flutter:\n    sdk: flutter\n',
                'dependencies:\n  flutter:\n    sdk: flutter\n  flutter_launcher_icons: ^0.13.1\n'
            )
            pubspec.write_text(content)

        # Run icon generation
        import subprocess
        subprocess.run(['flutter', 'pub', 'get'], cwd=self.app_dir, capture_output=True)
        result = subprocess.run(
            ['flutter', 'pub', 'run', 'flutter_launcher_icons'],
            cwd=self.app_dir, capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✓ App icon configured")
        else:
            print(f"⚠️  Icon generation failed: {result.stderr[:200]}")
