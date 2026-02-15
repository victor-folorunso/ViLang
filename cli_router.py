from pathlib import Path
from parser import Parser
from runtime import Runtime
from compiler import Compiler

class Vi:
    """Main entry for Vi CLI"""
    
    def __init__(self):
        self.filepath = Path.cwd() / "main.vi"
        self.ast = None

    def run(self):
        """Run Vi app on emulator with hot restart on file changes"""
        parser = Parser(self.filepath)
        self.ast = parser.parse()
        
        runtime = Runtime(self.ast, vi_file=self.filepath)
        runtime.run()

    def create(self, target):
        """Compile Vi app for target platform"""
        parser = Parser(self.filepath)
        self.ast = parser.parse()
        
        compiler = Compiler(self.ast, target)
        compiler.create()
