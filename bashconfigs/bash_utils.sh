#!/bin/bash
## Collection of bash utility functions for use in scripts

# Global aliases

alias _cp="/usr/bin/cp"

cp() {
    rsync -a --partial --progress $@
}

# If VERBOSE is set to true, echo the provided message
verbose() {
    if [ "$VERBOSE" = true ]; then
        echo ""
        echo "[VERBOSE]: $1"
    fi
}

decorate_d() {
    if [ "$DEBUG" = true ]; then
        echo ""
        echo "[DEBUG]: ===================="
        echo "[DEBUG]: $1"
        echo "[DEBUG]: ===================="
    fi
}

decorate_v() {
    if [ "$VERBOSE" = true ]; then
        echo ""
        echo "[VERBOSE]: ===================="
        echo "[VERBOSE]: $1"
        echo "[VERBOSE]: ===================="
    fi
}

decorate_e() {
    echo ""
    echo "[**ERROR**]: ===================="
    echo "[**ERROR**]: $1"
    echo "[**ERROR**]: ===================="
}

decorate_w() {
    echo ""
    echo "[*WARNING*]: ===================="
    echo "[*WARNING*]: $1"
    echo "[*WARNING*]: ===================="
}

decorate() {
    echo ""
    echo "===================="
    echo "$1"
    echo "===================="
}

# If DEBUG is set to true, echo the provided message
debug() {
    if [ "$DEBUG" = true ]; then
        echo ""
        echo "[DEBUG]: $1"
    fi
}

# Echo the message as an error
error() {
    echo ""
    echo "[**ERROR**]: $1" >&2
}

# Echo the message as a warning
warn() {
    echo ""
    echo "[*WARNING*]: $1" >&2
}

# Check for common CLI arguments
process_args() {
    decorate_d "Processing args"
    OPTIND=1

    VERBOSE=false
    # Check if the $BASH_VERBOSE environment variable is set
    if [ -n $BASH_VERBOSE ]; then
        VERBOSE=$BASH_VERBOSE
    fi

    DEBUG=false
    # Check if the $BASH_DEBUG environment variable is set
    if [ -n $BASH_DEBUG ]; then
        DEBUG=$BASH_DEBUG
    fi

    # Parse command line arguments
    while getopts 'vdq' flag; do
        case "${flag}" in
            v) VERBOSE=true ;;
            d) DEBUG=true ;;
            q) VERBOSE=false; DEBUG=false ;;
            *) warn "Unexpected option ${flag}" ;;
        esac
    done
    verbose "Verbose mode enabled"
    debug "Debug mode enabled"
}

# Process command line arguments
process_args $@
# Set the directory of the bash_utils.sh script
export BASH_UTILS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
debug "BASH_UTILS_DIR: $BASH_UTILS_DIR"

# Source the bash_vars.sh script
debug "Sourcing bash_vars.sh"
source $BASH_UTILS_DIR/bash_vars.sh

# Check if a provided command is available
cmd_exists() {
    if [ -x "$(command -v $1)" ]; then
        return 0
    else
        return 1
    fi
}

# Check if the system has sudo
system_has_sudo() {
    # Check if the sudo command exists
    if cmd_exists sudo; then
        return 0
    else
        return 1
    fi
}

# Attempt to run a provided command, using sudo if available
try_sudo() {
    # Check if the user is root and sudo is available
    if [ "$(id -u)" -ne 0 ] && system_has_sudo; then
        # If not, try to use sudo
        sudo "$@"
    else
        # If the user is root, just run the command
        "$@"
    fi
}

list_to_str() {
    local _LIST=($1)
    local _STR=""
    for i in ${_LIST[@]}; do
        _STR="${_STR}${i}${2}"
    done
    echo $_STR
}

# Check if an item is in a list
contains() {
    LIST=$1
    ITEM=$2

    for i in $LIST; do
        if [ $i == $ITEM ]; then
            return 0
        fi
    done
}

# Shortcut function to mount a partition using the last 2 characters of the device name
# and the last character of the mount path
mnt() {
    PART=$1
    PATH_NUM=$2

    if [ -n $PART ]; then
        DEVICE="/dev/sd$PART"
    else
        error "No partition provided"
        return
    fi

    if [ -n $PATH_NUM ]; then
        MOUNT_PATH="/media/joseph/external$PATH_NUM"
    else
        error "No path number provided"
        return
    fi

    if [ -b $DEVICE ]; then
        if [ ! -d $MOUNT_PATH ]; then
            warn "Mount path $MOUNT_PATH not found. Creating..."
            try_sudo mkdir -p $MOUNT_PATH
        fi
        verbose "Mounting $DEVICE to $MOUNT_PATH"
        try_sudo mount $DEVICE $MOUNT_PATH
    else
        error "Device $DEVICE not found"
    fi
}

# Check if a provided file exists
file_exists() {
    if [ -f "$1" ]; then
        return 0
    else
        return 1
    fi
}

# Try to install the provided package
install_pkg() {
    if [ -z $1 ]; then
        error "No package provided"
        return
    fi

    if cmd_exists apt-get; then
        try_sudo apt-get install -y $1
    elif cmd_exists yum; then
        try_sudo yum install -y $1
    elif cmd_exists dnf; then
        try_sudo dnf install -y $1
    else
        error "No package manager found"
    fi
}

parse_args() {
    local _ARGS_STR=$(list_to_str "$@")
    decorate_d "Parsing args: $_ARGS_STR"
    OPTIND=1

    local _OPTS_STR=""
    for key in "${!CMD_ARGS[@]}"; do
        _OPTS_STR="${_OPTS_STR}${key}"
    done

    debug "Options string: $_OPTS_STR"

    while getopts "${_OPTS_STR}" flag; do
    
        for key in "${!CMD_ARGS[@]}"; do
            local _DEFAULT="${CMD_ARGS[$key]}"
            local _TYPE="${CMD_ARG_TYPES[$key]}"
            
            arg_flag="${key//:/}"
            
            
            if [ "$flag" == "$arg_flag" ]; then

                if [ "$_TYPE" == "boolean" ]; then

                    if [ "$_DEFAULT" == true ]; then
                        CMD_ARGS["$key"]=false
                    else
                        CMD_ARGS["$key"]=true
                    fi
                elif [ "$_TYPE" == "string" ]; then
                    CMD_ARGS["$key"]="${OPTARG}"
                elif [ "$_TYPE" == "list" ]; then
                    if [ -z "${CMD_ARGS[$key]}" ]; then
                        CMD_ARGS["$key"]="${OPTARG}"
                    else
                        CMD_ARGS["$key"]+="${ARG_SEPARATOR}${OPTARG}"
                    fi
                fi

                debug "CMD_ARGS[$key]: ${CMD_ARGS[$key]}"
                
            fi
        done
    done
}

clear_args() {
    decorate_d "Clearing args"

    for key in "${!CMD_ARGS[@]}"; do
        debug "Unsetting CMD_ARGS.$key"
        unset CMD_ARGS["$key"]
    done


    for key in "${!CMD_ARG_TYPES[@]}"; do
        debug "Unsetting CMD_ARG_TYPES.$key"
        unset CMD_ARG_TYPES["$key"]
    done
}

get_cmd_arg() {
    local key=$1
    local value="${CMD_ARGS[$key]}"
    local type="${CMD_ARG_TYPES[$key]}"
    if [ "$type" == "list" ]; then
        IFS=$ARG_SEPARATOR read -r -a value <<< "$value"
        # Return the array
        echo "${value[@]}"
    else
        echo "$value"
    fi
}

# Define the command line args
# Colons are interpreted via the default getopts behavior
# For example, ":v:" means that the v flag requires an argument
# You can assign a default value to a parameter by using the equals sign
# For example, "d=1" means that the d flag defaults to 1
# The = and proceeding characters are removed from the flag name
# For example, "d=1" becomes "d"
# The type will be one of boolean, string, or list
# If the flag has no colon after, it is a boolean flag
# If the flag has a colon after, it is a string flag
# If the flag has an * after, it is a list flag
define_args() {
    decorate_d "Defining args"
    
    clear_args 


    local str_pattern="^.+?:$"
    local list_pattern="^.+?\*$"

    for pair in "$@"; do
        local _FLAG_NAME=""
        local _FLAG_TYPE=""
        local _FLAG_DEFAULT=""

        # Check if the pair contains an equals sign
        if [[ $pair == *"="* ]]; then
            _FLAG_NAME="${pair%=*}"
            _FLAG_DEFAULT="${pair#*=}"
        else
            _FLAG_NAME="$pair"
        fi

        # Determine the type of the flag
        if [[ $_FLAG_NAME =~ $str_pattern ]]; then
            _FLAG_TYPE="string"
        elif [[ $_FLAG_NAME =~ $list_pattern ]]; then
            _FLAG_TYPE="list"
            # Remove the * from the flag name
            _FLAG_NAME="${_FLAG_NAME%?}"
            # Append colon if it's missing
            if [[ $_FLAG_NAME != *":"* ]]; then
                _FLAG_NAME="${_FLAG_NAME}:"
            fi
        else
            _FLAG_TYPE="boolean"
        fi

        # Default boolean flags to false if no default is provided
        if [ "$_FLAG_TYPE" == "boolean"  ]; then
            if [ -z "$_FLAG_DEFAULT" ]; then
                _FLAG_DEFAULT=false
            fi
        fi
        
        
        CMD_ARGS["$_FLAG_NAME"]=$_FLAG_DEFAULT
        CMD_ARG_TYPES["$_FLAG_NAME"]=$_FLAG_TYPE
        debug "Defined $_FLAG_NAME as $_FLAG_TYPE with default $_FLAG_DEFAULT"
    done
}





# Retrieves the value of ls $1 and stores it in LS_AS_LIST_RESULT as an array
ls_as_list() {
    LS_PATH=$1
    if [ -z $LS_PATH ]; then
        LS_PATH="."
    fi

    ITEMS=$(ls $LS_PATH)
    LS_AS_LIST_RESULT=()
    for ITEM in $ITEMS; do
        LS_AS_LIST_RESULT+=($ITEM)
    done
}

# Source the known util scripts that are in the same directory as the current script
source_imports() {
    echo "Sourcing imports..."
    ls_as_list $BASH_UTILS_DIR

    for SCRIPT in ${IMPORT_SCRIPTS[@]}; do
        SCRIPT_PATH="$BASH_UTILS_DIR/$SCRIPT"

        # Check if the script is in the list of files and in the script directory
        if contains $LS_AS_LIST_RESULT $SCRIPT && file_exists $SCRIPT_PATH; then
            verbose "Sourcing $SCRIPT_PATH"
            source $SCRIPT_PATH
        else
            warn "Script $SCRIPT not found in $BASH_UTILS_DIR"
        fi
    done
}

source_imports

install_cyberpanel() {
    sh <(curl https://cyberpanel.net/install.sh || wget -O - https://cyberpanel.net/install.sh)
}