from pathlib import Path
from platform_bridge.executor import Executor
from codegen.dart_codegen import DartCodegen
import subprocess
import shutil

class Compiler:
    """Vi Compiler - Creates standalone Flutter apps"""
    
    def __init__(self, ast, target, output_dir=None):
        self.ast = ast
        self.target = target
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "build"

    def create(self):
        print(f"Creating Vi app for {self.target}...")
        
        Ex = Executor()
        app_dir = Ex.create_project(self.output_dir, project_name="vi_app")

        codegen = DartCodegen(self.ast)
        dart_code = codegen.generate_full_app()

        main_dart = app_dir / "lib" / "main.dart"
        main_dart.write_text(dart_code)
        print("✓ Dart code generated")

        if codegen.config_icon:
            self._setup_app_icon(codegen.config_icon, app_dir)

        if codegen.splash_attrs:
            self._setup_native_splash(codegen.splash_attrs, app_dir)

        Ex.pub_get(app_dir)

        if self.target == "android":
            Ex.build_apk(app_dir)
        elif self.target == "ios":
            Ex.build_ios(app_dir)
        elif self.target == "web":
            Ex.build_web(app_dir)
        
        print(f"✓ Build complete! Output: {app_dir}")

    def _setup_app_icon(self, icon_path_expr, app_dir):
        """Configure flutter_launcher_icons for production build"""
        raw = icon_path_expr.get('value', '') if icon_path_expr.get('type') == 'literal' else ''
        if not raw:
            return

        icon_src = Path(raw) if Path(raw).is_absolute() else \
                   Path.cwd() / raw.replace('\\', '/')

        if not icon_src.exists():
            print(f"⚠️  Icon not found: {icon_src}")
            return

        assets_dir = app_dir / 'assets'
        assets_dir.mkdir(exist_ok=True)
        shutil.copy2(icon_src, assets_dir / 'icon.png')

        self._inject_pubspec(app_dir, {
            'flutter_launcher_icons': '^0.13.1',
        }, extra_yaml="\nflutter_launcher_icons:\n  android: true\n  ios: true\n  image_path: \"assets/icon.png\"\n")

        subprocess.run(['flutter', 'pub', 'get'], cwd=app_dir, capture_output=True)
        result = subprocess.run(
            ['flutter', 'pub', 'run', 'flutter_launcher_icons'],
            cwd=app_dir, capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✓ App icon configured")
        else:
            print(f"⚠️  Icon generation failed: {result.stderr[:200]}")

    def _setup_native_splash(self, splash_attrs, app_dir):
        """Configure flutter_native_splash for production build.
        Native splash shows before the Flutter engine starts — proper OS-level splash."""
        color_expr = splash_attrs.get('color')
        color_hex = self._color_to_hex(color_expr)

        image_expr = splash_attrs.get('image') or splash_attrs.get('logo')
        image_path = None
        if image_expr:
            raw = image_expr.get('value', '') if image_expr.get('type') == 'literal' else ''
            if raw:
                src = Path(raw) if Path(raw).is_absolute() else Path.cwd() / raw.replace('\\', '/')
                if src.exists():
                    assets_dir = app_dir / 'assets'
                    assets_dir.mkdir(exist_ok=True)
                    dest = assets_dir / 'splash.png'
                    shutil.copy2(src, dest)
                    image_path = 'assets/splash.png'

        splash_yaml = "\nflutter_native_splash:\n"
        splash_yaml += f"  color: \"{color_hex}\"\n"
        if image_path:
            splash_yaml += f"  image: {image_path}\n"
        splash_yaml += "  android_12:\n"
        splash_yaml += f"    color: \"{color_hex}\"\n"

        self._inject_pubspec(app_dir, {
            'flutter_native_splash': '^2.3.10',
        }, extra_yaml=splash_yaml)

        subprocess.run(['flutter', 'pub', 'get'], cwd=app_dir, capture_output=True)
        result = subprocess.run(
            ['dart', 'run', 'flutter_native_splash:create'],
            cwd=app_dir, capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✓ Native splash screen configured")
        else:
            print(f"⚠️  Native splash setup failed: {result.stderr[:200]}")

    def _inject_pubspec(self, app_dir, deps: dict, extra_yaml: str = ''):
        pubspec = app_dir / 'pubspec.yaml'
        content = pubspec.read_text()
        for pkg, version in deps.items():
            if pkg not in content:
                content = content.replace(
                    'dependencies:\n  flutter:\n    sdk: flutter\n',
                    f'dependencies:\n  flutter:\n    sdk: flutter\n  {pkg}: {version}\n'
                )
        if extra_yaml and extra_yaml.strip().split(':')[0].strip() not in content:
            content += extra_yaml
        pubspec.write_text(content)

    def _color_to_hex(self, color_expr):
        """Convert Vi color expression to hex string for YAML config"""
        if not color_expr:
            return '#ffffff'
        named = {
            'white': '#ffffff', 'black': '#000000', 'red': '#f44336',
            'blue': '#2196f3', 'green': '#4caf50', 'yellow': '#ffeb3b',
            'purple': '#9c27b0', 'orange': '#ff9800', 'pink': '#e91e63',
            'gray': '#9e9e9e',
        }
        if color_expr.get('type') == 'var':
            return named.get(color_expr['name'], '#ffffff')
        if color_expr.get('type') == 'call':
            func = color_expr.get('function', {})
            if func.get('name') == 'rgb':
                args = color_expr.get('args', [])
                if len(args) == 3:
                    r = int(args[0].get('value', 0))
                    g = int(args[1].get('value', 0))
                    b = int(args[2].get('value', 0))
                    return f'#{r:02x}{g:02x}{b:02x}'
        return '#ffffff'
