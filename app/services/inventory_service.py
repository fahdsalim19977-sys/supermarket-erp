from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import InventoryMovement, InventoryStock, Product


def adjust_stock(*, warehouse_id, product_id, quantity, movement_type, user_id=None, batch_id=None, reason=None, reference_type=None, reference_id=None):
    """Atomically adjust stock and write an immutable movement record.

    Positive quantity adds stock; negative quantity removes it. PostgreSQL row
    locking is used when available to prevent concurrent overselling.
    """
    quantity = Decimal(str(quantity))
    if quantity == 0:
        raise ValueError("Stock adjustment quantity cannot be zero")

    product = db.session.get(Product, product_id)
    if not product:
        raise ValueError("Product not found")

    stmt = select(InventoryStock).where(
        InventoryStock.warehouse_id == warehouse_id,
        InventoryStock.product_id == product_id,
        InventoryStock.batch_id == batch_id,
    ).with_for_update()
    stock = db.session.scalar(stmt)

    if not stock:
        if quantity < 0 and not product.allow_negative_stock:
            raise ValueError("Insufficient stock")
        stock = InventoryStock(warehouse_id=warehouse_id, product_id=product_id, batch_id=batch_id, quantity=Decimal("0"))
        db.session.add(stock)
        db.session.flush()

    new_quantity = Decimal(stock.quantity) + quantity
    if new_quantity < 0 and not product.allow_negative_stock:
        raise ValueError("Insufficient stock")

    stock.quantity = new_quantity
    movement = InventoryMovement(
        warehouse_id=warehouse_id,
        product_id=product_id,
        batch_id=batch_id,
        movement_type=movement_type,
        quantity=quantity,
        reference_type=reference_type,
        reference_id=reference_id,
        reason=reason,
        user_id=user_id,
    )
    db.session.add(movement)
    return stock, movement


def set_stock(*, warehouse_id, product_id, quantity, user_id=None, batch_id=None, reason="Stock count"):
    quantity = Decimal(str(quantity))
    stmt = select(InventoryStock).where(
        InventoryStock.warehouse_id == warehouse_id,
        InventoryStock.product_id == product_id,
        InventoryStock.batch_id == batch_id,
    ).with_for_update()
    stock = db.session.scalar(stmt)
    current = Decimal(stock.quantity) if stock else Decimal("0")
    delta = quantity - current
    if delta == 0:
        return stock
    stock, _ = adjust_stock(
        warehouse_id=warehouse_id,
        product_id=product_id,
        quantity=delta,
        movement_type="ADJUSTMENT",
        user_id=user_id,
        batch_id=batch_id,
        reason=reason,
    )
    return stock
