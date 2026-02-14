import sys
from cli_router import Vi

def main():
    if len(sys.argv) < 2:
        print("== Vi CLI 5.0 ==")
        print("Usage:")
        print("  vi run                         - Run main.vi on emulator")
        print("  vi run --hot-reload            - Run with hot reload enabled")
        print("  vi create [platform]           - Create app for android/ios/web")
        return

    command = sys.argv[1].lower()
    
    vi = Vi()

    if command == "run":
        # Check for --hot-reload flag
        hot_reload = "--hot-reload" in sys.argv
        vi.run(hot_reload=hot_reload)
    elif command == "create":
        target = sys.argv[2] if len(sys.argv) > 2 else "android"
        vi.create(target)
    else:
        print(f"Unknown command: {command}")
    
if __name__ == "__main__":
    main()
