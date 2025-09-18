# HEMIS Database SQL Files

This directory contains the SQL files for setting up the HEMIS (Hospital Electronic Medical Information System) database.

## 📁 File Structure

### 1. `hemis_db.sql` - Database Schema

- **Purpose**: Contains the complete database structure
- **Contents**:
  - Table definitions
  - Indexes and constraints
  - Foreign key relationships
  - No user management or data
- **Usage**: Run first to create the database structure

### 2. `users.sql` - User Management & Permissions

- **Purpose**: Creates database users and assigns permissions
- **Contents**:
  - 9 different user roles with specific permissions
  - Role-based access control (RBAC)
  - Granular table-level permissions
- **Usage**: Run after `hemis_db.sql` to set up users

### 3. `seed.sql` - Initial Data

- **Purpose**: Populates the database with reference data
- **Contents**:
  - Core catalogs (identification types, appointment statuses, etc.)
  - Sample users with hashed passwords
  - Role assignments
- **Usage**: Run after `users.sql` to populate initial data

### 4. `views.sql` - Database Views

- **Purpose**: Provides simplified access to complex data relationships
- **Contents**:
  - 25 views organized by functional areas
  - Patient management, appointments, medical records, etc.
  - Role-based access considerations
- **Usage**: Run after `seed.sql` to create reporting views

## 🚀 Installation Order

```bash
# 1. Create database structure
mysql -u root -p < hemis_db.sql

# 2. Set up users and permissions
mysql -u root -p < users.sql

# 3. Populate with initial data
mysql -u root -p < seed.sql

# 4. Create reporting views
mysql -u root -p < views.sql
```

## 👥 User Roles & Permissions

| Role            | Description                | Primary Access                              |
| --------------- | -------------------------- | ------------------------------------------- |
| `super_admin`   | Full system access         | All tables (SELECT, INSERT, UPDATE, DELETE) |
| `admin_hr`      | Human resources management | User/doctor management, patient data        |
| `admin_medical` | Medical operations         | Medical records, appointments, specialties  |
| `admin_finance` | Financial operations       | Billing, payments, insurance                |
| `admin_system`  | Technical infrastructure   | Devices, monitoring, system configuration   |
| `doctor`        | Medical staff              | Patient care, medical records, appointments |
| `nurse`         | Nursing staff              | Patient care, medical support               |
| `reception`     | Front desk                 | Patient management, scheduling              |
| `coordinator`   | Medical coordination       | Scheduling, room management, coordination   |

## 🔐 Security Features

- **Role-Based Access Control**: Each user has minimal required permissions
- **Principle of Least Privilege**: Users can only access what they need
- **Granular Permissions**: Table-level access control with specific operations
- **Password Security**: Default passwords for development (change in production)

## 📊 Database Views

The views provide simplified access to:

- **Patient Management**: Directory, summaries, medical info, financial status
- **Appointments**: Calendar, schedules, triage queue, room allocation
- **Medical Records**: Vital signs, prescriptions, diagnoses
- **Monitoring**: Device status, incidents, alerts
- **Administration**: Staff directory, billing, user roles
- **Reporting**: Operations dashboard, daily reports, financial summaries

## 🛠️ Maintenance

### Adding New Tables

1. Add table definition to `hemis_db.sql`
2. Update relevant user permissions in `users.sql`
3. Consider adding views in `views.sql` if needed

### Adding New Users

1. Add user creation in `users.sql`
2. Assign appropriate role permissions
3. Follow the principle of least privilege

### Updating Permissions

1. Modify the relevant GRANT statements in `users.sql`
2. Test with the specific user role
3. Document changes for audit purposes

## ⚠️ Production Considerations

- **Change Default Passwords**: All users have default passwords
- **Password Policies**: Implement strong password requirements
- **Audit Logging**: Consider enabling MySQL audit logs
- **Regular Reviews**: Periodically review user permissions
- **Backup Strategy**: Include user permissions in backup procedures

## 🔍 Troubleshooting

### Common Issues

1. **Permission Denied**: Check if user has required table access
2. **Foreign Key Errors**: Ensure tables are created in correct order
3. **User Connection Issues**: Verify user exists and has proper permissions

### Debugging Permissions

```sql
-- Check user permissions
SHOW GRANTS FOR 'username'@'host';

-- Check current user
SELECT USER(), CURRENT_USER();

-- Check database access
SHOW DATABASES;
```

## 📚 Additional Resources

- [MySQL User Management](https://dev.mysql.com/doc/refman/8.0/en/user-management.html)
- [MySQL Privileges](https://dev.mysql.com/doc/refman/8.0/en/privileges-provided.html)
- [Database Security Best Practices](https://owasp.org/www-project-top-ten/2017/A6_2017-Security_Misconfiguration)
