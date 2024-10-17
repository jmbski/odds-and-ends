#!/bin/bash
## Global variables for use with the bash_utils scripts


# List of known util scripts to import
IMPORT_SCRIPTS=(\
    "file_utils.sh"\
    "service_utils.sh"\
    "nginx_utils.sh"\
    "remote_utils.sh"\
)

# Command parsing variables
declare -A CMD_ARGS
declare -A CMD_ARG_TYPES

export ARG_SEPARATOR=" %%%% "

# App variables
export APP_DIR="$HOME/app"
export APP_NGX_DIR="$APP_DIR/nginx"
export APP_NGX_CONF="$APP_NGX_DIR/nginx.conf"
export APP_NGX_SITE_CONF="$APP_NGX_DIR/$DEFAULT_SITE_CONF"
export APP_NGX_FASTCGI_PHP="$APP_NGX_DIR/fastcgi-php.conf"

export APP_NG_DIST="$APP_DIR/frontend/$APP_NAME/dist/$APP_NAME/browser"

export APP_BACKEND_DIR="$APP_DIR/backend/$APP_NAME"

# Nginx Variables

export NGX_DIR="/usr/local/nginx"
export NGX_BIN_DIR="$NGX_DIR/sbin"
export NGX_BIN="$NGX_BIN_DIR/nginx"
export NGX_CONF_DIR="$NGX_DIR/conf"
export NGX_CONF="$NGX_CONF_DIR/nginx.conf"
export NGX_SNIPPETS="$NGX_CONF_DIR/snippets"
export NGX_LOGS_DIR="$NGX_DIR/logs"

export NGX_ENABLED="$NGX_CONF_DIR/sites-enabled"
export NGX_AVAILABLE="$NGX_CONF_DIR/sites-available"
export NGX_DEFAULT_CONF=$NGX_AVAILABLE/$DEFAULT_SITE_CONF


# Nginx Install Variables
export NGX_VERSION="1.27.2"
export NGX_SRC_DIR="/usr/local/src/nginx-$NGX_VERSION"
export NGX_TAR_PATH="$NGX_SRC_DIR.tar.gz"
export NGX_LIBS="/usr/local/src/nginx-1.27.2/auto/lib"
export NGX_OPENSSL_DIR="$NGX_LIBS/openssl"
export NGX_OPENSSL_VERSION="1.1.1l"
export NGX_FASTCGI_PHP="$NGX_SNIPPETS/fastcgi-php.conf"

export NGX_PCRE_VERSION="2-10.44"
export NGX_PCRE_GIT_URI="https://github.com/PCRE2Project/pcre2.git"
export NGX_PCRE_DIR="/usr/local/src/pcre$NGX_PCRE_VERSION"
export NGX_PCRE_DL_URI="https://github.com/PCRE2Project/pcre2/releases/download/pcre$NGX_PCRE_VERSION/pcre$NGX_PCRE_VERSION.tar.gz"
