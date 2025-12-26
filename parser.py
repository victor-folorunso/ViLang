class Parser:
    """Stage 1: Parse .vi file into json"""

    def __init__(self, filepath):
        self.filepath = filepath
        self.tree = None

    def parse(self):
        print(f"Parsing '{self.filepath}'...")
        self.tree = {
            "type": "container",
            "width": "max",
            "height": "max",
            "color": "blue",
            "children": [
                {"type": "container", "width": 200, "height": 200, "color": "red"}
            ],
        }
        return self.tree
    
    #step 1: collect all imports into main.vi
    #step 2: parse main.vi into json
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
