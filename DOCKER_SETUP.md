# PostgreSQL Docker Setup - Quick Reference

## Initial Setup and Startup

```bash
# Start PostgreSQL and pgAdmin (first time will auto-run init-db scripts)
docker-compose up -d

# Check if services are running
docker-compose ps

# View PostgreSQL logs to confirm initialization
docker-compose logs postgres

# View pgAdmin logs
docker-compose logs pgadmin
```

## Database Access

### PostgreSQL Connection Details
- **Host**: localhost
- **Port**: 5432
- **Database**: design_patterns
- **User**: pdp_user
- **Password**: pdp_password

### Connection Strings for Python

```python
# psycopg2
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="design_patterns",
    user="pdp_user",
    password="pdp_password"
)

# asyncpg
import asyncpg
conn = await asyncpg.connect(
    "postgresql://pdp_user:pdp_password@localhost:5432/design_patterns"
)
```

### pgAdmin Access
- **URL**: http://localhost:5050
- **Email**: admin@example.com
- **Password**: admin

**Adding PostgreSQL server in pgAdmin:**
1. Right-click "Servers" → "Register" → "Server"
2. General tab: Name = "Local PostgreSQL"
3. Connection tab:
   - Host: postgres (use the service name, not localhost)
   - Port: 5432
   - Database: design_patterns
   - Username: pdp_user
   - Password: pdp_password

## Verification Commands

```bash
# List all tables in the database
docker-compose exec postgres psql -U pdp_user -d design_patterns -c "\dt"

# View sample users data
docker-compose exec postgres psql -U pdp_user -d design_patterns -c "SELECT * FROM users;"

# View sample products data
docker-compose exec postgres psql -U pdp_user -d design_patterns -c "SELECT * FROM products;"

# Connect to PostgreSQL shell interactively
docker-compose exec postgres psql -U pdp_user -d design_patterns

# Inside psql shell, useful commands:
# \dt          - list all tables
# \d users     - describe users table
# \l           - list all databases
# \q           - quit
```

## Common Operations

```bash
# Stop services (data persists in volumes)
docker-compose down

# Start services again
docker-compose up -d

# Restart just PostgreSQL
docker-compose restart postgres

# View real-time logs
docker-compose logs -f postgres

# Stop and remove ALL data (fresh start)
docker-compose down -v

# After removing volumes, start fresh (re-runs init scripts)
docker-compose up -d
```

## Re-initializing Database

If you need to reset the database completely:

```bash
# Stop and remove volumes
docker-compose down -v

# Start fresh (this will re-run init-db/01-init-schema.sql)
docker-compose up -d

# Verify initialization
docker-compose logs postgres | grep "init-schema"
```

## Database Schema

The initialization script creates:

### Tables
- **users** - User accounts (id, username, email, full_name)
- **products** - Product catalog (id, name, description, price, stock_quantity)
- **orders** - Customer orders (id, user_id, total_amount, status)
- **order_items** - Order line items (id, order_id, product_id, quantity, price)
- **audit_log** - Audit trail (id, table_name, record_id, action, old_data, new_data)

### Sample Data
- 3 users (john_doe, jane_smith, bob_wilson)
- 4 products (Laptop, Mouse, Keyboard, Monitor)

## Troubleshooting

```bash
# Check if port 5432 is already in use
lsof -i :5432

# Check if port 5050 is already in use
lsof -i :5050

# Remove everything and start fresh
docker-compose down -v
docker-compose up -d

# Check container status
docker-compose ps

# View detailed logs
docker-compose logs postgres
docker-compose logs pgadmin

# Execute SQL file manually (if needed)
docker-compose exec -T postgres psql -U pdp_user -d design_patterns < init-db/01-init-schema.sql
```

## Environment Variables

Edit `.env` file to customize:
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB
- POSTGRES_PORT
- PGADMIN_EMAIL
- PGADMIN_PASSWORD
- PGADMIN_PORT

After changing `.env`, restart services:
```bash
docker-compose down
docker-compose up -d
```
