def main():
    print('\nHow do you want to use the assistant?')
    print('  1) CLI based')
    print('  2) Web based')
    choice = input('\nEnter 1 or 2: ').strip()

    if choice == '1':
        from cli import run_cli
        run_cli()
    elif choice == '2':
        from web_app import run_web
        run_web()
    else:
        print('Invalid choice. Please enter 1 or 2.')


if __name__ == '__main__':
    main()
