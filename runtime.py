from pathlib import Path
import tempfile
from platform_bridge.executor import Executor
from flutter_manipulator.injector import ProjectInjector

class Runtime:
    """Stage 2: Run widget tree dynamically on emulator"""

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        temp_dir = Path(tempfile.mkdtemp(prefix="vi_run_"))

        Ex = Executor()
        app_dir = Ex.create_project(temp_dir)
        Ex.pub_get(app_dir)
        
        injector = ProjectInjector(app_dir, self.tree)
        injector.inject_all()
        
        Ex.run_app_interactive(app_dir)