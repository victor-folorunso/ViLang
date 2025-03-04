import re


class Format_code:
    def __init__(self, code_text: str):
        self.code_text = code_text
        self.tokens = []

        self.variables = []
        self.functions = []
        self.containers = []

        self.objects_list = []

    def run_format_wizard(self):
        self.include_all_files()
        self.remove_comments()
        self.extract_variables()
        self.remove_spaces()
        self.extract_containers_and_functions()
        self.assign_container_attributes()

        self.check_objects_attributes()

    def check_objects_attributes(self):
        for i in self.objects_list:
            print(f"object {i.id}, color {i.color}")

    def cleanup(self, string):
        string = string.removeprefix("{")
        string = string.removesuffix("}")
       
        return string

    def assign_container_attributes(self):
        containers = self.containers
        for item in containers:
            value_keys = []
            value_values = []
            cache = ""
            braces = 0
            brackets = 0
            locks = 0
            lock_chars = ["{", "}", "[", "]"]

            blob = item.split("=", 1)
            key = [blob[0]][0]
            value = [blob[1]][0]
            value = self.cleanup(value)

            for char in value:
                if char in lock_chars:
                    if char == "{":
                        locks += 1

                    if char == "}":
                        locks -= 1
                            

                    if char == "[":
                        locks += 1
                    if char == "]":
                        locks -= 1

                if locks == 0:
                    if char == ":":
                        value_keys.append(cache)
                        cache = ""
                        continue  # thiqs iqs to enqsure cache not += :
                    if char == ",":
                        value_values.append(cache)
                        cache = ""
                        continue  # thiqs iqs to enqsure cache not += ,

                cache += char

            assert len(value_keys) == len(value_values),"len value_keys != len value_values"
            
            instance = Container()
            instance.id = key
            i = 0
            for valuekey in value_keys:                               #could alqso uqse value_valueqs qsince they are of qsame len
                assert value_keys[i] in Container.default_properties, f"{value_keys[i]} is not a default attribute"
                print(value_keys[i],value_values[i])
                setattr(instance,value_keys[i],value_values[i])
                i += 1

            self.objects_list.append(instance)

    def extract_containers_and_functions(self):

        cache = ""
        braces = 0
        for char in self.code_text:
            cache += char
            if char == "{":
                braces += 1
            if char == "}":
                braces -= 1
                if (braces == 0) and (cache not in self.tokens):
                    self.tokens.append(cache)
                    cache = ""

        self.functions = [token for token in self.tokens if "){" in token]
        self.tokens = [token for token in self.tokens if token not in self.functions]

        self.containers = [token for token in self.tokens if "={" in token]
        self.tokens = [token for token in self.tokens if token not in self.containers]

        assert self.tokens == []

    def extract_variables(self):
        variable_pattern = r"\b([a-zA-Z][a-zA-Z0-9_]*)\s*=\s*([^\n]+)"
        matches = re.findall(variable_pattern, self.code_text)
        self.code_text = re.sub(variable_pattern, "", self.code_text)

        for variable in matches:
            self.variables.append(variable)

    def remove_spaces(self):
        self.code_text = re.sub(r"\s", "", self.code_text)

    def include_all_files(self):
        # Regular expression to match "from ... include ..." and "include ..."
        from_include_pattern = r"(from\s+\S+\s+include\s+\S+.*)"
        include_pattern = r"(include\s+\S+.*)"

        from_include_list = re.findall(from_include_pattern, self.code_text)
        for include_statement in from_include_list:
            self.code_text = re.sub(include_statement, "", self.code_text)

        include_list = re.findall(include_pattern, self.code_text)
        for include_statement in include_list:
            self.code_text = re.sub(include_statement, "", self.code_text)

    def remove_comments(self):
        # remove multiline comments first
        multiline_comment_pattern = r"<#.*?#>"
        self.code_text = re.sub(
            multiline_comment_pattern, "", self.code_text, flags=re.DOTALL
        )

        # remove single line comments
        single_comment_pattern = r"#.*?\n"
        self.code_text = re.sub(
            single_comment_pattern, "", self.code_text, flags=re.DOTALL
        )


class Container:
    default_properties = {
        "id": "",
        "color": "red",
        "draw_hide": "default draw_hide",
        "shape": "default shape",
        "height": "default height",
        "width": "default width",
        "event_listeners": [],
        "children": [],
        "position_xy": [20, 20],
    }

    def __init__(self, **kwargs):
        # Merge defaults with provided arguments
        properties = {**self.default_properties, **kwargs}
        self.id = properties["id"]
        self.color = properties["color"]
        self.draw_hide = properties["draw_hide"]
        self.shape = properties["shape"]
        self.height = properties["height"]
        self.width = properties["width"]
        self.event_listeners = properties["event_listeners"]
        self.children = properties["children"]
        self.position_xy = properties["position_xy"]


text_code = """
include lib
from folder.subfolder include file

_scree = {
  color: red,
  draw_hide:draw,
  shape: square,
  height: 128,
  width: 72,
  position_xy: [20,20],
}    

greet_user(){
  //do qsomething
}

change_color(){
  i = 1
  _nilo.color: green
  _scree = {
    color: red,
    draw_hide: draw,
  }
}

containers = [_container1 , _scree]  
    
main _screen = {                         
  color: green,              
  draw_hide: draw,         
  shape: circle,
  height: 1280,
  width: 720,
  position_xy: [20,20],
  children: [
    _nilo = {
      color: blue,
      draw_hide: hide,
      shape: square,
      height: 128,
      width: 72,
      children: containers,
    },
    _scree,
  ],
  event_listeners: { 
    on_click: greet_user(),
    
  },
}"""
