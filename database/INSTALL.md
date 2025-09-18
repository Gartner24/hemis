# HEMIS Database Installation Guide

This guide helps you install MySQL on your VPS and set up the HEMIS database.

## Prerequisites

- VPS with Ubuntu/Debian, CentOS/RHEL, or similar Linux distribution
- Root or sudo access
- Internet connection

## Step 1: Install MySQL 8.0

### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install MySQL Server
sudo apt install mysql-server-8.0

# Start and enable MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Secure MySQL installation
sudo mysql_secure_installation
```

### CentOS/RHEL
```bash
# Install MySQL Server
sudo yum install mysql-server

# Start and enable MySQL
sudo systemctl start mysqld
sudo systemctl enable mysqld

# Get temporary root password
sudo grep 'temporary password' /var/log/mysqld.log

# Secure MySQL installation
sudo mysql_secure_installation
```

## Step 2: Configure MySQL

### Create MySQL Root User (if needed)
```bash
# Connect to MySQL
sudo mysql

# Create root user with password
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'YourSecurePassword';
FLUSH PRIVILEGES;
EXIT;
```

### Create MySQL Admin User (Recommended)
```bash
# Connect to MySQL as root
mysql -u root -p

# Create admin user with full privileges
CREATE USER 'mysql_admin'@'localhost' IDENTIFIED BY 'YourAdminPassword';
GRANT ALL PRIVILEGES ON *.* TO 'mysql_admin'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;

# Test the new user
EXIT;
mysql -u mysql_admin -p

# If successful, you can now use mysql_admin instead of root
EXIT;
```

### Configure MySQL for HEMIS
```bash
# Edit MySQL configuration
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Add these settings:
[mysqld]
character-set-server = utf8mb4
collation-server = utf8mb4_0900_ai_ci
max_connections = 200
innodb_buffer_pool_size = 256M
```

### Restart MySQL
```bash
sudo systemctl restart mysql
```

## Step 3: Set Up HEMIS Database

### Copy Database Files to VPS
```bash
# Copy database directory
scp -r database/ user@your-vps:/path/to/hemis/
```

### Run Database Setup
```bash
# On your VPS
cd /path/to/hemis/database
chmod +x setup.sh
./setup.sh
```

The script will:
1. Check if MySQL is installed and running
2. Ask for MySQL root password
3. Run the SQL files in correct order:
   - `hemis_db.sql` - Creates database and tables
   - `users.sql` - Creates users and permissions
   - `seed.sql` - Populates with initial data

## Step 4: Configure Environment Variables

Create a `database/.env` file with MySQL configuration:

### Option 1: Use Template (Recommended)
```bash
# Copy the template
cp env.template .env

# Edit with your actual credentials
nano .env
```

### Option 2: Create Manually
```bash
# Create database/.env file
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
```

**Note**: The database setup script will automatically use these credentials if they exist in the `database/.env` file.

## Step 5: Test Database Connection

```bash
# Test connection
mysql -u root -p hemis_db

# Test with application user
mysql -u santi -p hemis_db

# List all users
mysql -u root -p -e "SELECT User, Host FROM mysql.user WHERE User LIKE '%admin%' OR User LIKE '%doctor%' OR User LIKE '%nurse%';"
```

## Database Management

### Backup Database
```bash
# Full backup
mysqldump -u root -p hemis_db > hemis_backup_$(date +%Y%m%d).sql

# Backup with compression
mysqldump -u root -p hemis_db | gzip > hemis_backup_$(date +%Y%m%d).sql.gz
```

### Restore Database
```bash
# From SQL file
mysql -u root -p hemis_db < hemis_backup_20240101.sql

# From compressed file
gunzip < hemis_backup_20240101.sql.gz | mysql -u root -p hemis_db
```

### Monitor Database
```bash
# Check MySQL status
sudo systemctl status mysql

# View MySQL logs
sudo tail -f /var/log/mysql/error.log

# Check database size
mysql -u mysql_admin -p -e "SELECT table_schema AS 'Database', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' FROM information_schema.tables WHERE table_schema = 'hemis_db' GROUP BY table_schema;"
```

## Security Considerations

1. **Use Admin User**: Use `mysql_admin` instead of `root` for database operations
2. **Change Default Passwords**: Update all default passwords in production
3. **Firewall**: Only allow database access from your application servers
4. **SSL**: Enable SSL for database connections in production
5. **Regular Backups**: Set up automated daily backups
6. **Monitor Access**: Log and monitor database access
7. **Principle of Least Privilege**: Only grant necessary permissions to users

## Troubleshooting

### MySQL Won't Start
```bash
# Check error logs
sudo tail -f /var/log/mysql/error.log

# Check configuration
sudo mysql --help --verbose | grep -A 1 'Default options'
```

### Permission Denied
```bash
# Check MySQL user permissions
mysql -u root -p -e "SHOW GRANTS FOR 'santi'@'localhost';"

# Reset user password
mysql -u root -p -e "ALTER USER 'santi'@'localhost' IDENTIFIED BY 'NewPassword';"
```

### Connection Refused
```bash
# Check if MySQL is listening
sudo netstat -tlnp | grep 3306

# Check MySQL configuration
sudo mysql -u root -p -e "SHOW VARIABLES LIKE 'bind_address';"
```

## Next Steps

After database setup is complete:
1. Start your backend application
2. Test the connection from your application
3. Verify all user roles work correctly
4. Set up monitoring and backups
