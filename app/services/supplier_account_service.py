from decimal import Decimal
from app import db
from app.models.purchasing import Supplier


def add_supplier_balance(supplier_id, amount):
    supplier = db.session.get(Supplier, supplier_id)
    if not supplier:
        raise ValueError("SUPPLIER_NOT_FOUND")
    amount = Decimal(str(amount))
    if amount < 0:
        raise ValueError("AMOUNT_MUST_BE_NONNEGATIVE")
    supplier.balance = (supplier.balance or Decimal("0")) + amount
    db.session.flush()
    return supplier


def pay_supplier(supplier_id, amount):
    supplier = db.session.get(Supplier, supplier_id)
    if not supplier:
        raise ValueError("SUPPLIER_NOT_FOUND")
    amount = Decimal(str(amount))
    if amount <= 0 or amount > (supplier.balance or Decimal("0")):
        raise ValueError("INVALID_SUPPLIER_PAYMENT")
    supplier.balance -= amount
    db.session.flush()
    return supplier
