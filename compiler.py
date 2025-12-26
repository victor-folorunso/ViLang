class Compiler:
    """Stage 3: Compile widget tree into standalone app"""
    def __init__(self, tree, target):
        self.tree = tree
        self.target = target

    def create(self):
        print(f"Creating Vi app for {self.target}...")