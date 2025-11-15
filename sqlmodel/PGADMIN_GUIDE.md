# pgAdmin Access Guide

Complete guide to accessing and using pgAdmin with your PostgreSQL database.

## Quick Start

1. **Access pgAdmin**: http://localhost:5050
2. **Default Credentials**:
   - Email: `admin@example.com`
   - Password: `admin`

## Table of Contents

- [Accessing pgAdmin](#accessing-pgadmin)
- [Adding PostgreSQL Server](#adding-postgresql-server)
- [Navigating the Database](#navigating-the-database)
- [Common Operations](#common-operations)
- [Troubleshooting](#troubleshooting)

---

## Accessing pgAdmin

### Step 1: Start Docker Containers

```bash
# Start PostgreSQL and pgAdmin
docker-compose up -d

# Verify containers are running
docker ps
```

You should see:
- `pdp-postgres` (PostgreSQL database)
- `pdp-pgadmin` (pgAdmin web interface)

### Step 2: Open pgAdmin in Browser

1. Navigate to: **http://localhost:5050**
2. Login with credentials:
   - **Email**: `admin@example.com` (or check `.env` for `PGADMIN_EMAIL`)
   - **Password**: `admin` (or check `.env` for `PGADMIN_PASSWORD`)

---

## Adding PostgreSQL Server

### Method 1: First-Time Setup (Recommended)

After logging in for the first time:

#### Step 1: Add New Server

1. In pgAdmin, right-click **"Servers"** in the left sidebar
2. Select **"Register" → "Server..."**

#### Step 2: General Tab

Fill in the **General** tab:

```
Name: Local PostgreSQL (or any name you prefer)
```

#### Step 3: Connection Tab

Fill in the **Connection** tab:

| Field | Value | Notes |
|-------|-------|-------|
| **Host name/address** | `postgres` | ⚠️ Use `postgres` (Docker service name) NOT `localhost` |
| **Port** | `5432` | Default PostgreSQL port |
| **Maintenance database** | `postgres` | Default database |
| **Username** | `pdp_user` | From `.env` or docker-compose.yml |
| **Password** | `pdp_password` | From `.env` or docker-compose.yml |
| **Save password?** | ✓ (checked) | Optional, for convenience |

**Important**: Use `postgres` as hostname because pgAdmin runs inside Docker and connects to the PostgreSQL container via the Docker network.

#### Step 4: Save

Click **"Save"** button at the bottom right.

You should now see your server connected in the left sidebar!

---

### Method 2: If "postgres" Hostname Doesn't Work

If you get a connection error with `postgres` as hostname:

1. Try hostname: `host.docker.internal` (Mac/Windows)
2. Or try hostname: `172.17.0.1` (Linux Docker bridge IP)
3. Or use `localhost` with port mapping (if configured in docker-compose.yml)

---

## Navigating the Database

After connecting, navigate through this hierarchy:

```
Servers
└── Local PostgreSQL (your server name)
    └── Databases
        └── design_patterns (your database)
            └── Schemas
                └── public (default schema)
                    ├── Tables
                    │   ├── test_users
                    │   ├── test_users_async
                    │   └── user
                    ├── Views
                    ├── Functions
                    └── Sequences
```

### Viewing Table Data

1. Expand: **Servers → Local PostgreSQL → Databases → design_patterns → Schemas → public → Tables**
2. **Right-click** on a table (e.g., `test_users`)
3. Select **"View/Edit Data" → "All Rows"**

This opens a data grid showing all rows in the table.

### Alternative: Quick View

- **Right-click** table → **"View/Edit Data" → "First 100 Rows"**

---

## Common Operations

### 1. Running SQL Queries

#### Method A: Query Tool

1. Right-click on database name (`design_patterns`)
2. Select **"Query Tool"**
3. Type your SQL:
   ```sql
   SELECT * FROM test_users;
   ```
4. Click **▶ Execute** button (or press F5)

#### Method B: Quick Query

1. Right-click on any table
2. Select **"Scripts" → "SELECT Script"**
3. Executes: `SELECT * FROM table_name`

### 2. Viewing Table Structure

1. Expand: **Tables → test_users → Columns**
2. See all columns with data types

Or:

1. Right-click on table
2. Select **"Properties"**
3. View tabs: **General**, **Columns**, **Constraints**, **Indexes**, etc.

### 3. Creating a New Table

1. Right-click on **Tables**
2. Select **"Create" → "Table..."**
3. Fill in:
   - **General** tab: Table name
   - **Columns** tab: Add columns with data types
   - **Constraints** tab: Add primary keys, foreign keys, etc.
4. Click **"Save"**

### 4. Exporting Data

1. Right-click on table
2. Select **"Import/Export Data..."**
3. Choose format: CSV, JSON, etc.
4. Set file path and options
5. Click **"OK"**

### 5. Viewing Active Connections

1. Right-click on database (`design_patterns`)
2. Select **"Dashboard"**
3. See: Active sessions, transactions, locks

### 6. Refreshing View

If data doesn't appear after running scripts:

- Right-click on **Tables** → **"Refresh"** (or press F5)

---

## Environment Variables Reference

Your setup uses these values (from `docker-compose.yml` or `.env`):

```bash
# PostgreSQL
POSTGRES_USER=pdp_user
POSTGRES_PASSWORD=pdp_password
POSTGRES_DB=design_patterns
POSTGRES_PORT=5432

# pgAdmin
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin
PGADMIN_PORT=5050
```

---

## Troubleshooting

### Issue 1: Can't Connect to Server

**Error**: "Could not connect to server"

**Solutions**:
1. Verify Docker containers are running:
   ```bash
   docker ps
   ```
2. Check hostname:
   - Use `postgres` (Docker service name)
   - NOT `localhost` or `127.0.0.1`
3. Verify credentials match `.env` or `docker-compose.yml`
4. Check PostgreSQL health:
   ```bash
   docker exec -it pdp-postgres pg_isready -U pdp_user
   ```

### Issue 2: "Hostname 'postgres' Not Found"

**Solution**: Try alternative hostnames:
- `host.docker.internal` (Mac/Windows Docker Desktop)
- `172.17.0.1` (Linux default Docker bridge)
- Find container IP:
  ```bash
  docker inspect pdp-postgres | grep IPAddress
  ```

### Issue 3: Login Fails

**Error**: Invalid email or password

**Solution**:
1. Check `.env` file for correct `PGADMIN_EMAIL` and `PGADMIN_PASSWORD`
2. If changed, recreate pgAdmin container:
   ```bash
   docker-compose down
   docker volume rm python-design-patterns_pgadmin_data
   docker-compose up -d
   ```

### Issue 4: Can't See Tables

**Solutions**:
1. Make sure you ran the Python scripts to create tables:
   ```bash
   python sqlmodel/sync_pattern.py
   ```
2. Refresh the view: Right-click **Tables** → **Refresh**
3. Check you're looking in the correct schema: **public**

### Issue 5: Password Authentication Failed

**Error**: "password authentication failed for user"

**Solutions**:
1. Verify username/password in:
   - pgAdmin connection settings
   - Match `docker-compose.yml` or `.env`
2. Restart PostgreSQL container:
   ```bash
   docker restart pdp-postgres
   ```

---

## Useful pgAdmin Shortcuts

| Action | Shortcut |
|--------|----------|
| Execute Query | `F5` |
| Refresh | `F5` |
| Query Tool | `Alt + Shift + Q` |
| Save Query | `Ctrl + S` |
| New Tab | `Ctrl + T` |
| Close Tab | `Ctrl + W` |

---

## Advanced: Direct Database Access (Without pgAdmin)

If pgAdmin has issues, access PostgreSQL directly:

### Using psql (PostgreSQL CLI):

```bash
# Connect to database
docker exec -it pdp-postgres psql -U pdp_user -d design_patterns

# List tables
\dt

# Query table
SELECT * FROM test_users;

# Exit
\q
```

### Using Python Script:

See: `sqlmodel/check_table.py` (if created) or use patterns from `sync_pattern.py`

---

## Database Hierarchy Reference

```
┌─────────────────────────────────────────────────────┐
│ Server (PostgreSQL Instance)                        │
│   Host: postgres (or localhost)                     │
│   Port: 5432                                         │
│   User: pdp_user                                     │
├─────────────────────────────────────────────────────┤
│ └── Database: design_patterns                       │
│     ├── Schemas                                      │
│     │   └── public (default)                         │
│     │       ├── Tables                               │
│     │       │   ├── test_users                       │
│     │       │   ├── test_users_async                 │
│     │       │   └── user                             │
│     │       ├── Views                                │
│     │       ├── Functions                            │
│     │       └── Sequences                            │
│     └── Other schemas (if any)                       │
└─────────────────────────────────────────────────────┘
```

---

## Next Steps

After setting up pgAdmin:

1. ✅ Run `python sqlmodel/sync_pattern.py` to create tables
2. ✅ Verify data in pgAdmin: `test_users` table
3. ✅ Run `python sqlmodel/async_pattern.py` (after installing `greenlet`)
4. ✅ Verify data in pgAdmin: `test_users_async` table
5. ✅ Experiment with queries in pgAdmin Query Tool

---

## Additional Resources

- **pgAdmin Documentation**: https://www.pgadmin.org/docs/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│             pgAdmin Connection Settings             │
├─────────────────────────────────────────────────────┤
│ URL:          http://localhost:5050                 │
│ Email:        admin@example.com                     │
│ Password:     admin                                 │
├─────────────────────────────────────────────────────┤
│ Host:         postgres                              │
│ Port:         5432                                  │
│ Database:     design_patterns                       │
│ Username:     pdp_user                              │
│ Password:     pdp_password                          │
└─────────────────────────────────────────────────────┘
```

---

**Last Updated**: 2025-11-15
