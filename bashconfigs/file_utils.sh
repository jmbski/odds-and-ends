#!/bin/bash
## Collection of bash utility functions for managing file interactions

# Check if a provided directory exists
dir_exists() {
    if [ -d "$1" ]; then
        return 0
    else
        return 1
    fi
}

# Check if a provided path exists
path_exists() {
    if [ -e "$1" ]; then
        return 0
    else
        return 1
    fi
}

# Check if a provided path is a directory
is_dir() {
    if [ -d "$1" ]; then
        return 0
    else
        return 1
    fi
}

# Unlink all symlinks in the provided directory, defaults to the current directory
unlink_all() {
    UL_PATH=${1:-.}
    verbose "Unlinking all symlinks in $UL_PATH"
    
    if is_dir $UL_PATH; then
        for file in $(ls -l $UL_PATH | grep ^l | awk '{print $9}'); do
            verbose "Unlinking $file"
            try_sudo unlink $UL_PATH/$file
        done
    else
        if file_exists $UL_PATH; then
            verbose "Unlinking $UL_PATH"
            try_sudo unlink $UL_PATH
        elif file_exists $(pwd)/$UL_PATH; then
            verbose "Unlinking $UL_PATH"
            try_sudo unlink $(pwd)/$UL_PATH
        else
            error "No file or directory found at $UL_PATH"
        fi
    fi
}

bak() {
    local file=$1
    if [ -f "$file" ]; then
        if is_symlink "$file"; then
            echo "$file is already a symlink, unlinking"
            sudo unlink "$file"
        else
            echo "Backing up $file to $file.bak"
            sudo mv "$file" "$file.bak"
        fi
    else
        error "No file found at $file"
    fi
}

# Check if the provided path is in $PATH, and if not, add it
add_to_path() {
    local path=$1
    if [[ ":$PATH:" == *":$path:"* ]]; then
        verbose "$path is already in \$PATH"
    else
        verbose "Adding $path to \$PATH"
        export PATH=$PATH:$path
    fi
}

modenv() {
    local _ACTION=$1
    local _KEY=$2
    local _VALUE="${@:3}"
    local _ENV=/etc/environment

    if [ -z $_ACTION ]; then
        error "No action provided"
        return
    fi

    if [ -z $_KEY ]; then
        error "No key provided"
        return
    fi

    case $_ACTION in
        "set")
            if [ -z "$_VALUE" ]; then
                error "No value provided"
                return
            fi
            # Check if the key is already set
            if grep -q "^export $_KEY=" $_ENV; then
                verbose "$_KEY already set in $_ENV"
                try_sudo sed -i "s/^export $_KEY=.*/$_KEY=\"$_VALUE\"/" $_ENV
            else
                verbose "Adding $_KEY to $_ENV"
                echo "export $_KEY=\"$_VALUE\"" | try_sudo tee -a $_ENV
            fi
            ;;
        "unset")
            if grep -q "^export $_KEY=" $_ENV; then
                verbose "Unsetting $_KEY in $_ENV"
                try_sudo sed -i "/^export $_KEY=/d" $_ENV
            else
                verbose "$_KEY not found in $_ENV"
            fi
            unset $_KEY
            ;;
        *) error "Invalid action $_ACTION"
            ;;
    esac
    source $_ENV
}

set_env_defaults() {
    local _ENV_DEFAULTS=$1

    mapfile -t lines < $_ENV_DEFAULTS

    # Iterate over the array using a for loop
    for line in "${lines[@]}"; do
        if [ -n "$line" ] && [ "${line:0:1}" != "#" ]; then
            # Split the line into an array
            IFS='=' read -r -a parts <<< "$line"
            
            # Assign the values, and drop 'export' from the key if it exists
            key=${parts[0]}
            value=${parts[1]}
            if [ "${key:0:7}" == "export " ]; then
                key=${key:7}
            fi
            
            modenv set $key $value
        fi
    done
}