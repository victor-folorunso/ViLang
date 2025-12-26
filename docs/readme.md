# Vi Language

**Build cross-platform apps with simple, intuitive syntax.**

Vi is a declarative language that compiles to Flutter, letting you create mobile, web, and desktop apps by simply describing what you want.

---

## Quick Example
```vi
<# A simple counter app #>
current_count = 0

increment():
  current_count = current_count + 1

main app:
  height = max
  width = max
  children = [counter_display, button]

counter_display:
  text_content = "Count: {current_count}"
  align_self = center

button:
  text_content = "Increment"
  on_click: increment()
  align_self = bottom, center
```

**Result:** A working cross-platform counter app.

---

## 🚀 Features

- **Simple Syntax** - Describe your UI, Vi handles the rest
- **Cross-Platform** - Android, iOS, Web, and Desktop from one codebase
- **Declarative** - Containers, attributes, and events
- **Type Inference** - No type declarations needed
- **Zero Setup** - Vi includes everything you need

---

## 📦 Installation

1. **Download** `vi.exe` from [Releases](https://github.com/victor-folorunso/ViLang/releases)
2. **Add to PATH** - Add the Vi directory to your system PATH
3. **Done** - Vi includes its own Flutter SDK internally

**Prerequisites:**
- Android Studio (for Android emulator) OR
- Xcode (for iOS simulator, macOS only)

---

## 🏃 Quick Start
```bash
# Create new project
create main.vi in any folder

# Navigate to project
cd folder

# Run on emulator
vi run
```

Vi will show available emulators - just pick one and it handles everything else.

---

## 🎯 How It Works

Vi compiles your code to a widget tree (JSON), then uses a Flutter runtime to render your app dynamically. You write simple Vi code, and Vi manages the Flutter complexity behind the scenes.

**Benefits:**
- Focus on describing UI, not managing boilerplate
- Simplified syntax
- Automatic device selection and emulator management
- Apps are generated on-the-fly from your Vi code

---

## 📖 Learn More

- **[Language Documentation](ViLang/wiki)** - Complete syntax guide and examples

---

## Current Status

Vi is in **early development**. Core features are working:

- Vi → Flutter compilation
- Android emulator integration
- 🚧 iOS deployment (in progress)
- 🚧 Web deployment (in progress)

---

## Contributing

Vi is open source! Contributions, bug reports, and feedback are welcome.

---

## 💬 Community

- **GitHub Discussions** - Ask questions, share your Vi projects
- **Issues** - Report bugs or request features

---
