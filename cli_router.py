from pathlib import Path
from parser import Parser
from runtime import Runtime
from compiler import Compiler

class Vi:
    """Main entry for CLI"""
    def __init__(self):
        self.filepath = Path.cwd() / "main.vi"
        self.tree = None

    def run(self):
        parser = Parser(self.filepath)
        self.tree = parser.parse()
        runtime = Runtime(self.tree)
        runtime.run()

    def create(self, target):
        parser = Parser(self.filepath)
        self.tree = parser.parse()
        compiler = Compiler(self.tree, target)
        compiler.create()