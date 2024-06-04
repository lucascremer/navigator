import yaml
from lib.colors import Colors
from lib.messages import error


class Navigator:
    def __init__(self, config_path='analysis_config.yaml'):
        try:
            with open(config_path, 'r') as file:
                self.analysis_config = yaml.safe_load(file)
        except (FileNotFoundError, yaml.YAMLError) as exc:
            error(exc, 'Failed to load the analysis config file.', fatal=True)

        # self.init_tools()


    # def init_tools(self):
    #     for tool in self.analysis_config['tools']:
    #         tool_name = tool
    #         tool_path = tool['path']


    def run(self):
        while True:
            try:
                user_input = input("navigator> ")
                if user_input == "help":
                    print("Available commands: help, exit")
                elif user_input == "exit":
                    self.exit_navigator()
                elif user_input == "status":
                    print(self.analysis_config)
                elif user_input == "":
                    continue
                else:
                    print(f"Unknown command: {user_input}")
            except EOFError: # Ctrl+D
                self.exit_navigator(ctrl_D=True)

    
    def exit_navigator(self, ctrl_D=False):
        if ctrl_D:
            print('exit')
        print(f'Exiting... {Colors.RED}G{Colors.ORANGE}o{Colors.YELLOW}o{Colors.GREEN}d{Colors.CYAN}b{Colors.BLUE}y{Colors.VIOLET}e{Colors.RESET} :)')
        exit(0)