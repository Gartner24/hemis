#!/bin/bash

# HEMIS Database Setup Script for Host MySQL
# This script sets up the MySQL database for HEMIS on the host system

set -e

echo "HEMIS Database Setup"
echo "===================="

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "Error: MySQL is not installed"
    exit 1
fi

# Check if MySQL is running
if ! systemctl is-active --quiet mysql && ! pgrep mysqld > /dev/null; then
    echo "Error: MySQL is not running"
    exit 1
fi

# Check if database .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: database/.env file not found"
    echo "Creating database/.env file with default values..."
    cat > .env << EOF
# MySQL Admin Configuration
MYSQL_ROOT_PASSWORD=YourSecureRootPassword
MYSQL_ADMIN_USER=mysql_admin
MYSQL_ADMIN_PASSWORD=YourAdminPassword

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=hemis_db
DB_USER=santi
DB_PASSWORD=Eldestructor66*
EOF
fi

# Load environment variables from database/.env
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "Setting up database..."

# Get MySQL admin credentials
if [ -n "$MYSQL_ADMIN_USER" ] && [ -n "$MYSQL_ADMIN_PASSWORD" ]; then
    MYSQL_USER="$MYSQL_ADMIN_USER"
    MYSQL_PASSWORD="$MYSQL_ADMIN_PASSWORD"
else
    echo "Enter MySQL admin credentials:"
    read -p "Username [mysql_admin]: " MYSQL_USER
    MYSQL_USER=${MYSQL_USER:-mysql_admin}
    
    read -s -p "Password: " MYSQL_PASSWORD
    echo ""
fi

# Test MySQL connection
echo "Testing connection..."
if ! mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1;" > /dev/null 2>&1; then
    echo "Error: Cannot connect to MySQL"
    exit 1
fi

echo "Connection successful"

# Run SQL files in order
echo "Creating schema..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" < sql/hemis_db.sql

echo "Setting up users..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" < sql/users.sql

echo "Loading initial data..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" < sql/seed.sql

echo ""
echo "Database Setup Complete!"
echo ""