#!/bin/bash
# This file is executed every time a new environment is entered. $ENV is the environment's name and $ENV_PATH is the environment's path
export ENVMAN_OLDPS1="$PS1" # Please do not remove this unless you know what you are doing
export PS1="[$ENV] $PS1"
