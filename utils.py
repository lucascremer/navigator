import re
from pathlib import Path


class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ORANGE = '\033[38;5;214m'
    VIOLET = '\033[38;5;57m'
    GREY = '\033[38;5;240m'


def green(string):
    return f'{Colors.GREEN}{string}{Colors.RESET}'
def red(string):
    return f'{Colors.RED}{string}{Colors.RESET}'
def yellow(string):
    return f'{Colors.YELLOW}{string}{Colors.RESET}'
def blue(string):
    return f'{Colors.BLUE}{string}{Colors.RESET}'
def magenta(string):
    return f'{Colors.MAGENTA}{string}{Colors.RESET}'
def cyan(string):
    return f'{Colors.CYAN}{string}{Colors.RESET}'
def white(string):
    return f'{Colors.WHITE}{string}{Colors.RESET}'
def orange(string):
    return f'{Colors.ORANGE}{string}{Colors.RESET}'
def violet(string):
    return f'{Colors.VIOLET}{string}{Colors.RESET}'
def grey(string):
    return f'{Colors.GREY}{string}{Colors.RESET}'


def get_fresh_env():
    # load in the environment variables from ~/.fresh_env
    with open(AutoPath('~/.fresh_env'), 'r') as f:
        env = f.read()
        lines = env.split('\n')

    fresh_env = {}

    for i, line in enumerate(lines):
        parts = line.split('=', 1)
        if line.startswith('BASH_FUNC_which'):
            key, value = parts
            value += '\n' + lines[i+1] + '\n' + lines[i+2]
        elif len(parts) == 2:
            key, value = parts 

        fresh_env[key] = value

    return fresh_env


def fill_string(string, length, fill_char=' ', alignment='left'):
    n_fill = length - len(remove_ansi_codes(string))
    if alignment == 'left':
        return f'{string}{fill_char*n_fill}'
    elif alignment == 'right':
        return f'{fill_char*n_fill}{string}'
    elif alignment == 'center':
        if n_fill % 2 == 0:
            left_fill = right_fill = n_fill // 2
        else:
            left_fill = n_fill // 2
            right_fill = n_fill // 2 + 1
        return f'{fill_char*left_fill}{string}{fill_char*right_fill}'


def remove_ansi_codes(string):
    string = str(string)
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', string)


def print_dict(d, indent=0):
    for key, value in d.items():
        print(' ' * indent + str(key) + ':', end=' ')
        if isinstance(value, dict):
            print()
            print_dict(value, indent + 4)
        else:
            print(str(value))


def replace_placeholder(string, replacements: dict) -> str:
    for placeholder, replacement in replacements.items():
        string = string.replace(placeholder, str(replacement))
    return string


class AutoPath:
    def __init__(self, path):
        self.path = Path(path).expanduser()

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return f"AutoPath({str(self.path)!r})"

    def __fspath__(self):
        return str(self.path)

    def __add__(self, other):
        return AutoPath(self.path / other)
    
    def __radd__(self, other):
        return AutoPath(Path(other) / self.path)
    
    def __truediv__(self, other):
        return AutoPath(self.path / other)
    
    def __rtruediv__(self, other):
        return AutoPath(Path(other) / self.path)

    def __eq__(self, other):
        if isinstance(other, AutoPath):
            return self.path == other.path
        return self.path == other

    def __ne__(self, other):
        return not self.__eq__(other)