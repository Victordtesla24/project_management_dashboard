#!/bin/bash

# Cross-platform timeout implementation
timeout() {
    if command -v gtimeout >/dev/null 2>&1; then
        gtimeout "$@"
    else
        perl -e '
            use strict;
            use warnings;
            my $timeout = shift;
            my $command = join(" ", @ARGV);
            eval {
                local $SIG{ALRM} = sub { die "timeout\n" };
                alarm($timeout =~ s/s$//r);
                system($command);
                alarm(0);
            };
            if ($@ eq "timeout\n") {
                exit 124;
            }
        ' "$1" "${@:2}"
    fi
}

# Utility function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Utility function to handle errors
error_exit() {
    printf "\r\033[K❌ Error: %s\n" "$1" >&2
    exit "${2:-1}"
}

# Utility function to print warnings
print_warning() {
    printf "\r\033[K⚠️  Warning: %s\n" "$1" >&2
}

# Utility function to print success messages
print_success() {
    printf "\r\033[K✓ %s\n" "$1"
}

# Utility function to check dependencies
check_dependency() {
    local cmd="$1"
    local pkg="${2:-$1}"
    if ! command_exists "$cmd"; then
        if command_exists brew; then
            print_warning "$cmd not found, attempting to install via Homebrew..."
            brew install "$pkg" >/dev/null 2>&1 || error_exit "Failed to install $pkg"
        else
            error_exit "$cmd is required but not found"
        fi
    fi
}

# Export functions
export -f timeout
export -f command_exists
export -f error_exit
export -f print_warning
export -f print_success
export -f check_dependency
