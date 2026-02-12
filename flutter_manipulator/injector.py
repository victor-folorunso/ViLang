# platform_bridge/project_injector.py
from pathlib import Path
import json
from ruamel.yaml import YAML


class ProjectInjector:
    """
    Manages injection of Vi runtime code and assets into Flutter project.
    Coordinates different file manipulators.
    """
    
    def __init__(self, project_dir: Path, widget_tree: dict):
        self.project_dir = project_dir
        self.widget_tree = widget_tree
        
        self.main_dart = MainDartInjector(project_dir)
        self.pubspec = PubspecInjector(project_dir)
        self.assets = AssetsInjector(project_dir)
    
    def inject_all(self):
        """Inject all Vi runtime components into Flutter project"""
        print("Injecting Vi runtime...")
        
        # 1. Create assets and save widget tree
        self.assets.save_widget_tree(self.widget_tree)
        
        # 2. Update pubspec.yaml to include assets
        self.pubspec.add_assets()
        
        # 3. Replace main.dart with Vi runtime
        self.main_dart.inject_runtime()
        
        print("✓ Vi runtime injected successfully")


class MainDartInjector:
    """Handles main.dart manipulation"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.main_dart_path = project_dir / "lib" / "main.dart"
    
    def inject_runtime(self):
        """Replace main.dart with Vi runtime code"""
        if not self.main_dart_path.exists():
            raise FileNotFoundError(f"main.dart not found at {self.main_dart_path}")
        
        runtime_code = self._get_runtime_code()
        self.main_dart_path.write_text(runtime_code)
        print("  ✓ main.dart updated")
    
    def _get_runtime_code(self) -> str:
        """Get Vi runtime Dart code"""
        # Get path relative to Vi compiler installation directory
        # __file__ is the path to this injector.py file
        # Use .resolve() to get absolute path regardless of CWD
        vi_compiler_dir = Path(__file__).resolve().parent.parent  # Go up from flutter_manipulator/ to ViLang/
        template_path = vi_compiler_dir / "flutter_template" / "lib" / "main.dart"
        
        if template_path.exists():
            return template_path.read_text()
        else:
            raise FileNotFoundError(
                f"Runtime template not found!\n\n"
                f"Expected location: {template_path}\n"
                f"Vi compiler directory: {vi_compiler_dir}\n"
                f"Current working directory: {Path.cwd()}\n\n"
                f"Please ensure the 'flutter_template' directory exists in your Vi installation."
            )

class PubspecInjector:
    """Handles pubspec.yaml manipulation"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.pubspec_path = project_dir / "pubspec.yaml"
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=2, offset=0)

    def add_assets(self):
        """Add assets section to pubspec.yaml if not present"""
        if not self.pubspec_path.exists():
            raise FileNotFoundError(f"pubspec.yaml not found at {self.pubspec_path}")
        
        with open(self.pubspec_path) as f:
            data = self.yaml.load(f)
        
        # Ensure flutter.assets exists
        data.setdefault("flutter", {}).setdefault("assets", [])
        
        # Add asset if missing
        if "assets/vi_tree.json" not in data["flutter"]["assets"]:
            data["flutter"]["assets"].append("assets/vi_tree.json")
            with open(self.pubspec_path, "w") as f:
                self.yaml.dump(data, f)
            print("  ✓ pubspec.yaml updated")
        else:
            print("  ✓ pubspec.yaml already configured")

class AssetsInjector:
    """Handles assets folder and files"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.assets_dir = project_dir / "assets"
    
    def save_widget_tree(self, widget_tree: dict):
        """Save widget tree as JSON in assets folder"""
        # Create assets directory
        self.assets_dir.mkdir(exist_ok=True)
        
        # Save tree as JSON
        tree_file = self.assets_dir / "vi_tree.json"
        with open(tree_file, 'w') as f:
            json.dump(widget_tree, f, indent=2)
        
        print("  ✓ Widget tree saved to assets/vi_tree.json")