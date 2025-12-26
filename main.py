import sys
from cli_router import Vi

def main():
    if len(sys.argv) < 2:
        print("== Vi CLI 4.0 ==")
        print("Usage:")
        print("  vi run [target]                - Run main.vi on target")
        print("  vi create [platform]           - Create app for android/ios")
        return

    command = sys.argv[1].lower()
    target = sys.argv[2] if len(sys.argv) > 2 else None

    vi = Vi()

    if command == "run":
        vi.run()
    elif command == "create":
        vi.create(target)
    else:
        print(f"Unknown command: {command}")
    
if __name__ == "__main__":
    main()
