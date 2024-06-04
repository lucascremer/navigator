from lib.colors import Colors

def error(exc, message='', fatal=False):
    print(f'{Colors.RED}Error: {message} {Colors.ORANGE}{exc}{Colors.RESET}')
    if fatal:
        exit(1)
    else:
        return