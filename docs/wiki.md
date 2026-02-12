# Vi Language Documentation
Overview
Vi is a flexible, compiler-powered cross-platform app development language designed for simplicity and expressiveness. Write once in Vi, compile to responsive apps that adapt to mobile, tablet, and desktop screens.
Philosophy:Everything is possible - the language adapts to your intent through intelligent interpretation.
Workflow:`code.v` → Vi Compiler → Platform-specific app (web, mobile, desktop)
Vi code is processed by the Vi compiler which interprets your intent and generates optimized, platform-specific code.
Comments
Multi-line and single-line comments use the same syntax:
```vi
<# 
  This is a multi-line comment.
  It can span multiple lines.
#>

<# This is a single-line comment #>
```
Naming Conventions
Vi follows Python-style naming conventions:
- snake_casefor variables, functions, and container names
- lowercasefor built-in keywords
Examples:`main_screen`, `task_list`, `add_task()`, `user_profile`
Core Concept: Containers
Everything in Vi is a container. Containers are the building blocks of your UI and are styled using attributes (key-value pairs).
Basic Container Syntax
```vi
container_name:
  attribute1 = value1
  attribute2 = value2
  attribute3 = value3
```
Nested Containers (Parent-Child Relationships)
```vi
parent_container:
  color = blue
  children = [child1, child2]
child1:
  <# This is a child of parent_container #>
  color = red
  height = 50
child2:
  color = green
  width = 100
```
Key Concepts:
- Parent:The outer container
- Children:Containers nested inside a parent
- Children inherit certain properties from parents (unless explicitly overridden)
- By default, a child cannot be wider or taller than its parent, especially when the parent has a definite height
- All inherited styles pass down from one generation to the next until explicitly overridden or until a component has its own defaults
Multiple Containers with Same Style
Use commas to apply the same styling to multiple containers:
```vi
container1, container2, container3:
  color = red
  shape = square
  height = 100
  width = 100
```
Type System and Inference
Vi uses context-based type inference. You never declare types explicitly - the Vi compiler determines whether something is a function, container, or variable based on how it's used.
How Vi Determines Types
Containers:
```vi
<# Used in children arrays or styled with attributes #>
main_screen:
  children = [header, body]
header:
  color = blue
```
Functions:
```vi
<# Contains logic, performs actions, may return values #>
add_task(text):
  items.add({ id: 1, text: text, done: false })
get_color(task):
  if (task.done):
    return green
  else:
    return gray
```
Variables:
```vi
<# Assigned values directly #>
current_player = "X"
game_over = false
items = [1, 2, 3]
```
Parameterized Containers:
Containers can accept parameters and be reused with different data:
```vi
<# Define a parameterized container #>
user_card(user):
  color = white
  text_content = user.name
  height = 50
<# Use it #>
main_screen:
  children = [user_card(john), user_card(sarah)]
```
The Vi compiler uses context to determine if `user_card(data)` is a container or function - no parentheses distinction needed.
Data Structures
Arrays (Lists)
```vi
my_list = [item1, item2, item3]
numbers = [1, 2, 3, 4, 5]
<# Accessing elements #>
first_item = my_list[0]
second_number = numbers[1]
```
Objects (Dictionaries)
```vi
user = { 
  name: "Alice", 
  age: 25, 
  active: true 
}
<# Accessing properties #>
user_name = user.name
user_age = user.age
<# Modifying properties #>
user.age = 26
```
Array of Objects
```vi
items = [
  { id: 1, text: "Task one", done: false },
  { id: 2, text: "Task two", done: true },
  { id: 3, text: "Task three", done: false }
]
```
Array Methods
```vi
<# Add to array #>
items.add(new_item)
<# Remove from array #>
items.remove(target_item)
<# Get index of item #>
index = items.index(target_item)
<# Get item by index #>
item = items[0]
<# Get length #>
count = length(items)
```
Boolean Operations
```vi
<# Toggle boolean #>
value = !value
task.done = !task.done
<# Comparisons #>
if (x > 10):
  action
if (user.age >= 18):
  allow_access()
```
Functions
User-Defined Functions
Functions in Vi contain logic and perform actions:
```vi
function_name():
  <# function logic here #>
  code_statements
function_with_params(param1, param2):
  <# use param1 and param2 here #>
  result = param1 + param2
  return result
```
Calling functions:
```vi
function_name()
result = function_with_params(10, 20)
```
Built-in Functions
Built-in functions are called directly without definition:
- `visit(url)` - Navigate to a URL
- `play(url)` - Play media from URL
- `wait_sec(seconds)` - Delay execution
- `random(number in range(min, max))` - Generate random number
- `length(array)` - Get array length
Examples:
```vi
visit("https://example.com")
play("\assets\music.mp3")
wait_sec(3)
random_number = random(number in range(1, 100))
array_size = length(my_list)
```
Control Flow
Conditionals
```vi
<# If statement (parentheses optional) #>
if condition:
  action
if (user.age > 18):
  show_content = true
<# If-else #>
if (condition):
  action1
else:
  action2
<# If-else if-else #>
if (score > 90):
  grade = "A"
else if (score > 80):
  grade = "B"
else:
  grade = "C"
```
Inline Ternary Operator
```vi
value = true_value if (condition) else false_value
status = "online" if (user.active) else "offline"
icon = "check_circle" if (task.done) else "circle_outline"
color = green[600] if (task.done) else gray[200]
```
Loops
```vi
<# For loop #>
for item in array:
  action
for user in users:
  display(user.name)
for cell in grid.children:
  cell:
    color = blue
```
The Main Container
Every Vi app has a main container- the entry point that the compiler parses first.
```vi
main container_name:
  height = max
  width = max
  children = [header, body, footer]
```
Rules:
- Define using the `main` keyword followed by container name
- Must be in a `main.v` file in your project's `lib` folder
- All other containers are drawn directly or indirectly inside the main container
- Auxiliary containers and functions are imported into `main.v` using the `import` keyword
Importing
```vi
<# Import specific containers/functions #>
from file.v import container_name
from file.v import function_name
<# Import everything #>
from file.v import *
from file.v import all
<# Import entire file #>
import file.v
```
Note:All import paths are relative to the project root directory.
Container Attributes
Attributes define how containers look and behave. No units needed - values are relative to the parent container by default.
Attribute Syntax
```vi
<# Single attribute #>
attribute: value
<# Multiple attributes #>
attribute1: value1
attribute2: value2
<# Multiple values #>
attribute1, attribute2: value1, value2
```
Attribute Reference
Display & Visibility
visibility
- Type:`true` | `false`
- Default:`true`
- Description:Controls whether container is visible
```vi
visibility = true   <# visible #>
visibility = false  <# hidden #>
```
Layout & Sizing
width
- Type:number | `max`
- Default:`10`
- Description:Width of container. Must be specified unless container is scrollable.
```vi
width = 100
width = max  <# fills parent width #>
```
height
- Type:number | `max` | `auto`
- Default:`auto`
- Description:Height of container. Required for fixed layouts (games, non-scrolling apps).
```vi
height = 50
height = max   <# fills parent height #>
height = auto  <# adjusts to content #>
```
shape
- Type:`square` | `circle` | `sqircle` | `cube`
- Default:`square`
- Description:Shape of the container. `cube` is for 3D shapes.
```vi
shape = circle
shape = sqircle  <# rounded square #>
shape = cube     <# 3D shape #>
```
position
- Type:keyword | coordinates
- Keywords:`left`, `right`, `top`, `bottom`, `middle`
- Coordinates:`[X, Y]` or `[X, Y, Z]` (percentages 0-100, not pixels)
- Description:Position of container within parent
```vi
position = top
position = [50, 50]      <# center at 50% width, 50% height #>
position = [25, 75, 10]  <# 3D position #>
```
Appearance
color
- Type:color name | `rgb()` | color with shade
- Description:Background color of container
```vi
color = red
color = rgb(255, 0, 0)
color = blue[600]   <# Material Design-style shades #>
color = gray[100]
```
background_image
- Type:URL path (relative to project root)
- Description:Background image for container
```vi
background_image = \assets\hero_image.png
background_image = \assets\textures\wood.jpg
```
background_image_blur
- Type:number (0 to 1)
- Description:Blur intensity for background image. 0 = no blur, 1 = fully blurred
```vi
background_image_blur = 0.5
background_image_blur = 1
```
z_index
- Type:number
- Description:Controls layering (higher values appear on top)
```vi
z_index = 0  <# bottom layer #>
z_index = 1  <# draws over z_index 0 #>
z_index = 5  <# draws over lower z_index values #>
```
Note:z_index values should be sequential or the compiler will report an error.
Content
text_content
- Type:string (supports multi-line and variable interpolation)
- Description:Text displayed in container
```vi
text_content = "Hello World"
text_content = "Hello {user.name}"  <# variable interpolation #>
text_content = "Hello {{user.name}}" <# literal: Hello {user.name} #>
text_content = "This text can span
                multiple lines in the editor"
```
text_content_font
- Type:string (font name or size)
- Description:Font family or size for text
```vi
text_content_font = "16"
text_content_font = "Arial"
```
text_content_style
- Type:array of style properties
- Description:Additional styling for text content
```vi
text_content_style = [font: bold, font_size: 16]
text_content_style = [font: italic, color: blue]
text_content_style = [font: bold, font_size: 20, color: rgb(100, 100, 100)]
```
audio_content
- Type:URL to audio file (relative to project root)
- Description:Audio file to play
```vi
audio_content = \assets\music.mp3
```
video_content
- Type:URL to video file (relative to project root)
- Description:Video file to display
```vi
video_content = \assets\intro.mp4
```
Note:All font sizes, widths, and layouts are automatically responsive and adapt to screen size. The layout may change depending on screen dimensions.
Content Alignment & Padding
Important Terminology:
- selfattributes: Apply to the container itself
- childrenattributes: Apply to child containers within the container
align_self
- Type:keyword or combination
- Keywords:`center`, `centre`, `top`, `bottom`, `left`, `right`
- Description:Alignment of the container within its parent
```vi
align_self = centre
align_self = center  <# same as centre #>
align_self = bottom, right  <# positioned at bottom-right corner #>
```
align_children
- Type:keyword
- Keywords:`center`, `centre`, `left`, `right`, `top`, `bottom`
- Description:Alignment of child containers within this container
```vi
align_children = center
align_children = left
```
self_padding_top, self_padding_bottom, self_padding_left, self_padding_right
- Type:number
- Description:Padding for specific sides of the container itself
```vi
self_padding_top = 5
self_padding_bottom = 10
self_padding_left = 8
self_padding_right = 8
```
children_padding
- Type:number
- Description:Spacing between child containers
```vi
children_padding = 10
```
children_padding_top, children_padding_bottom, children_padding_left, children_padding_right
- Type:number
- Description:Padding for specific sides of the children area
```vi
children_padding_top = 5
children_padding_bottom = 10
```
children_padding_color
- Type:color name | `rgb()` | color with shade
- Description:Color of the padding area for children
```vi
children_padding_color = white
children_padding_color = rgb(240, 240, 240)
```
Children Management
children
- Type:array of container names or parameterized containers
- Description:List of child containers to render
```vi
children = [header, body, footer]
children = [user_card(user1), user_card(user2)]
```
Nested Children Definition:
You can define children inline within the children array for cleaner code:
```vi
main main_screen:
  height = max
  width = max
  children = [
    header:
      height = 15
      color = blue,
    body:
      height = max
      children = [content],
    footer
  ]
<# Separately defined containers are still accessible #>
footer:
  height = 10
  color = gray
```
Scope Rules:
- Containers defined inline within `children` arrays are locally scopedto that parent
- They cannot be accessed by sibling containers or containers outside the parent
- To access a locally scoped container from outside, reference it through its public parent: `parent_name.child_name`
- Containers defined at the top level (not nested) are globally accessible
Behavior
scrollable
- Type:`true` | `false`
- Default:`false`
- Description:Makes container scrollable. Scrollable containers always use `children` (plural), never `child`.
```vi
scrollable = true
scrollable = false
```
type
- Type:keyword
- Options:`button`, `link`, `input`, `icon`, `search_bar`, `scroller`
- Description:Defines container behavior/role and adds default attributes
```vi
type = button
type = input
type = icon
type = search_bar
```
Note:When a `type` is specified and has required attributes that are not supplied, the compiler will report an error.
placeholder
- Type:string
- Description:Placeholder text for input containers
- Used with:`type = input`
```vi
type = input
placeholder = "Enter your name..."
```
icon
- Type:icon name
- Description:Icon name for icon-type containers
- Used with:`type = icon`
```vi
type = icon
icon = "check_circle"
icon = "trash"
icon = "plus"
```
id
- Type:unique identifier (string or number)
- Description:Unique identifier for accessing container data across scopes
```vi
id = unique_identifier
id = 123
id = "user_input_field"
```
Spacing
margin
- Type:number | array
- Description:Outer spacing around container
```vi
margin = 10              <# all sides #>
margin = [5, 10]         <# vertical, horizontal #>
margin = [5, 10, 5, 10]  <# top, right, bottom, left #>
```
Event Listeners
event_listners
- Type:array of event-action pairs
- Description:Defines interactive behavior for the container
```vi
event_listners = [
  on_click: function_name(),
  on_long_press: [function1(), function2()],
  on_swipe_down: action,
  on_swipe_left: action,
  on_swipe_right: action,
  on_swipe_up: action
]
```
Alternative Inline Syntax:
```vi
container:
  on_click: do_something()
  on_swipe_left: delete_item()
```
Collision Events (for games/animations):
```vi
event_listners = [
  on_collide: [
    [object1, object2]: [action1(), action2()],
    [object3, object4]: [action3()]
  ]
]
```
Available Events:
- `on_click` - Single tap/click
- `on_long_press` - Press and hold
- `on_swipe_left`, `on_swipe_right`, `on_swipe_up`, `on_swipe_down` - Swipe gestures
- `on_collide` - When objects collide (for games/animations)
The repeat_by Attribute
Purpose:Dynamically generate multiple containers without explicitly creating each one.
Type:`int, int` (for 2D grid) or `int, int, int` (for 3D grid)
```vi
container:
  repeat_by = 4, 4  <# creates 4x4 grid = 16 containers #>
container:
  repeat_by = 3, 3, 2  <# creates 3x3x2 = 18 containers in 3D #>
```
Magic Variable: repeat_by.index
When using `repeat_by`, a special variable `repeat_by.index` is available representing the current iteration index (0-based).
```vi
task_list:
  repeat_by = 1, length(items)
  item = items[repeat_by.index]  <# access current item #>
  text_content = item.name
```
Accessing Generated Children
Each generated container is named: `parent_name_XnYm` (or `_XnYmZp` for 3D), where n, m, p are the indices.
```vi
screen:
  repeat_by = 4, 4
<# Access individual cells #>
change_color():
  screen.children.X1Y1:
    color = red
  screen.children.X2Y3:
    color = blue
```
Styling with repeat_by
You can style the repeated container itself instead of iterating over children:
```vi
grid_box:
  repeat_by = 3, 3
  width = 18
  height = 18
  color = rgb(230, 230, 240)
  shape = sqircle
  align_children = center
  text_content = ""
```
Place `grid_box` in a parent container, and it will automatically create the grid.
Example:
```vi
grid:
  color = red
  shape = square
  height = 25
  width = 25
  repeat_by = 4, 4
<# Creates: grid_X0Y0, grid_X0Y1, grid_X0Y2, ..., grid_X3Y3 #>
```
Accessing Data Across Containers
Using id for Cross-Container Access
Containers can have an `id` attribute for accessing their data from other scopes:
```vi
text_input:
  type = input
  id = user_input_123
input_bar:
  children = [submit_button]
submit_button:
  type = button
  on_click: process(text_input.id(user_input_123).text_content)
```
Simplified Access (Same Scope)
When both containers are in the same parent at the same level:
```vi
submit_button:
  on_click: process(text_input.text_content)
```
Both methods work - `id()` is useful for accessing data across distant scopes.
Accessing Nested Private Containers
If a container is locally scoped (nested inside another), access it relative to its public parent:
```vi
public_parent:
  children = [private_child]
  private_child:
    text_content = "Secret"
<# Access from outside #>
other_container:
  on_click: display(public_parent.private_child.text_content)
```
Scoping Rules
Local Scope
Containers defined inside another container are locally scoped to that parent:
```vi
parent:
  children = [local_child]
  local_child:
    <# Only accessible within parent scope or via parent.local_child #>
    color = red
```
Key Points:
- Locally scoped containers cannot be directly accessed by sibling containers
- They can be accessed by other children of the same parent
- They can be accessed from outside via: `parent.local_child`
Global Scope
Top-level containers and functions are globally accessible:
```vi
global_container:
  color = blue
main_screen:
  children = [global_container]  <# can reference it here #>
```
Updating the Display
Vi automatically redraws containers when their properties change. After modifying container attributes, visual updates happen automatically.
```vi
button:
  on_click: change_background()
change_background():
  main_screen:
    color = blue  <# screen automatically redraws #>
```
Manual Delay
Use `wait_sec()` to delay actions:
```vi
show_message():
  message:
    visibility = true
  wait_sec(3)
  message:
    visibility = false
```
Memory Management
Apps built with Vi use minimal memory. Any container not currently visible is removed from memory and will only be redrawn when needed.

Project Structure Rules:
- All asset paths are relative to project root (e.g., `\assets\logo.png`)
- Import paths are relative to project root (e.g., `from lib\functions.v import *`)
Building Your App
```bash
# In terminal
vilang build "my_app_name"
```
The Vi compiler processes your code, interprets intent, and generates platform-specific optimized app code.
Error Handling
The Vi compiler reports errors when it cannot interpret your code or when structural issues occur.
Common Error Types
Scope Errors:
- Accessing non-existent containers
- Referencing private containers incorrectly
Layout Errors:
- Invalid dimension values
- Non-sequential z_index values
- Missing required dimensions
Attribute Errors:
- Missing required attributes for specified `type`
- Invalid attribute values
Path Errors:
- Incorrect asset paths (not relative to project root)
- Incorrect import paths
Structural Errors:
- Missing `main` container in `main.v`
- Circular dependencies
Philosophy:When the compiler is uncertain about your intent, it reports an error with context rather than making assumptions. Add comments to clarify intent when needed.

# Complete Examples
Example 1: Counter App
```vi
<# Data #>
current_index = 0
<# Functions #>
increment_counter():
  current_index = current_index + 1
<# Main App #>
main main_screen:
  color = white
  height = max
  width = max
  children = [header, body]
header:
  height = 12
  width = max
  color = purple[300]
  align_children = center
  children = [header_text]
header_text:
  text_content = "Simple Counter App"
  text_content_style = [font: bold, font_size: 16]
body:
  height = max
  width = max
  children = [counter, fab]
counter:
  width = 30
  height = 30
  align_self = center  <# centered in parent both horizontally and vertically #>
  align_children = center
  text_content = "{current_index}"
  color = purple[300]
  shape = sqircle
fab:
  width = 15
  height = 15
  shape = circle
  color = blue
  align_self = bottom, right  <# positioned at bottom-right corner #>
  align_children = center
  children = [icon_container]
icon_container:
  type = icon
  icon = "plus"
  color = white
  on_click: increment_counter()
```
Example 2: To-Do App
```vi
<# 
  Vi Example App: Simple To-Do
  Demonstrates containers, data, events, and repeat_by 
  File structure:
  my_to_do_app/
    lib/
      main.v
    assets/
      app_logo.png
#>
<# Data #>
items = [
  { id: 1, text: "Buy groceries", done: false },
  { id: 2, text: "Finish ViLang docs", done: true },
  { id: 3, text: "Water the plants", done: false }
]
<# Functions #>
add_task(text_input):
  items.add({ 
    id: random(number in range(0, 1000)), 
    text: text_input, 
    done: false 
  })
toggle_task(task):
  task.done = !task.done
delete_task(task):
  items.remove(task)
get_color(task):
  if (task.done):
    return green[600] 
  else:
    return gray
<# Main App #>
main main_screen:
  color = white
  height = max
  width = max
  children = [header, task_list, input_bar]
header:
  height = 12
  color = blue
  align_children = center
  children = [title_container]
title_container:
  text_content = "To-Do App"
  text_content_style = [font: bold, font_size: 16]
<# Task List #>
task_list:
  scrollable = true
  children = [task_items(items)]
task_items(items):
  i = repeat_by.index
  task = items[i]
  height = 8
  width = 95
  repeat_by = 1, length(items)
  margin = [2, 2]
  color = get_color(task)
  children = [checkbox(task), task_text(task), delete_icon(task)]
  event_listners = [
    on_swipe_left: delete_task(task)
  ]
<# Task Components #>
checkbox(task):
  type = icon
  icon = "check_circle" if (task.done) else "circle_outline"
  on_click: toggle_task(task)
task_text(task):
  text_content = task.text
  text_content_font = "16"
  align_children = left
delete_icon(task):
  type = icon
  icon = "trash"
  color = red
  on_click: delete_task(task)
<# Input Bar #>
input_bar:
  height = 10
  width = max
  color = gray[100]
  shape = sqircle
  children = [task_input, add_button]
task_input:
  type = input
  placeholder = "Add new task..."
  width = 70
  height = 8
  id = new_task_input
add_button:
  type = button
  width = 25
  height = 8
  color = blue
  text_content = "Add"
  on_click: add_task(task_input.id(new_task_input).text_content)
```
Example 3: TicTacToe Game
```vi
<# TicTacToe - Vi Language Game #>
<# Data #>
current_player = "X"
game_over = false
winner = ""
<# Main App #>
main main_screen:
  color = rgb(240, 240, 250)
  height = max
  width = max
  children = [header, game_container, footer]
header:
  height = 15
  width = max
  color = rgb(100, 100, 200)
  align_children = center
  children = [title]
title:
  text_content = "TicTacToe"
  text_content_style = [font: bold, font_size: 32, color: white]
game_container:
  height = max
  width = max
  align_children = center
  children = [game_board, status_panel]
game_board:
  width = 60
  height = 60
  align_self = center
  color = white
  shape = sqircle
  children_padding = 4
  children = [grid]
grid:
  width = max
  height = max
  repeat_by = 3, 3
  children_padding = 2
  width = 18
  height = 18
  color = rgb(230, 230, 240)
  shape = sqircle
  align_children = center
  text_content = ""
  text_content_style = [font: bold, font_size: 48]
  on_click: make_move(grid)
<# Functions #>
make_move(cell):
  if (not game_over and cell.text_content == ""):
    cell:
      text_content = current_player
      text_content_style = [
        font: bold, 
        font_size: 48, 
        color: rgb(100, 150, 250) if (current_player == "X") else rgb(250, 100, 100)
      ]
    check_winner()
    if (not game_over):
      current_player = "O" if (current_player == "X") else "X"
check_winner():
  <# Store all cell values #>
  A = grid.X0Y0.text_content
  B = grid.X1Y0.text_content
  C = grid.X2Y0.text_content
  D = grid.X0Y1.text_content
  E = grid.X1Y1.text_content
  F = grid.X2Y1.text_content
  G = grid.X0Y2.text_content
  H = grid.X1Y2.text_content
  I = grid.X2Y2.text_content
  <# Check rows #>
  if (A == B and B == C and A != ""):
    winner = A
    game_over = true
  if (D == E and E == F and D != ""):
    winner = D
    game_over = true
  if (G == H and H == I and G != ""):
    winner = G
    game_over = true
  <# Check columns #>
  if (A == D and D == G and A != ""):
    winner = A
    game_over = true
  if (B == E and E == H and B != ""):
    winner = B
    game_over = true
  if (C == F and F == I and C != ""):
    winner = C
    game_over = true
  <# Check diagonals #>
  if (A == E and E == I and A != ""):
    winner = A
    game_over = true
  if (C == E and E == G and C != ""):
    winner = C
    game_over = true
  <# Check for draw #>
  all_filled = true
  for cell in grid.children:
    if (cell.text_content == ""):
      all_filled = false
  if (all_filled and not game_over):
    game_over = true
    winner = "Draw"
reset_game():
  for cell in grid.children:
    cell:
      text_content = ""
  current_player = "X"
  game_over = false
  winner = ""
status_panel:
  width = 60
  height = 20
  align_self = center
  align_children = center
  children = [status_text, reset_button]
status_text:
  text_content = (
    ("It's a Draw!" if (winner == "Draw") else "Winner: {winner}!") if (game_over) else "Current Player: {current_player}"
  )
  text_content_style = [font: bold, font_size: 24, color: rgb(80, 80, 80)]
reset_button:
  type = button
  width = 30
  height = 8
  color = rgb(100, 200, 100)
  shape = sqircle
  text_content = "New Game"
  text_content_style = [font: bold, font_size: 18, color: white]
  on_click: reset_game()
footer:
  height = 10
  width = max
  color = rgb(220, 220, 230)
  align_children = center
  children = [footer_text]
footer_text:
  text_content = "Made with Vi Language"
  text_content_style = [font_size: 14, color: rgb(100, 100, 100)]
```
Philosophy: Everything is Possible
Vi is intentionally flexible. The same syntax can mean different things based on context:
- Containers can be functions:`user_card(data)`
- Functions can return values or modify state:Context determines behavior
- Data types are inferred:Numbers, strings, booleans, arrays, objects
- Scope is flexible:Variables bubble up until they're found
The Vi compiler intelligently interprets your intent. When in doubt, add comments to clarify:
```vi
<# This container takes a user object and displays their info #>
user_profile(user):
  text_content = user.name
  color = if (user.active) green else gray
```
Best Practices
1. Use descriptive names:`task_list` not `tl`
2. Comment complex logic:Help the compiler understand your intent
3. Keep functions small:One responsibility per function
4. Group related containers:Organize by feature
5. Use parameterized containers:For reusable components
6. Leverage repeat_by:Instead of manually creating repeated elements
7. Explicit is better than implicit:When uncertain, be verbose
8. Consistent paths:Always use paths relative to project root
9. Sequential z_index:Keep z_index values sequential to avoid errors
Language Keywords Summary
Container Keywords
- `main` - Define main entry container
- `children` - Array of child containers
- `repeat_by` - Generate multiple containers
- `repeat_by.index` - Current iteration index
Control Flow
- `if`, `else`, `else if` - Conditionals
- `for`, `in` - Loops
- `return` - Return value from function
Built-in Functions
- `visit(url)` - Navigation
- `play(url)` - Play media
- `wait_sec(n)` - Delay execution
- `random(number in range(min, max))` - Generate random number
- `length(array)` - Get array length
Array Methods
- `array.add(item)` - Add item to array
- `array.remove(item)` - Remove item from array
- `array.index(item)` - Get index of item
- `array[n]` - Access item by index
Event Keywords
- `on_click` - Single tap/click
- `on_long_press` - Press and hold
- `on_swipe_left`, `on_swipe_right`, `on_swipe_up`, `on_swipe_down` - Swipe gestures
- `on_collide` - Collision detection
Special Values
- `max` - Fill parent dimension
- `auto` - Automatic dimension based on content
- `true`, `false` - Boolean values
- `center`, `centre` - Center alignment
Import Keywords
- `from` - Import from file
- `import` - Import entire file
- `all`, `*` - Import everything
Quick Reference
Basic Container
```vi
container_name:
  width = 100
  height = 50
  color = blue
  children = [child1, child2]
```
Parameterized Container
```vi
card(data):
  text_content = data.title
  color = data.color
  height = 50
```
Function
```vi
process_data(input):
  result = input * 2
  return result
```
Conditional
```vi
if (condition):
  action
else:
  other_action
```
Loop
```vi
for item in array:
  display(item)
```
Event Handler
```vi
button:
  on_click: handle_click()
```
Repeat By
```vi
grid:
  repeat_by = 4, 4
  width = 25
  height = 25
```
Vi - Everything is possible.