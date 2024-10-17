#!/bin/bash
## Simple script to set up default symlinks for bashconfigs

# Variables
_SCRIPTS=(".bashrc" ".profile" ".inputrc" ".vimrc")
_CONFIGS_DIR=$1
if [ -z $_CONFIGS_DIR ]; then
    _CONFIGS_DIR="$HOME/bashconfigs"
fi

# Functions

is_symlink() {
    local file=$1
    if [ -L "$file" ]; then
        return 0
    else
        return 1
    fi
}

update_script() {
    local _ORIG_SCRIPT=$1
    local _CONFIG_SCRIPT=$2

    if [ ! -f "$_CONFIG_SCRIPT" ]; then
        echo "No config file found for $_CONFIG_SCRIPT"
        return
    fi
    
    echo "Checking $_ORIG_SCRIPT"
    if [ -f "$_ORIG_SCRIPT" ]; then
        echo "$_ORIG_SCRIPT exists"
        if is_symlink "$_ORIG_SCRIPT"; then
            echo "$_ORIG_SCRIPT is already a symlink, unlinking"
            sudo unlink "$_ORIG_SCRIPT"
        else
            echo "Backing up $_ORIG_SCRIPT to $_ORIG_SCRIPT.bak"
            sudo mv "$_ORIG_SCRIPT" "$_ORIG_SCRIPT.bak"
        fi
    fi

    echo "Creating symlink for $_ORIG_SCRIPT"
    sudo ln -s "$_CONFIG_SCRIPT" "$_ORIG_SCRIPT"
}

# Backup and create symlinks for each script
for script in "${_SCRIPTS[@]}"; do
    update_script "$HOME/$script" "$_CONFIGS_DIR/$script"
    update_script "/root/$script" "$_CONFIGS_DIR/$script"
done

# Symlink bash_utils.sh
update_script "$HOME/.bash_utils.sh" "$_CONFIGS_DIR/bash_utils.sh"
update_script "/root/.bash_utils.sh" "$_CONFIGS_DIR/bash_utils.sh"

echo "Sourcing $_CONFIGS_DIR/.bashrc"
source "$_CONFIGS_DIR/bash_utils.sh"
#source "$_CONFIGS_DIR/.bashrc"

set_env_defaults "$_CONFIGS_DIR/env_defaults"