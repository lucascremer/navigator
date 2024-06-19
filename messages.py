from navigator.utils import Colors

def error(message='', exc='', fatal=False):
    if len(message) != 0:
        message += ' '
    print(f'{Colors.RED}ERROR: {message}{Colors.ORANGE}{exc}{Colors.RESET}')
    if fatal:
        exit(1)
    else:
        return
    

def warning(message='', exc=''):
    if len(message) != 0:
        message += ' '
    print(f'{Colors.YELLOW}WARNING: {message}{Colors.ORANGE}{exc}{Colors.RESET}')


def info(message='', exc=''):
    if len(message) != 0:
        message += ' '
    print(f'{Colors.BLUE}INFO: {message}{Colors.ORANGE}{exc}{Colors.RESET}')