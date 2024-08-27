# Navigator

Disclaimer: This is heavily influenced by the functionalities i needed for my HEP phd
analysis, but they might be also useful for other analyses. Furthermore i am not a highly
experienced programmer, so there are for sure better/more efficient way to achieve these
things i describe below, which i dont know of. Any help/comments are appreciated :)

This tool is designed to help you structure your code for your analyses. The basic idea is
that your analysis consists of certain steps, each of which has its own code, variables and
paths (more details later). Furthermore, one central `analysis_config.yml` is used to link
all the steps and provide variables/paths that are used across multiple steps. Two other key
concepts are, that you can still
- edit your code while you are in this shell and changes will be considered
- execute your scripts as usual from the normal terminal
Navigator is just meant to be a higher-level interface, which helps you to keep track of all
your scripts, their execute order and their purpose as well as helping others to understand
the structure of your code.

## Basics
### Dependencies
I used a micromamba environment with 
- python 3.12.5
- pyyaml 6.0.2

### Usage

Assuming you have completed the setup below and ideally have at least one analysis step ready
(see below), you can start a navigator session by executing the python start file
```
python start_navigator.py
```
Then you should have a prompt looking like this
```
navigator> 
```
You can type `help` to get an overview of your analysis, the available steps and the available
commands. The most important command is `switch_step`, which let you enter the specified step
```
switch_step step1
```
Then you can do `help` again to get an overview of this step (based on the information you
provided in the `stepconfig.yml`) and see which new commands are available in this step.
You can also always do
```
<some command> help
```
to get a description of the command and how to use it (given you provided the info when defining
the step command in your step config).
You can leave by typing `exit`/`Ctrl+D`, interrupt commands with `Ctrl+C`, use tab for 
auto-completion (at least for the available commands), scroll through your previous commands
with the arrow keys and do reverse search of your commands with `Ctrl+R`.

### Setup

Clone this repo and add it to your `PYTHONPATH` so that python can find it as a package. You
can achieve this by either cloning this repo at a location inside your current `PYTHONPATH`
or adding this to your `~/.bashrc`
```
export PYTHONPATH="<path-to-the-parent-directory>:$PYTHONPATH"
```
and replacing the `<...>` with the path to the directory in which you cloned this repo. You
can then start a navigator session by creating a python script which imports the Navigator base
class, creates a Navigator instance by passing the path to the central analysis config and
execute its run command, e.g. something like (using `click` is of course optional)
```python
import click

from navigator.navigator import Navigator


@click.command()
@click.option('--config', help='Path to the analysis config.')
def main(config):
    navigator = Navigator(config)
    navigator.run()


if __name__ == '__main__':
    main()
```
After that, you just have to execute the script.

## Central Analysis Config
The central analysis yaml config has to contain some basic information, so that the navigator
tool is able to be used correctly. Here is a minimal layout:
```yaml
name: <name of your analysis>
history_file: <path to your history file>

analysis_steps:
    1:
        - name: step1
          path: <path to step1>
    2:
        - name: step2.1
          path: <path to step2.1>
        - name: step2.2
          path <path to step2.2>
    3:
        - name: step3
          path: <path to step3>
```
The history file logs your history of commands used inside the navigator shell (just like
`.bash_history`) and is required to ensure funtionalities like scrolling through old commands
(arrow keys) and reverse search (`ctrl + R`). The analysis steps section is used to link your
different steps and sort them in the right order. In the above example analysis, step1 would
has to be done first, then 2.1 and 2.2 and in the end step3. It doesn't matter in which order
steps are executed that are on the same step level (e.g. 2.1 and 2.2). If a step has no path
specified it is considered a future step, which is not yet implemented, but can still be added
already for a better overview.
You can add any number of new variables to the analysis config you need.

### Analysis Step

The analysis step is the key building block in the navigator framework. Each step has to include
a file in the the corresponding step folder called `stepconfig.yml`. Basic layout of this file:
```yaml
name: step1
description: |
  This is an analysis step. In this step blabla is done.

  Manual:
    1. Create dummy data (create_dummy_data)
    2. Preprocess data (preprocess_data)
    3. Make plot (create_plot)

# paths (not exactly required, but often useful to add these)
analysis_config_path: <path to analysis config>
step_path: <path to step1>

step_commands:
  - name: create_dummy_data
    shellcommand: 'python bin/create_dummy_data.py'
    usage_args: '--dummy_argument <dummy argument>'
    description: 'This create the dummy data for step1 based on the given dummy parameter'
  - name: preprocess_data
    shellcommand: 'python bin/preprocess_data.py'
    usage_args: ''
    description: 'Preprocess the data and make it ready for the plot'
  - name: create_plot
    shellcommand: 'python bin/create_plot.py'
    usage_args: ''
    description: 'Create the final plot'
```
The description can be used to give you an overview of the step and in which order commands
have to executed. The other key ingredient are the step commands, which are commands that
execute the scripts corresponding to this step. A step command includes
- `name`: the name/command that you call in navigator
- `shellcommand`: what you would type in the shell to execute the script (assuming you are
  in the step folder and are using the same package environment as you used to start navigator)
- `usage_args`: description of which additional command line arguments the script accepts
- `description`: Explanation of the functionality/purpose of the command
Besides that you can again include any additional variables in this config relevant for this
step.

## Advanced
### Hints / Suggested Layout
I used the following folder structure for each of my analysis steps (corresponding to the
example above):
```
- analysis_steps
  - step1
    - bin (put all file corresponding to the step commands here)
      - create_dummy_data.py
      - preprocess_data.py
      - create_plot.py
    - scripts (for any other files required for the step commands)
      - dummy_file.txt
    - stepconfig.yml
    - steputils.py (library file containing central python functions for this step)
  ...(other steps)
```
I then added the `analysis_steps` folder to my `PYTHONPATH`, so that i am able to include
functions from `steputils.py` in my scripts with (i wouldnt recommend numbers in your folder
names, as this causes issues i think, when importing like this)
```python
from step1.steputils import load_step_config, load_analysis_config
```
I added these `load_config` functions in each of my `steputils.py` so that i can load in
these configs at any time and access central variables, which are used to configure the
behaviour (e.g. where software is located, etc) of my scripts. Just for completeness, the
definition of these functions (AutoPath is a helper class of the navigator tool, details
below)
```python
import os
import yaml
from navigator.utils import AutoPath


def load_step_config():
    config_path = AutoPath(os.path.dirname(__file__)) + 'stepconfig.yml'
    
    with open(config_path, 'r') as configfile:
        config = yaml.safe_load(configfile)

    return config


def load_analysis_config():
    step_config = load_step_config()
    analysis_config_path = AutoPath(step_config['analysis_config_path'])

    with open(analysis_config_path, 'r') as analysis_config_file:
        analysis_config = yaml.safe_load(analysis_config_file)

    return analysis_config
```

Often i have to use external software, which is not included in my software environment
(e.g. some tools of your collaboration which you build from source, etc). There are 2
steps to deal with that:
1) At end of my analysis config, i have a section configuring the extra tools i use.
```yaml
tools:
  random_tool:
    path: ~/Desktop/tools/random_tool
    source_cmd: cd ~/Desktop/tools/random_tool/build && source setup.sh && cd -
```
2) I have a corresponding step command with an associated python file `run_tool.py` in
my bin folder. In this script i use the `subprocess.run` command to execute commands in a
shell (like you would normally do in the terminal). To the normal command you would use to
run your tool, you prepend the source command which you would use to setup your tool in the
shell. In addition i use the `get_fresh_env` command from navigator (more details on setup
of this command below) to load in the environment variables from a fresh shell, as otherwise
`subprocess.run` uses the environment varibales from you current shell, which might conflict
with your tool.
```python
import subprocess

from navigator.utils import AutoPath, get_fresh_env
from step1.steputils import load_analysis_config


def main():
    fresh_env = get_fresh_env()
    analysis_config = load_analysis_config()
    tool = analysis_config['tools']['FastFrames']
    tool_source_cmd = ff_tool['source_cmd']
    some_argument = 'tool_argument'

    command = tool_source_cmd + f'&& run_tool --some_tool_argument {some_argument}'    
    subprocess.run(command, shell=True, env=fresh_env)


if __name__ == '__main__':
    main()
```

I added an alias to my bashrc to always able to quickly start navigator:
```bash
alias nav="cd <path to the folder containing the start file>; python start_navigator.py; cd - > /dev/null"
```


## Quality of Life Features
### AutoPath
I often want to use `~` in my paths to shorten them. However, many functions in python dont
expand `~` to the path of your home and therefore fail. Therefore i added the `AutoPath` class
to navigator which is basically the `Path` from `pathlib`, but it automatically expands the
`~`. It can be imported by
```python
from navigator.utils import AutoPath
```
and initialised by passing a path
```python
expand_path = AutoPath('~/Desktop/some_folder')
```
You can then expand this path further like this
```python
file = expand_path + 'another_folder/file_in_folder.txt'
file = expand_path / 'another_folder/file_in_folder.txt'
```

### Fresh envs
I am using several extra tools, which are not included in my basic software environment and
are build from source. If i want to execute them with `subprocess.run` i want a fresh
environment (like opening a new terminal) to avoid any conflicts from the tool with my
current software environment. Therefore i implemented the `get_fresh_env` command in
`navigator.utils` to fetch the environment variables of a fresh shell from a file in your
home called `.fresh_env`. For this file to exist you have to add the following line in your
bashrc (presumably at the end)
```bash
env > ~/.fresh_env
```
Now, whenever you open a new terminal the environment variables are stored in this file,
can be loaded with the `get_fresh_env` command and passed to the subprocess command. Example
python file for that in *Hints / Suggested Layout* (at the bottom).