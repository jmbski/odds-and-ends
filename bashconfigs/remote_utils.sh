#!/bin/bash
## Collection of bash utility functions for use with remote servers



# Upload a file to a remote host
upload() {
    decorate_d "Running upload command"

    local flag_pattern="^-[a-zA-Z]$"
    
    LOCAL_PATH=$1
    shift

    REMOTE_PATH=$1
    shift
    
    USER=""
    HOST=""
    
    # if $1 isn't a flag, then it's the user
    if [[ ! $1 =~ $flag_pattern ]]; then
        USER=$1
        shift
    fi


    if [[ ! $1 =~ $flag_pattern ]]; then
        HOST=$1
        shift
    fi

    define_args "c" "i:*" "e:*"

    parse_args "$@"

    COPY_SYMLINKS=$(get_cmd_arg "c")
    INCLUDES=$(get_cmd_arg "i:")
    EXCLUDES=$(get_cmd_arg "e:")

    debug "LOCAL_PATH: $LOCAL_PATH"
    debug "REMOTE_PATH: $REMOTE_PATH"
    for i in $INCLUDES; do
        debug "INCLUDES: $i"
    done
    for e in $EXCLUDES; do
        debug "EXCLUDES: $e"
    done

    
    if [ -z $LOCAL_PATH ]; then
        error "No file provided for upload"
        return
    fi

    if [ -z $REMOTE_PATH ]; then
        error "No destination provided for upload"
        return
    fi

    if [ -z $USER ]; then
        if [ -n $DEFAULT_USER ]; then
            warn "No user provided for upload. Using default user $DEFAULT_USER"
            USER=$DEFAULT_USER
        else
            error "No user provided for upload"
            return
        fi
    fi

    if [ -z $HOST ]; then
        if [ -n $DEFAULT_HOST ]; then
            warn "No host provided for upload. Using default host $DEFAULT_HOST"
            HOST=$DEFAULT_HOST
        else
            error "No host provided for upload"
            return
        fi
    fi

    verbose "Uploading ${LOCAL_PATH} to ${USER}@${HOST}:${REMOTE_PATH}"

    CMD_OPTS="-a --progress --partial -e ssh"

    if [ -n $COPY_SYMLINKS ]; then
        CMD_OPTS="${CMD_OPTS} --copy-links"
    fi
    
    for i in $INCLUDES; do
        CMD_OPTS="${CMD_OPTS} --include=${i}"
    done

    for e in $EXCLUDES; do
        CMD_OPTS="${CMD_OPTS} --exclude=${e}"
    done

    CMD_STR="rsync ${CMD_OPTS} ${LOCAL_PATH} ${USER}@${HOST}:${REMOTE_PATH}"
    debug "CMD_STR: $CMD_STR"
    try_sudo $CMD_STR
}

# Upload a file to a remote host using the default user and host
simple_upload() {
    LOCAL_PATH=$1
    REMOTE_PATH=$2
    USER=$DEFAULT_USER
    HOST=$DEFAULT_HOST

    if [ -z $LOCAL_PATH ]; then
        error "No file provided for upload"
        return
    fi

    if [ -z $REMOTE_PATH ]; then
        REMOTE_PATH=$(basename $LOCAL_PATH)
        warn "No destination provided for upload. Using default destination: $REMOTE_PATH"
    fi
    
    upload $LOCAL_PATH $REMOTE_PATH $USER $HOST
}

artssh() {
    USER=$1

    if [ -z $USER ]; then
        USER=$DEFAULT_USER
    fi

    ssh $USER@$DEFAULT_HOST
}

artcopyid() {
    USER=$1

    if [ -z $USER ]; then
        USER=$DEFAULT_USER
    fi

    ssh-copy-id $USER@$DEFAULT_HOST
}

artftp() {
    USER=$1

    if [ -z $USER ]; then
        USER=$DEFAULT_USER
    fi

    sftp $USER@$DEFAULT_HOST
}

artclearssh() {
    USER=$1

    if [ -z "$USER" ]; then
        USER="joseph"
    fi

    if [ "$USER" == "root" ]; then
        try_sudo ssh-keygen -f "/root/.ssh/known_hosts" -R $DEFAULT_HOST
    else
        try_sudo ssh-keygen -f "$HOME/.ssh/known_hosts" -R $DEFAULT_HOST
    fi
}