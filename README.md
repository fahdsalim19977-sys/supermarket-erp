# NQ Supermarket ERP

Production-oriented supermarket management platform covering POS, inventory, purchasing, sales, customers, delivery, reporting and administration.

## Phase 1 + Phase 2 — Foundation, Products & Inventory

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
- System settings and audit log models
- Arabic RTL starter UI
- Categories, brands and units
- Products with SKU and barcode support
- Batch and expiry metadata
- Warehouse stock balances
- Immutable inventory movement records
- Transactional stock adjustment service with row locking
- Barcode lookup API for the future POS
- Product creation and inventory adjustment UI
- Inventory business-rule tests
- Initial database seed command

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

4. Initialize migrations only on a brand-new checkout:

```bash
flask --app manage.py db init
flask --app manage.py db migrate -m "initial schema"
flask --app manage.py db upgrade
```

If migrations are already initialized, create a new migration after model changes:

```bash
flask --app manage.py db migrate -m "products and inventory"
flask --app manage.py db upgrade
```

5. Seed initial data:

```bash
flask --app manage.py seed
```

6. Run tests:

```bash
pytest -q
```

7. Run:

```bash
python manage.py
```

Initial development account created by the seed command:

- Username: `admin`
- Password: `ChangeMe123!`

**Change this password immediately outside development.**

## Phase 2 API

After login, barcode lookup is available at:

`GET /products/lookup?barcode=<BARCODE>`

Example response:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "sku": "SKU-001",
    "name_ar": "منتج",
    "selling_price": "10.000",
    "unit": "PCS"
  }
}
```

## Roadmap

1. Foundation & security
2. Products & inventory — implemented on this branch
3. POS & cashier shifts
4. Purchasing & suppliers
5. Customers, loyalty & promotions
6. Online orders & delivery
7. Reports, backups, performance and production deployment
