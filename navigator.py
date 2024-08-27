import os
import yaml
import textwrap
import readline

from navigator.command import NavigatorCommand, StepCommand
from navigator.messages import error, warning, info
from navigator.utils import AutoPath, green, red, orange, yellow, cyan, blue, violet, grey, fill_string, print_dict, remove_ansi_codes


class Navigator:
    def __init__(self, config_path):
        try:
            with open(config_path, 'r') as file:
                self.analysis_config = yaml.safe_load(file)
        except (FileNotFoundError, yaml.YAMLError) as exc:
            error('Failed to load the analysis config file.', exc, fatal=True)

        self.history_file = AutoPath(self.analysis_config['history_file'])
        terminal_width = os.get_terminal_size().columns
        self.terminal_width = terminal_width if terminal_width < 120 else 120
        self.cur_step = 'navigator'
        self.init_commands()

        # initialize readline
        readline.set_completer(self.tab_completion)
        readline.parse_and_bind("tab: complete")
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass

    def run(self):
        self.welcome_message()
        while True:
            try:
                user_input = input(f'{self.cur_step}> ')
                readline.write_history_file(self.history_file)
                command = user_input.split(' ')[0]
                args = user_input.split(' ')[1:]
                if command in self.valid_commands:
                    self.valid_commands[command].execute(*args)
                elif user_input.strip() == '':
                    continue
                else:
                    error(f'Unknown command: {command}. Type help for a list of available commands.')
            except EOFError: # Ctrl+D
                self.exit_navigator(ctrl_D=True)
            except KeyboardInterrupt: # Ctrl+C
                print('KeyboardInterrupt')
                continue
            except Exception as exc:
                error('An unexpected error occurred.', exc)
    
    def exit_navigator(self, ctrl_D=False):
        if ctrl_D:
            print('exit')
        print(f'Exiting... {red('G')}{orange('o')}{yellow('o')}{green('d')}{cyan('b')}{blue('y')}{violet('e')} :)')
        exit(0)

    def print_config(self):
        print_dict(self.analysis_config)

    def welcome_message(self):
        lines = [
            ('Welcome to the Navigator!', 'center'),
            (f'Analysis: {self.analysis_config["name"]}', 'center'),
            ('', 'center'),
        ]
        lines += self.get_analysis_steps()
        self.boxed_message(lines)

        return

    def init_commands(self):
        self.valid_navigtor_commands = {
            'config': NavigatorCommand('config', self.print_config, [], 'Prints the loaded analysis config.'),
            'exit': NavigatorCommand('exit', self.exit_navigator, [], 'Exits the navigator right away.'),
            'switch_step': NavigatorCommand('switch_step', self.switch_step, ['step_name'], 'Switches to the specified step.'),
            'leave_step': NavigatorCommand('leave_step', self.leave_step, [], 'Leaves the current step and returns to the main navigator level.'),
            'help': NavigatorCommand('help', self.help, [], 'Prints the help message.'),
            'cmds': NavigatorCommand('cmds', self.print_avail_cmds, [], 'Prints the available commands.'),
            # 'tool_manager': NavigatorCommand('tool_manager', self.tool_manager, [], 'Opens the tool manager.')
        }
        self.step_commands = {}
        self.valid_commands = self.valid_navigtor_commands.copy()

    def switch_step(self, step_name):
        step_names = []
        step_found = False
        for steps in self.analysis_config['analysis_steps'].values():
            for step in steps:
                if step['name'] == step_name:
                    new_step = step
                    step_found = True
                step_names.append(step['name'])
        
        if not step_found:
            error(f'Invalid step: {step}')
            return

        if 'path' not in new_step:
            error(f'Step {step_name} is not yet implemented.')
            return

        # attempt to load the step config file
        try:
            with open(AutoPath(f'{new_step['path']}/stepconfig.yml'), 'r') as file:
                self.step_config = yaml.safe_load(file)
        except (FileNotFoundError, yaml.YAMLError) as exc:
            error(f'Failed to load the step config file for step {new_step['name']}. Has to be called "stepconfig.yml" and placed in the top level folder of your step.', exc)
            return

        self.cur_step = new_step['name']
        
        # load the step commands
        self.step_commands = {}
        for command in self.step_config['step_commands']:
            try:
                self.step_commands[command['name']] = StepCommand(command['name'], command['shellcommand'], new_step['path'], command['usage_args'], command['description'])
            except KeyError as exc:
                warning(f'Failed to load the step command "{command["name"]}": Missing argument {exc}')

        self.valid_commands = {**self.valid_navigtor_commands, **self.step_commands}
        info(f'Switched to step: {self.cur_step}')

        return

    def leave_step(self):
        if self.cur_step == 'navigator':
            info('No active step to leave.')
            return
        self.cur_step = 'navigator'
        self.valid_commands = self.valid_navigtor_commands.copy()
        self.step_config = None
        self.step_commands = {}
        info('Left the current step')
        return
    
    def help(self):
        if self.cur_step == 'navigator':
            lines = [
                (f'Analysis: {self.analysis_config["name"]}', 'center'),
                ('', 'center')
            ]
            lines += self.get_analysis_steps() + [('','center')]
        else:
            lines = [
                (f'Step: {self.cur_step}', 'center'),
                ('', 'center')
            ]
            step_description = self.step_config['description']
            for desc_line in step_description.split('\n'):
                lines.append((desc_line, 'left'))
            lines += [('','center')]
        lines += self.available_commands()
        lines += [('','center')]
        lines += [('If you need help with a specific command, type "<command> help".', 'left')]
        
        self.boxed_message(lines)
        return

    def boxed_message(self, lines):
        # limit text to terminal width
        limited_lines = []
        alignments = []
        for line in lines:
            if type(line) == tuple:
                n_ansis = len(line[0]) - len(remove_ansi_codes(line[0]))
                wrapped_lines = textwrap.fill(line[0], width=self.terminal_width+n_ansis-4).split('\n')
                alignment = line[1]
            elif type(line) == str:
                n_ansis = len(line) - len(remove_ansi_codes(line))
                wrapped_lines = textwrap.fill(line, width=self.terminal_width+n_ansis-4).split('\n')
                alignment = 'left'
            limited_lines.extend(wrapped_lines)
            alignments.extend([alignment]*len(wrapped_lines))

        print(cyan(f'+{"-"*(self.terminal_width-2)}+'))
        for line, alignment in zip(limited_lines, alignments):
            print(cyan('| ') + fill_string(line, self.terminal_width-4, alignment=alignment) + cyan(' |'))
        print(cyan(f'+{"-"*(self.terminal_width-2)}+'))

        return

    def available_commands(self):
        lines = [
            ('Available commands:', 'left')
        ]
        step_commands = '   '.join(self.step_commands.keys())
        navigator_commands = '   '.join(self.valid_navigtor_commands.keys())
        step_commands_wrapped = textwrap.wrap(step_commands, width=self.terminal_width-4, initial_indent=' '*2, subsequent_indent=' '*2)
        navigator_commands_wrapped = textwrap.wrap(navigator_commands, width=self.terminal_width-4, initial_indent=' '*2, subsequent_indent=' '*2)
        for line in step_commands_wrapped:
            lines.append((yellow(line), 'left'))
        for line in navigator_commands_wrapped:
            lines.append((orange(line), 'left'))

        return lines

    def get_analysis_steps(self):
        lines = [
            ('The analysis consists of the following steps:', 'left')
        ]
        for step_level in self.analysis_config['analysis_steps']:
            step_names = ''
            for step in self.analysis_config['analysis_steps'][step_level]:
                if 'path' not in step:
                    step_names += grey(step["name"]) + '   '
                else:
                    step_names += yellow(step["name"]) + '   '
            lines.append((f'  {step_level}: {step_names}', 'left'))

        return lines

    def print_avail_cmds(self):
        cmds = self.available_commands()
        self.boxed_message(cmds)
        return
    
    def tab_completion(self, text, state):
        options = [command for command in self.valid_commands.keys() if command.startswith(text)]
        try:
            return options[state]
        except IndexError:
            return None