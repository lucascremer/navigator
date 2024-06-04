import subprocess
from lib.messages import error

class Tool:
    def __init__(self, name, update_cmd, source_cmd, build_cmd, clean_cmd):
        self.name = name
        self.update_cmd = update_cmd
        self.source_cmd = source_cmd
        self.build_cmd = build_cmd
        self.clean_cmd = clean_cmd

        # check if the tool is up-to-date
        self.check_update()


    def check_update(self):
        try:
            result = subprocess.run(f'cd {self.path} && git status', text=True, capture_output=True, check=True)
            
        except Exception as exc:
            error(exc, f'Failed to check if {self.name} is up-to-date.')