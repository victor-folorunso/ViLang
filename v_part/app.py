from lib import *

code_instance = Format_code(text_code)
code_instance.run_format_wizard()

containers = code_instance.containers

drawable_objects = {}
for container in containers:
    objects = container.split("=",1)
    drawable_objects[objects[0]] = objects[1]
 
print(drawable_objects)
