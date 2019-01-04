from pathlib import Path

envdir = str((Path.home() / '.envman').resolve())
db_uri = 'sqlite:///{}/envs.db'
db_uri_default = db_uri.format(envdir)
startup_content = '''#!/bin/bash
# Environment: {name}
# Environment path: {path}
# $ENV is the environment's name and $ENV_PATH is the environment's path
# For example, to activate a virtualenv in the environment's directory:
#  source $ENV_PATH/venv/bin/activate
# To add a bin directory to the PATH:
#  export PATH="$ENV_PATH/bin:$PATH"
'''
startup_file = 'start.sh'
global_startup = f'{envdir}/{startup_file}'
global_startup_content = '''#!/bin/bash
# This file is executed every time a new environment is entered. 
# $ENV is the environment's name and $ENV_PATH is the environment's path
export PS1="[$ENV] $PS1"
'''
envs_dir = f'envs'

# export ENVMAN_OLDPS1="$PS1" # Please do not remove this unless you know what you are doing - Used to be L20
