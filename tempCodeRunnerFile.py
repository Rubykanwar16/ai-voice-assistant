def main():
    print('\nHow do you want to use the assistant?')
    print('  1) CLI based')
    print('  2) Web based')
    choice = input('\nEnter 1 or 2: ').strip()

    if choice == '1':
        try:
            from cli import run_cli
            run_cli()
        except ValueError as e:
            print(f"\nError: {e}\n")
            exit(1)
        except ImportError as e:
            print(f"\nError importing CLI: {e}")
            print("Make sure all dependencies are installed: pip install -r requirements.txt\n")
            exit(1)
    elif choice == '2':
        try:
            from web_app import run_web
            run_web()
        except ValueError as e:
            print(f"\nError: {e}\n")
            exit(1)
        except ImportError as e:
            print(f"\nError importing web app: {e}")
            print("Make sure all dependencies are installed: pip install -r requirements.txt\n")
            exit(1)
    else:
        print('Invalid choice. Please enter 1 or 2.')


if __name__ == '__main__':
    main()
