# NQ Supermarket ERP

Production-oriented supermarket management platform covering POS, inventory, purchasing, sales, customers, delivery, reporting and administration.

## Phase 1 — Foundation

Current branch: `feature/phase-1-foundation`

Implemented:

- Flask application factory
- PostgreSQL-ready SQLAlchemy setup
- Flask-Migrate integration
- Secure session authentication
- Password hashing
- Global CSRF protection
- Users, roles and permissions
- Branches and warehouses
- System settings model
- Audit log model
- Arabic RTL starter UI
- Initial database seed command
- Authentication tests

## Local setup

1. Create PostgreSQL database:

```sql
CREATE DATABASE supermarket_erp;
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and update database credentials and `SECRET_KEY`.

4. Initialize migrations:

```bash
flask --app manage.py db init
flask --app manage.py db migrate -m "initial schema"
flask --app manage.py db upgrade
```

5. Seed initial data:

```bash
flask --app manage.py seed
```

6. Run:

```bash
python manage.py
```

Initial development account created by the seed command:

- Username: `admin`
- Password: `ChangeMe123!`

**Change this password immediately outside development.**

## Roadmap

1. Foundation & security
2. Products & inventory
3. POS & cashier shifts
4. Purchasing & suppliers
5. Customers, loyalty & promotions
6. Online orders & delivery
7. Reports, backups, performance and production deployment
