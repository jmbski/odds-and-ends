# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples
#echo 'set completion-ignore-case On' >> ~/.inputrc

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# If set, the pattern "**" used in a pathname expansion context will
# match all files and zero or more directories and subdirectories.
#shopt -s globstar

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color|*-256color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
#force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf.)
	color_prompt=yes
    else
	color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    ;;
*)
    ;;
esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# colored GCC warnings and errors
#export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
#export LS_COLORS=$(dircolors -b)

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

######
# Execute environment variables
#source /etc/environment

# Unset all aliases to start fresh
unalias -a

# Simple Aliases
alias py='python3'

# Navigation Aliases
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias cdconpy='cd $CODING_BASE\\silverlight\\conlang/python'
alias wldbldr='cd $CODING_BASE\\silverlight\\world_builder_ai\\python'
alias cdcwindow='cd $CLEAR_WINDOW'
alias cdcwbase='cd $CW_BASE'
alias cddbx='cd $CLEAR_WINDOW/dropbox_cli/dropbox_cli'
alias cdgolang='cd $CLEAR_WINDOW/golang/clear_window/analysis'
alias cdcwgo='cd $CWGO'
alias cdgo='cd $GO_BASE'

# Connection Aliases
alias oldssh="ssh root@31.220.63.217"
alias newssh='ssh root@86.38.218.146'
alias oldsftp='sftp griffon@31.220.63.217'
alias newsftp='sftp warskald_admin@86.38.218.146'
#alias wasssh='ssh root@$WASABI_BALL'
#alias wasftp='sftp root@$WASABI_BALL'
alias wasssh='ssh root@$WASABI_BALL_2'
alias wasftp='sftp root@$WASABI_BALL_2'
alias bnssh='ssh $BITNAMI'
alias bnsftp='sftp $BITNAMI'
#alias artssh='ssh jmbski@$ARTWB'
#alias artftp='sftp jmbski@$ARTWB'

# Administrative
alias vbash="vim ~/.bashrc"
alias vprof="vim ~/.profile"
alias sbash="source ~/.profile"
alias listcmds='cat ~/.bashrc | grep -e "alias"'
alias listvars='cat ~/.bashrc | grep -e "export"'
alias rcgrep='cat ~/.bashrc | egrep -in'
alias prgrep='cat ~/.profile | egrep -in'
alias engrep='cat /etc/environment | egrep -in'
alias valias=' vim ~/.bash_aliases'
alias venvars='sudo vim /etc/environment'
alias senvars='source /etc/environment'
alias phpup='sudo rsync -a --progress $CODING_BASE/php_clearwindow/ /var/www/html/ && sudo chown -R www-data:www-data /var/www/html/ && sudo systemctl restart apache2'
alias siteup='rsync -a --progress --partial -e ssh $CODING_BASE/clear-window/demo-ui/ $BITNAMI:/home/bitnami/wp_code'
alias dbup='rsync -a --progress --partial -e ssh $CODING_BASE/_sqlite_dbs/clear_window.db $BITNAMI:/home/bitnami/clear_window.db'
alias pyservup='rsync -a --progress --partial -e ssh $CODING_BASE/clear-window/demo_server/ $BITNAMI:/home/bitnami/web_server'
#alias pyservup='rsync -a --progress --partial -e ssh $CODING_BASE/test_server/ $BITNAMI:/home/bitnami/web_server'

alias dbxwas='rsync -a --progress --partial -e ssh $CODING_BASE/clear-window/dropbox_cli/ root@$WASABI_BALL_2:/Volume1/home/dropbox_cli/'

alias syctl='sudo systemctl'
alias systt='sudo systemctl status'
alias systart='sudo systemctl start'
alias syrestart='sudo systemctl restart'
alias systop='sudo systemctl stop'
alias sydmnrld='sudo systemctl daemon-reload'
alias kstart='sudo $KIBANA_HOME/bin/kibana --allow-root'
alias cwup='rsync -a --progress --partial --exclude="*.json" --exclude="*.csv" --exclude="*.feather" -e ssh $CODING_BASE/clear-window/cw_base/ $BITNAMI:/home/bitnami/cw_base/'
alias artup='upload $CODING_BASE/artificers_workbench/ /home/jmbski/app -e **/node_modules -e **/dist'
alias artbash='upload $CODING_BASE/bashconfigs/ /home/jmbski/bashconfigs/ jmbski $ARTWB -l'

# Tool Aliases
alias drawdeps='madge -i deps.svg ./* && convert deps.svg deps.png'
alias lintall='npx eslint --fix . --ext .ts'
alias lint='npx eslint --fix'
alias runai='ollama run llama3'
alias s3put='aws s3api put-object --bucket wasabi-s3 --profile minio-wasabi --endpoint-url http://192.168.1.60:443'
alias glbpy='source $GLB_PY_ENV/bin/activate'
alias wspubrv='python3 $utils/wspub.py --message '
#alias localjmble='pip remove jmble && pip install' 

alias wslatest='npm i warskald-ui@latest'
alias ngserve='python3 $utils/ng_serve.py'
alias ngstart='python3 $utils/ng_serve.py'
alias status='sudo systemctl status'
alias srestart='sudo systemctl restart'
alias rsapach='sudo systemctl restart apache2'

alias s3cli='poetry run python3 /home/joseph/coding_base/clear-window/cw_base/src/main.py --aws'

# Environment Aliases
alias nvm18='nvm use lts/hydrogen'
alias nvm16='nvm use 16'

# Python management
alias pinst='pip install --upgrade'
alias punst='pip uninstall'
alias pywslatest='pip install --upgrade warskald'
alias prun='poetry run python'
alias spoetry='sudo /home/joseph/.local/bin/poetry'
alias sprun='sudo /home/joseph/.local/bin/poetry run python'

# Build Aliases
alias pyuplod='twine upload --repository'
alias chrdb='chroma run --path $CODING_BASE\\chroma\\'
alias cwbuild='poetry build && pip install --force-reinstall $CLEAR_WINDOW/common-python/ici-common/dist/ici_common-0.1.0-py3-none-any.whl'
alias uptcvcomp='glbpy && pip uninstall -y cv-compare && pip install $CODING_BASE/clear-window/cv-compare/dist/cv_compare-0.1.0-py3-none-any.whl'
alias pbuild='glbpy && vmgr -p && deactivate && poetry build'
alias ppublish='pbuild && poetry publish'
alias jmblup='poetry remove jmble && poetry add jmble'
alias locjmbl='bash $utils/jmble_loc_install.sh && glbpy'
alias bldcwgo='bash $UTILS/install_cwgo.sh && source /tmp/cw_completion'
alias srccw='source /tmp/cw_completion'

# Build Functions

function gpush() {
    cmt_msg="$*"
    glbpy
    git_push $cmt_msg
    deactivate
}

# General
alias cwtest='prun $CODING_BASE/clear-window/cw_base/src/main.py -A -a'

# Linux only
alias getserial='udevadm info --query=property --property=ID_SERIAL_SHORT --value'
alias getserial1='getserial --name=/dev/sda1'
alias getserial2='getserial --name=/dev/sda2'
alias mounta1e1='sudo mount /dev/sda1 /media/joseph/external1/'
alias mounta2e1='sudo mount /dev/sda2 /media/joseph/external1/' 

# Created by `pipx` on 2024-08-16 15:59:03
#export PATH="$PATH:/home/joseph/.local/bin"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Check for bash_utils.sh location. First check $BASH_UTILS_PATH, then ~/.bash_utils, then 
# ~/.bash_utils.sh, then finally check in the local directory. If found, source the file. 
# If not found, emit an error message
BUTILS_SOURCED=false
if [ -f "$BASH_UTILS_PATH" ]; then
    echo "sourcing \$BASH_UTILS_PATH: $BASH_UTILS_PATH"
    source "$BASH_UTILS_PATH"
    BUTILS_SOURCED=true
elif [ -f "$HOME/.bash_utils" ]; then
    echo "Sourcing $HOME/.bash_utils"
    source "$HOME/.bash_utils"
    BUTILS_SOURCED=true
elif [ -f "$HOME/.bash_utils.sh" ]; then
    echo "Sourcing $HOME/.bash_utils.sh"
    source "$HOME/.bash_utils.sh"
    BUTILS_SOURCED=true
elif [ -f "bash_utils.sh" ]; then
    echo "Sourcing $(pwd)/bash_utils.sh"
    source "bash_utils.sh"
    BUTILS_SOURCED=true
else
    echo "Error: bash_utils.sh not found."
fi



# Load Angular CLI autocompletion.
if cmd_exists ng; then
    source <(ng completion script)
fi


if [ "$UPDATE_NGX" == true ]; then
    if dir_exists $NGX_BIN_DIR; then
        add_to_path $NGX_BIN_DIR
    fi
    update_ngx_configs
fi

 