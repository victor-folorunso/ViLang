# Vi Language Documentation

## Overview

Vi is a declarative UI language that compiles to Flutter/Dart. Write responsive, cross-platform apps with a Python-inspired syntax. Vi handles state management, hot restart, and responsive layouts automatically.

**Philosophy**: Clear, explicit syntax. What you write is what you get.

**Workflow**: `app.vi` → Vi Compiler → Flutter/Dart → Android/iOS/Web

---

## Commands

```bash
vi run main.vi          # Development mode with hot restart
vi create android       # Production build for Android
vi create ios           # Production build for iOS  
vi create web           # Production build for Web
```

---

## Comments

Multi-line comments use `<#` and `#>`:
```vi
<# This is a comment #>

<#
  Multi-line comment
  Spans multiple lines
#>

score = 0  <# Inline comment #>
```

---

## Core Concepts

### 1. Containers

Everything in Vi is a container. Containers are UI elements defined by attributes.

```vi
container_name:
  attribute1 = value1
  attribute2 = value2
```

**Example**:
```vi
header:
  width = 100
  height = 15
  color = blue
```

### 2. The Main Container

Every app needs one main container - the entry point:

```vi
main app_name:
  width = 100
  height = max
  children = [header, body]
```

Rules:
- Use `main` keyword before container name
- Must be in your `.vi` file
- All other containers render inside or are referenced by main

### 3. Children

Containers can contain other containers:

```vi
parent:
  children = [child1, child2]

child1:
  color = red

child2:
  color = blue
```

**Inline Definition** (children defined inside the array):
```vi
parent:
  children = [
    inline_child:
      color = green
      height = 10,
    another_child:
      color = yellow
  ]
```

### 4. Comma-Separated Containers

Apply the same style to multiple containers:
```vi
box1, box2, box3:
  width = 30
  height = 30
  color = gray
  shape = sqircle
```

This creates three independent containers with identical attributes. Scope is determined by indentation level, not by comma separation.

---

## Data Types

### Variables

Variables are assigned directly - no type declarations needed:
```vi
score = 0
player_name = "Alice"
game_over = false
items = [1, 2, 3]
```

### Numbers
```vi
x = 42
pi = 3.14
negative = -10
```

### Strings
```vi
name = "Bob"
message = "Hello"
```

**String Interpolation**:
```vi
greeting = "Hello, {name}!"  <# Outputs: Hello, Bob! #>
```

**Literal Braces** (when you want actual `{}`):
```vi
code = "Use {{var}} for interpolation"  <# Outputs: Use {var} for interpolation #>
```

### Booleans
```vi
active = true
disabled = false
```

### Arrays (Lists)

**Explicit brackets**:
```vi
numbers = [1, 2, 3, 4, 5]
names = ["alice", "bob", "charlie"]
mixed = [1, "two", true]
```

**Implicit brackets** (single-line only):
```vi
colors = red, blue, green  <# Same as [red, blue, green] #>
scores = 10, 20, 30        <# Same as [10, 20, 30] #>
```

Note: For multi-line arrays, you must use explicit `[]`.

**Accessing Elements**:
```vi
first = numbers[0]
second = numbers[1]
```

**Array Methods**:
```vi
items.add(new_item)          <# Add to end #>
items.remove(target_item)    <# Remove specific item #>
index = items.index(item)    <# Get index of item #>
count = length(items)        <# Get array length #>
```

### Objects (Dictionaries)
```vi
user = {
  name: "Alice",
  age: 25,
  active: true
}

<# Access properties #>
user_name = user.name
user.age = 26
```

### Array of Objects
```vi
tasks = [
  { id: 1, text: "Buy milk", done: false },
  { id: 2, text: "Write code", done: true }
]
```

---

## Functions

### Defining Functions
```vi
function_name():
  <# function body #>
  code_here

function_with_params(param1, param2):
  result = param1 + param2
  return result
```

### Calling Functions
```vi
do_something()
answer = calculate(10, 20)
```

### Nested Functions
Functions can be defined inside other functions:
```vi
outer():
  inner(x):
    return x * 2
  
  result = inner(5)
  return result
```

Nested functions have access to their parent function's variables (closure).

### Built-in Functions

**Navigation**:
```vi
go_to(screen_name)    <# Navigate to another screen #>
go_back()             <# Go back to previous screen #>
```

**Utilities**:
```vi
wait_sec(3)                      <# Pause execution for 3 seconds #>
random_num = random(1, 100)      <# Random number between 1-100 #>
count = length(my_array)         <# Get array length #>
```

**External** (placeholder implementations):
```vi
visit("https://example.com")     <# Open URL #>
play("assets/audio.mp3")         <# Play audio #>
```

---

## Control Flow

### If Statements
```vi
if (condition):
  action

if (score > 100):
  show_message()
```

### If-Else
```vi
if (user.age >= 18):
  show_content()
else:
  show_warning()
```

### If-Else If-Else
```vi
if (score > 90):
  grade = "A"
else if (score > 80):
  grade = "B"
else:
  grade = "C"
```

### Ternary Operator
```vi
status = "online" if (user.active) else "offline"
color = green if (task.done) else gray
```

### For Loops
```vi
for item in array:
  process(item)

for user in users:
  display(user.name)
```

### While Loops
```vi
while (count < 10):
  count = count + 1
```

---

## Container Attributes

Attributes define how containers look and behave.

### Layout & Sizing

**width**
- Type: `number` | `max`
- Units: Percentage of screen width (0-100)
- `max` = fill parent width
```vi
width = 50    <# 50% of screen width #>
width = max   <# Fill parent width #>
```

**height**
- Type: `number` | `max` | `auto`
- Units: Percentage of screen width (maintains aspect with width)
- `auto` = fit content
- `max` = fill available space in parent
```vi
height = 30    <# 30% of screen width #>
height = max   <# Fill parent height #>
height = auto  <# Fit content #>
```

**shape**
- Type: `square` | `circle` | `sqircle`
- Default: `square`
```vi
shape = circle
shape = sqircle  <# Rounded square #>
```

### Appearance

**color**
- Named colors: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `white`, `black`, `gray`
- Material shades: `blue[600]`, `red[300]`
- RGB: `rgb(255, 100, 50)`
```vi
color = blue
color = blue[600]
color = rgb(255, 0, 0)
```

**background_image**
- Path relative to project root
```vi
background_image = "assets/hero.png"
```

**visibility**
- Type: `true` | `false`
- Default: `true`
```vi
visibility = false  <# Hide container #>
```

### Content

**text_content**
- String with interpolation support
```vi
text_content = "Hello World"
text_content = "Score: {score}"
```

**Text Styling** (separate attributes):
```vi
text_font = bold         <# or italic #>
text_font_size = 20
text_color = blue        <# Any color expression #>
```

**Legacy text_content_style** (still supported):
```vi
text_content_style = [font: bold, font_size: 20, color: blue]
```

**audio_content** / **video_content**
- Paths to media files
```vi
audio_content = "assets/music.mp3"
video_content = "assets/intro.mp4"
```
Note: These generate placeholders - full implementation requires Flutter packages.

### Alignment

**align_self**
- How container positions itself within parent
- Values: `center`, `top`, `bottom`, `left`, `right`
- Multi-axis: `bottom, right`, `top, left` (implicit array), etc.
```vi
align_self = center
align_self = bottom, right  <# Bottom-right corner #>
```

**align_children**
- How children are aligned within this container
- Values: `center`, `left`, `right`, `top`, `bottom`
```vi
align_children = center
```

### Spacing

**margin**
- Outer spacing around container
```vi
margin = 10                  <# All sides #>
margin = 5, 10               <# Vertical, horizontal (implicit array) #>
margin = 5, 10, 5, 10        <# Top, right, bottom, left #>
```

**children_padding**
- Spacing between children
```vi
children_padding = 10
```

### Behavior

**scrollable**
- Makes container scrollable
```vi
scrollable = true
```

**type**
- Defines special widget type
- Values: `button`, `input`, `icon`, `search_bar`, `link`
```vi
type = button
type = input
type = icon
type = search_bar
type = link
```

**placeholder**
- For `input` and `search_bar` types
```vi
type = input
placeholder = "Enter your name..."
```

**icon**
- For `icon` type
- Names: `plus`, `add`, `trash`, `delete`, `check_circle`, `circle_outline`, `close`, `settings`, `home`, `back`, `forward`, `search`, `menu`, `star`, `heart`, `share`, `edit`, `camera`, `image`, `info`, `warning`, `error`, `check`, `refresh`, `send`, `lock`, `person`, `notification`
```vi
type = icon
icon = "plus"
color = white
```

### Events

**on_click**
- Triggers on tap/click
```vi
on_click: do_something()
```

**on_long_press**
- Triggers on press and hold
```vi
on_long_press: show_menu()
```

**Swipe Events**:
```vi
on_swipe_left: delete_item()
on_swipe_right: archive_item()
on_swipe_up: scroll_up()
on_swipe_down: refresh()
```

---

## Dynamic Layouts

### repeat_by

Generate multiple containers in a grid:
```vi
grid:
  repeat_by = 3, 3  <# 3 rows x 3 columns = 9 containers #>
  width = 18
  height = 18
  color = gray
```

**Access**: Containers named `grid_X0Y0`, `grid_X0Y1`, ... `grid_X2Y2`

**repeat_by.index**: Magic variable for current iteration index (0-based)
```vi
task_list:
  repeat_by = 1, length(items)
  item = items[repeat_by.index]
  text_content = item.name
```

**Modifying Repeated Containers**:
```vi
change_color():
  grid_X1Y1:
    color = red
```

Or in loops:
```vi
for cell in grid.children:
  cell:
    color = blue
```

---

## Modifying Containers

Inside functions, you can modify existing containers:
```vi
button:
  color = blue
  on_click: change_color()

change_color():
  button:
    color = red  <# Modifies the button #>
```

This automatically triggers UI updates via setState.

---

## Multi-Screen Apps

Define additional screens as regular containers:
```vi
main home:
  children = [goto_button]

goto_button:
  type = button
  text_content = "Go to Settings"
  on_click: go_to(settings)

settings:
  children = [back_btn]

back_btn:
  type = button
  text_content = "Back"
  on_click: go_back()
```

Vi automatically handles navigation state and Android back button.

---

## Configuration

The `config:` block sets app-level settings:
```vi
config:
  title = "My App"
  icon = "assets/icon.png"
  splash:
    color = purple
    logo = "assets/logo.png"
    duration = 3
  screens:
    mobile = 0 to 600
    tablet = 600 to 1024
    desktop = 1024 to max
```

**Runtime Config**:
```vi
app_title = config.title  <# Access config values #>
```

**Breakpoints** (using `to` syntax):
Automatically generates boolean getters:
```vi
cols = 1 if mobile else 2 if tablet else 3
```

Breakpoints are defined with the `to` keyword:
```vi
mobile = 0 to 600      <# 0 <= width < 600 #>
tablet = 600 to 1024   <# 600 <= width < 1024 #>
desktop = 1024 to max  <# width >= 1024 #>
```

---

## Importing

**Import specific items**:
```vi
from "utils.vi" import helper_function
from "components.vi" import card, button
```

**Import everything**:
```vi
from "helpers.vi" import *
```

**Import file**:
```vi
import "shared.vi"
```

**Import from URL**:
```vi
from "https://example.com/components.vi" import header
import "https://raw.githubusercontent.com/user/repo/main/shared.vi"
```

Paths are relative to project root. URL imports download and cache the file.

---

## Development

### vi run
- Fast development mode
- Hot restart on save (regenerates entire app)
- In-app splash screen
- Uses emulator or connected device
```bash
vi run main.vi
```

### vi create
- Production builds
- Native splash screens (OS-level, before Flutter starts)
- App icon generation
- Optimized output
```bash
vi create android
vi create ios
vi create web
```

---

## Complete Examples

### Counter App
```vi
<# Data #>
count = 0

<# Functions #>
increment():
  count = count + 1

<# Main App #>
main app:
  width = 100
  height = max
  color = white
  children = [counter_display, button]

counter_display:
  text_content = "Count: {count}"
  text_font_size = 32
  text_color = blue

button:
  type = button
  text_content = "Increment"
  width = 40
  color = green
  on_click: increment()
```

### To-Do List
```vi
<# Data #>
tasks = [
  { id: 1, text: "Buy groceries", done: false },
  { id: 2, text: "Write code", done: true }
]

<# Functions #>
toggle(task):
  task.done = !task.done

add_task(text):
  tasks.add({
    id: random(1, 1000),
    text: text,
    done: false
  })

<# Main App #>
main app:
  width = 100
  height = max
  children = [task_list, input_bar]

task_list:
  scrollable = true
  children = [task_row(tasks)]

task_row(tasks):
  repeat_by = 1, length(tasks)
  task = tasks[repeat_by.index]
  width = 95
  height = 8
  color = green[600] if (task.done) else gray
  children = [task_text(task)]
  on_click: toggle(task)

task_text(task):
  text_content = task.text

input_bar:
  height = 10
  children = [task_input, add_btn]

task_input:
  type = input
  placeholder = "New task..."

add_btn:
  type = button
  text_content = "Add"
  on_click: add_task(task_input.text_content)
```

### TicTacToe Game
```vi
<# Data #>
current_player = "X"
game_over = false
winner = ""

<# Main App #>
main screen:
  width = 100
  height = max
  color = white
  children = [title, game_board, reset_btn]

title:
  text_content = "TicTacToe"
  text_font_size = 32
  text_color = blue

game_board:
  width = 60
  height = 60
  children = [grid]

grid:
  repeat_by = 3, 3
  width = 18
  height = 18
  color = gray[200]
  shape = sqircle
  text_content = ""
  text_font_size = 48
  on_click: make_move(grid)

reset_btn:
  type = button
  text_content = "New Game"
  width = 30
  color = green
  on_click: reset_game()

<# Functions #>
make_move(cell):
  if (not game_over and cell.text_content == ""):
    cell:
      text_content = current_player
      text_color = blue if (current_player == "X") else red
    check_winner()
    if (not game_over):
      current_player = "O" if (current_player == "X") else "X"

check_winner():
  <# Check rows, columns, diagonals #>
  A = grid.X0Y0.text_content
  B = grid.X1Y0.text_content
  C = grid.X2Y0.text_content
  
  if (A == B and B == C and A != ""):
    winner = A
    game_over = true

reset_game():
  for cell in grid.children:
    cell:
      text_content = ""
  current_player = "X"
  game_over = false
  winner = ""
```

---

## Best Practices

1. **Naming**: Use `snake_case` for everything
2. **Comments**: Explain complex logic
3. **One responsibility**: Functions should do one thing
4. **Group related**: Organize containers by feature
5. **Asset paths**: Always relative to project root
6. **Test early**: Use `vi run` frequently
7. **Implicit arrays**: Use for simple lists, explicit `[]` for clarity

---

## Troubleshooting

**Import failed**: Check file path and syntax in imported file

**Container not found**: Check spelling and that container is defined

**Function not found**: Ensure function is defined before use

**Hot restart not working**: Save the `.vi` file, check terminal for errors

**Layout issues**: Check parent-child relationships and width/height values

**URL import failed**: Check network connection and URL accessibility

---

## Coming Soon

- **Animations**: `animate = [property: opacity, duration: 0.3]`
- **Database Support**: Syntax in design
- **Advanced Media**: Full audio/video player widgets
- **Parameterized Containers**: Full implementation

---

## Quick Reference

### Data Types
- Numbers: `42`, `3.14`
- Strings: `"text"`, interpolation: `"Hello {name}"`
- Booleans: `true`, `false`
- Arrays: `[1, 2, 3]` or `1, 2, 3` (single-line)
- Objects: `{key: value}`
- Ranges: `0 to 600` → `[0, 600]`

### Control Flow
- If: `if (cond): action`
- Ternary: `val if (cond) else other`
- For: `for item in array: action`
- While: `while (cond): action`

### Common Attributes
- Size: `width`, `height` (0-100 or `max`)
- Color: `color = blue` or `rgb(r, g, b)`
- Text: `text_content`, `text_font`, `text_font_size`, `text_color`
- Layout: `align_self`, `align_children`, `margin`
- Events: `on_click`, `on_long_press`, `on_swipe_*`

### Built-in Functions
- `go_to(screen)`, `go_back()`
- `wait_sec(n)`
- `random(min, max)`
- `length(array)`
- `visit(url)`, `play(audio)`

### Special Features
- Nested functions: Define functions inside functions
- `repeat_by.index`: Access current iteration in repeated containers
- Implicit arrays: `a = 1, 2, 3` same as `a = [1, 2, 3]`
- `to` syntax: `0 to 600` same as `[0, 600]`
- URL imports: Import from `https://` URLs
