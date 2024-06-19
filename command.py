import subprocess

from navigator.messages import error
from navigator.utils import blue


class NavigatorCommand:
    def __init__(self, cmd_nav, func, arg_names, description=''):
        self.cmd_nav = cmd_nav
        self.func = func
        self.description = description
        self.n_args = len(arg_names)
        self.arg_help_string = ' '.join([f'<{arg}>' for arg in arg_names])

    def execute(self, *args):
        if len(args) == 1 and args[0] == 'help':
            self.help()
            return
            
        if len(args) != self.n_args:
            error(f'Expected {self.n_args} arguments, but got {len(args)}')
            return

        return self.func(*args)

    def help(self):
        help_string = f'\n{self.description}\n\nUsage: {self.cmd_nav} ' + self.arg_help_string + '\n\n'
        print(blue(help_string))
        return
    

class StepCommand:
    def __init__(self, cmd_nav, shellcommand, step_path, arg_names, description=''):
        self.cmd_nav = cmd_nav
        self.shellcommand = shellcommand
        self.step_path = step_path
        self.arg_help_string = ' '.join([f'--{arg} <{arg}>' for arg in arg_names])
        self.description = description

    def execute(self, *args):
        if len(args) == 1 and args[0] == 'help':
            self.help()
            return

        arguments = ' '.join(args)
        subprocess.run(f'cd {self.step_path} && {self.shellcommand} {arguments}', shell=True)
        return
    
    def help(self):
        help_string = f'\n{self.description}\n\nUsage: {self.cmd_nav} ' + self.arg_help_string + '\n\n'
        print(blue(help_string))
        return