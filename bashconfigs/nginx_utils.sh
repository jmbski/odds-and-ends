#!/bin/bash
## Collection of bash utility functions for use with Nginx




ngxreload() {
    verbose "Reloading Nginx"
    try_sudo systemctl reload nginx-custom
}

ngxstop() {
    verbose "Stopping Nginx"
    try_sudo systemctl stop nginx-custom
}

ngxstart() {
    verbose "Starting Nginx"
    try_sudo systemctl start nginx-custom
}

ngxrestart() {
    verbose "Restarting Nginx"
    try_sudo systemctl restart nginx-custom
}

ngxstatus() {
    verbose "Checking Nginx status"
    try_sudo systemctl status nginx-custom
}

ngxtest() {
    verbose "Testing Nginx configuration"
    try_sudo nginx -t
}

ngxconf() {
    verbose "Opening Nginx configuration"
    if [ -z $EDITOR ]; then
        EDITOR="vim"
    fi

    if [ -n $1 ]; then
        EDITOR=$1
    fi

    if [ cmd_exists $EDITOR ]; then
        try_sudo $EDITOR $NGX_CONF
    fi
}

ngxcurrent_site() {
    ls -l $NGX_ENABLED | grep ^l | awk '{print $9}'
}

tgl_enabled() {
#    if [ -n $DEFAULT_SITE_CONF ]; then
#        SITE_CONF=$DEFAULT_SITE_CONF
#    fi
#    
#    # 
#    if [ -n $1 ]; then
#        verbose "Setting default site configuration to $1"
#        SITE_CONF=$1
#    fi
    if [ -z $1 ]; then
        if [ -n $DEFAULT_SITE_CONF ]; then
            SITE_CONF=$DEFAULT_SITE_CONF
        else
            error "No site configuration provided"
            return
        fi
    else
        SITE_CONF=$1
    fi
    

    echo "Enabling $SITE_CONF"
    if [ -z $SITE_CONF ]; then
        error "No site configuration provided"
        return
    fi

    unlink_all $NGX_ENABLED

    verbose "Enabling $SITE_CONF"
    
    try_sudo ln -s $NGX_AVAILABLE/$SITE_CONF $NGX_ENABLED/$SITE_CONF

    ngxreload

    ngxtest

}


get_nginx() {
    # Download the Nginx source
    decorate "Downloading Nginx source"

    try_sudo wget "http://nginx.org/download/nginx-$NGX_VERSION.tar.gz" -P /usr/local/src
    
    echo "Extracting Nginx source to $NGX_SRC_DIR"
    try_sudo tar -xzf $NGX_TAR_PATH -C /usr/local/src
    if [ -d $NGX_SRC_DIR ]; then
        echo "Nginx source extracted to $NGX_SRC_DIR"
    else
        error "Nginx source not found at $NGX_SRC_DIR"
    fi
}

is_installed() {
    # Check if a package is installed
    #dpkg -s $1 &> /dev/null
    if dpkg-query -l $1 &> /dev/null; then
        debug "$1 is installed"
        return 0
    else
        debug "$1 is not installed"
        return 1
    fi
}

install_build_tools() {
    # Install build tools for Nginx
    decorate "Installing build tools for Nginx"
    TOOL_LIBS=("build-essential" "libpcre3" "libpcre3-dev" "zlib1g" "zlib1g-dev" "libssl-dev" "libgd-dev")

    # Iterate through the list of tools, check if they're installed or not, and install them if necessary
    for lib in ${TOOL_LIBS[@]}; do
        if ! is_installed $lib; then
            try_sudo apt-get install -y $lib
        else
            echo "$lib is already installed"
        fi
    done
}

install_pcre() {
    # Clear old PCRE source
    if [ -d $NGX_PCRE_DIR ]; then
        try_sudo rm -rf $NGX_PCRE_DIR
    fi

    # Create PCRE source directory
    try_sudo mkdir -p $NGX_PCRE_DIR
    
    # Download PCRE source
    decorate "Downloading PCRE source"

    try_sudo wget $NGX_PCRE_DL_URI -P /usr/local/src
    TAR_PATH="$NGX_PCRE_DIR.tar.gz"

    # Extract PCRE source
    echo "Extracting PCRE source to $NGX_PCRE_DIR"
    try_sudo tar -xzf $TAR_PATH -C /usr/local/src
    if [ -d $NGX_PCRE_DIR ]; then
        echo "PCRE source extracted to $NGX_PCRE_DIR"
    else
        error "PCRE source not found at $NGX_PCRE_DIR"
    fi

    # Build PCRE
    decorate "Building PCRE"
    cd $NGX_PCRE_DIR

    try_sudo ./configure
    make
    try_sudo make install

    # Clean up PCRE source
    try_sudo rm -rf $TAR_PATH

    # Return to Nginx source directory
    cd $NGX_SRC_DIR

}

update_ngx_configs() {
    BACKUP=false
    while getopts "b" flag; do
        case $flag in
            b) BACKUP=true ;;
            *) warn "Unexpected option ${flag}" ;;
        esac
    done

    debug "Checking if $NGX_AVAILABLE exists"
    if [ ! -d $NGX_AVAILABLE ]; then
        verbose "Creating Nginx available directory"
        try_sudo mkdir -p $NGX_AVAILABLE
    fi

    debug "Checking if $NGX_ENABLED exists"
    if [ ! -d $NGX_ENABLED ]; then
        verbose "Creating Nginx enabled directory"
        try_sudo mkdir -p $NGX_ENABLED
    fi

    debug "Checking if $NGX_SNIPPETS exists"
    if [ ! -d $NGX_SNIPPETS ]; then
        verbose "Creating Nginx snippets directory"
        try_sudo mkdir -p $NGX_SNIPPETS
    fi

    if $BACKUP; then
        bak $NGX_CONF
    fi
    
    verbose "Copying default configuration to $NGX_CONF"
    try_sudo cp $APP_NGX_CONF $NGX_CONF

    verbose "Copying default configuration to $NGX_AVAILABLE"
    try_sudo cp $APP_NGX_SITE_CONF $NGX_DEFAULT_CONF

    verbose "Copying defalt fastcgi-php configuration to $NGX_SNIPPETS"
    try_sudo cp $APP_NGX_FASTCGI_PHP $NGX_FASTCGI_PHP
    
    verbose "Checking links: $NGX_DEFAULT_CONF to $NGX_ENABLED"
    if [ ! -e $NGX_ENABLED/$DEFAULT_SITE_CONF ]; then
        try_sudo ln -s $NGX_DEFAULT_CONF $NGX_ENABLED/$DEFAULT_SITE_CONF
    fi

    if [ ! -f "/run/nginx.pid" ]; then
        verbose "Creating /run/nginx.pid"
        try_sudo touch /run/nginx.pid
    fi
}

build_nginx() {
    # Build Nginx from source
    decorate "Building Nginx from source"

    # Parse options
    OPTIND=1

    # Define configuration options to match with flags
    declare -A OPT_BUILD_FLAGS
    OPT_BUILD_FLAGS["m"]=" --with-mail --with-mail_ssl_module"
    OPT_BUILD_FLAGS["s"]=" --with-http_ssl_module"
    #OPT_BUILD_FLAGS["p"]=" --with-pcre=$NGX_PCRE_DIR"
    OPT_BUILD_FLAGS["d"]=" --with-debug"
    #OPT_BUILD_FLAGS["o"]=" --with-openssl=$NGX_OPENSSL_DIR"

    # Build options string
    local OPT_STR=""
    for key in "${!OPT_BUILD_FLAGS[@]}"; do
        OPT_STR="${OPT_STR}${key}"
    done
    OPT_STR="${OPT_STR}AD"

    # Build configuration flag string
    OPTS=""
    local _DRY_RUN=false
    while getopts "$OPT_STR" flag; do
        case $flag in
            A) for key in "${!OPT_BUILD_FLAGS[@]}"; do
                    local value="${OPT_BUILD_FLAGS[$key]}"
                    if [[ $OPTS != *"$value"* ]]; then
                        OPTS="${OPTS}${OPT_BUILD_FLAGS[$key]}"
                    fi
                done ;;
            D) _DRY_RUN=true ;;
            *) if [[ -n "${OPT_BUILD_FLAGS["$flag"]}" ]]; then
                    local value="${OPT_BUILD_FLAGS["$flag"]}"
                    # Check if the value has been added to opts already
                    if [[ $OPTS != *"$value"* ]]; then
                        OPTS="${OPTS}${OPT_BUILD_FLAGS["$flag"]}"
                    fi
                else
                    echo "Unexpected option ${flag}"
                fi ;;
        esac
    done
    
    if ! _DRY_RUN; then
        remove_nginx
    fi

    if [ ! -d $NGX_TAR_PATH ]; then
        get_nginx
    fi

    if [ ! -d $NGX_SRC_DIR ]; then
        error "Nginx source not found at $NGX_SRC_DIR"
        return
    fi

    install_build_tools

    cd $NGX_SRC_DIR

    echo "CMD: ./configure $OPTS"
    if $_DRY_RUN; then
        return
    fi

    try_sudo ./configure $OPTS
    make
    try_sudo make install


}

remove_nginx() {
    # Remove Nginx source and build
    decorate "Removing Nginx source and build"
    try_sudo rm -rf $NGX_SRC_DIR
    try_sudo apt-get remove nginx nginx-common nginx-full -y
}