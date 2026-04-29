def main():
    print('\n' + '='*60)
    print('  AI VOICE ASSISTANT - SELECT MODE')
    print('='*60)
    print('\nHow do you want to use the assistant?')
    print('  1) CLI based (command-line)')
    print('  2) Web based (browser UI)')
    print('\nNote: Make sure you have:')
    print('  ✓ Created a .env file with GROQ_API_KEY')
    print('  ✓ Run: pip install -r requirements.txt\n')
    choice = input('Enter 1 or 2: ').strip()

    if choice == '1':
        try:
            from cli import run_cli
            run_cli()
        except ModuleNotFoundError as e:
            print(f"\n❌ ERROR: Missing module: {e}")
            print("   Run: pip install -r requirements.txt\n")
            exit(1)
        except ValueError as e:
            print(f"\n❌ ERROR: {e}\n")
            exit(1)
        except ImportError as e:
            print(f"\n❌ ERROR importing CLI: {e}")
            print("   Make sure all dependencies are installed: pip install -r requirements.txt\n")
            exit(1)
        except Exception as e:
            print(f"\n❌ ERROR: {e}\n")
            exit(1)
    elif choice == '2':
        try:
            from web_app import run_web
            run_web()
        except ModuleNotFoundError as e:
            print(f"\n❌ ERROR: Missing module: {e}")
            print("   Run: pip install -r requirements.txt\n")
            exit(1)
        except ValueError as e:
            print(f"\n❌ ERROR: {e}\n")
            exit(1)
        except ImportError as e:
            print(f"\n❌ ERROR importing web app: {e}")
            print("   Make sure all dependencies are installed: pip install -r requirements.txt\n")
            exit(1)
        except Exception as e:
            print(f"\n❌ ERROR: {e}\n")
            exit(1)
    else:
        print('\n❌ Invalid choice. Please enter 1 or 2.\n')
        main()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\nShutting down...')
        exit(0)
    except Exception as e:
        print(f'\n❌ Unexpected error: {e}\n')
        exit(1)
