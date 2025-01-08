#!/bin/bash

# Import utility functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils/common.sh"
source "$SCRIPT_DIR/utils/logger.sh"

# Default values
DB_NAME=${DB_NAME:-"dashboard"}
DB_USER=${DB_USER:-"postgres"}
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-5432}
MIGRATIONS_DIR="migrations"

# Function to check database connection
check_db_connection() {
    log_info "Checking database connection..."
    if ! command_exists psql; then
        log_error "PostgreSQL client (psql) not found"
        return 1
    fi
    
    if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" > /dev/null 2>&1; then
        log_error "PostgreSQL server is not running"
        return 1
    fi
    
    if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' > /dev/null 2>&1; then
        log_error "Could not connect to database"
        return 1
    fi
    
    log_success "Database connection successful"
    return 0
}

# Function to create database
create_database() {
    log_info "Creating database..."
    
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        log_warning "Database $DB_NAME already exists"
        return 0
    fi
    
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" > /dev/null 2>&1; then
        log_success "Database created successfully"
        return 0
    else
        log_error "Failed to create database"
        return 1
    fi
}

# Function to create migrations directory
create_migrations_dir() {
    log_info "Setting up migrations directory..."
    
    ensure_directory "$MIGRATIONS_DIR"
    ensure_directory "$MIGRATIONS_DIR/versions"
    
    # Create __init__.py files
    touch "$MIGRATIONS_DIR/__init__.py"
    touch "$MIGRATIONS_DIR/versions/__init__.py"
    
    log_success "Migrations directory created"
}

# Function to create new migration
create_migration() {
    local description=$1
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local filename="${timestamp}_${description// /_}.py"
    local filepath="$MIGRATIONS_DIR/versions/$filename"
    
    log_info "Creating new migration: $description"
    
    cat > "$filepath" << EOL
"""${description}

Revision ID: ${timestamp}
Create Date: $(date -u +"%Y-%m-%d %H:%M:%S.%3N")
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Implement your upgrade steps here
    pass

def downgrade():
    # Implement your downgrade steps here
    pass
EOL
    
    log_success "Created migration file: $filepath"
}

# Function to apply migrations
apply_migrations() {
    local direction=${1:-"upgrade"}
    local version=${2:-"head"}
    
    log_info "Applying migrations ($direction to $version)..."
    
    if [ "$direction" = "upgrade" ]; then
        alembic upgrade "$version"
    else
        alembic downgrade "$version"
    fi
    
    log_success "Migrations applied successfully"
}

# Function to show migration history
show_history() {
    log_info "Migration History:"
    alembic history --verbose
}

# Function to show current version
show_current() {
    log_info "Current Database Version:"
    alembic current
}

# Function to verify database schema
verify_schema() {
    log_info "Verifying database schema..."
    
    # Check if all tables exist
    local required_tables=("users" "metrics" "alerts" "configurations")
    local missing_tables=()
    
    for table in "${required_tables[@]}"; do
        if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\dt $table" > /dev/null 2>&1; then
            missing_tables+=("$table")
        fi
    done
    
    if [ ${#missing_tables[@]} -eq 0 ]; then
        log_success "All required tables exist"
    else
        log_error "Missing tables: ${missing_tables[*]}"
        return 1
    fi
}

# Function to backup database
backup_database() {
    local backup_dir="backups"
    local backup_file="$backup_dir/${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql"
    
    ensure_directory "$backup_dir"
    
    log_info "Backing up database to $backup_file..."
    
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -F p > "$backup_file"; then
        log_success "Database backup created successfully"
        return 0
    else
        log_error "Failed to create database backup"
        return 1
    fi
}

# Function to restore database
restore_database() {
    local backup_file=$1
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    log_info "Restoring database from $backup_file..."
    
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" < "$backup_file"; then
        log_success "Database restored successfully"
        return 0
    else
        log_error "Failed to restore database"
        return 1
    fi
}

# Function to show help message
show_help() {
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo
    echo "Commands:"
    echo "  init              Initialize database and migrations"
    echo "  create NAME       Create new migration"
    echo "  upgrade [REV]     Upgrade database to revision (default: head)"
    echo "  downgrade [REV]   Downgrade database to revision"
    echo "  history          Show migration history"
    echo "  current          Show current database version"
    echo "  verify           Verify database schema"
    echo "  backup           Backup database"
    echo "  restore FILE     Restore database from backup"
    echo
    echo "Options:"
    echo "  --help           Show this help message"
}

# Main function
main() {
    # Parse arguments
    case "$1" in
        init)
            check_db_connection && \
            create_database && \
            create_migrations_dir
            ;;
        create)
            if [ -z "$2" ]; then
                log_error "Migration name required"
                show_help
                exit 1
            fi
            create_migration "$2"
            ;;
        upgrade)
            apply_migrations "upgrade" "${2:-head}"
            ;;
        downgrade)
            apply_migrations "downgrade" "${2:-head}"
            ;;
        history)
            show_history
            ;;
        current)
            show_current
            ;;
        verify)
            verify_schema
            ;;
        backup)
            backup_database
            ;;
        restore)
            if [ -z "$2" ]; then
                log_error "Backup file required"
                show_help
                exit 1
            fi
            restore_database "$2"
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
