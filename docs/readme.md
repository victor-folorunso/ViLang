# Vi Language

A declarative UI language that compiles to Flutter/Dart. Build cross-platform apps with Python-inspired syntax.

## Features

- **Declarative UI**: Define what you want, not how to build it
- **Hot Restart**: See changes instantly on save
- **Responsive by Default**: Breakpoints and adaptive layouts built-in
- **State Management**: Automatic UI updates when data changes
- **Cross-Platform**: Compile to Android, iOS, and Web from one codebase

## Quick Start

```vi
<# Counter App in 20 lines #>
count = 0

increment():
  count = count + 1

main app:
  width = 100
  height = max
  children = [counter, button]

counter:
  text_content = "Count: {count}"
  text_font_size = 32

button:
  type = button
  text_content = "+"
  on_click: increment()
```

Run it:
```bash
vi run main.vi
```

## Installation

Vi requires Flutter to be installed on your system.

1. Install Flutter: https://flutter.dev/docs/get-started/install
2. Clone this repo
3. Add Vi to your PATH (or run from source)

## Commands

```bash
vi run <file>           # Development mode with hot restart
vi create android       # Build APK
vi create ios           # Build iOS app  
vi create web           # Build web app
```

## Syntax Highlights

### Implicit Arrays
```vi
colors = red, blue, green  # Single-line arrays don't need []
```

### Range Syntax
```vi
config:
  screens:
    mobile = 0 to 600     # More intuitive than [0, 600]
    tablet = 600 to 1024
```

### Nested Functions
```vi
outer():
  inner(x):
    return x * 2
  result = inner(5)
```

### URL Imports
```vi
from "https://example.com/components.vi" import header
```

### Events
```vi
card:
  on_click: view_details()
  on_long_press: show_menu()
  on_swipe_left: delete()
```

### Dynamic Grids
```vi
grid:
  repeat_by = 3, 3
  width = 20
  height = 20
  color = gray
  on_click: toggle(grid)

toggle(cell):
  cell:
    color = blue if (cell.color == gray) else gray
```

## Documentation

See **[wiki.md](wiki.md)** for complete documentation including:
- All container attributes
- Control flow
- Functions and variables
- Multi-screen navigation
- Configuration and breakpoints
- Complete examples

## Examples

Check the `examples/` directory for:
- Counter app
- To-do list
- TicTacToe game
- Multi-screen navigation
- Form validation

## Architecture

```
.vi file → Parser → AST → Code Generator → Flutter/Dart → App
```

Vi compiles to clean, readable Dart code that uses Flutter widgets directly.

## Project Status

**Current**: v0.9 - Core language complete, production-ready for simple apps

**Coming Soon**:
- Database integration (local + Supabase)
- Animation system
- Advanced media widgets

## Contributing

Vi is actively developed. Feature requests and bug reports welcome!

## Philosophy

Vi believes in:
- **Explicit over implicit**: What you write is what you get
- **Simplicity**: Common tasks should be simple
- **No magic**: Clear compilation model, readable output
- **Progressive disclosure**: Start simple, add complexity as needed

## License

MIT License - See LICENSE file
