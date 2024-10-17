#!/bin/bash
## Collection of bash utility functions for managing services

# Check if systemd is available, then stop and disable a service
kill_service() {
    if cmd_exists systemctl; then
        
        v_echo "Stopping $1"
        try_sudo systemctl stop $1

        v_echo "Disabling $1"
        try_sudo systemctl disable $1
    else
        error "Systemd not found. Manual stopping of $1 required."
    fi
}

# Check if a service is enabled and running, then disable and stop it if so
disable_service() {
    package_path="/usr/sbin/$1"

    if cmd_exists systemctl; then
        if systemctl is-active --quiet $1; then
            kill_service $1
        elif file_exists "/etc/systemd/system/$1.service"; then
            kill_service $1
        elif [ -x "$package_path" ]; then
            kill_service $1
        else
            error "$1 service file not found. Manual disabling required."
        fi
    else
        error "Systemd not found. Manual disabling of $1 required."
    fi
}

# Reload systemd
daemon_reload() {
    if cmd_exists systemctl; then
        v_echo "Reloading systemd"
        try_sudo systemctl daemon-reload
    else
        error "Systemd not found. Manual reloading of systemd required."
    fi
}