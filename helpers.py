import os


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


def get_fresh_env():
    # load in the environment variables from ~/.fresh_env
    with open(os.path.expanduser('~/.fresh_env'), 'r') as f:
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