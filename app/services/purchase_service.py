from decimal import Decimal

from app import db
from app.models import InventoryMovement, InventoryStock, Product, Warehouse


def receive_purchase(warehouse_id, items, reference_id=None, user_id=None):
    warehouse = db.session.get(Warehouse, warehouse_id)
    if not warehouse:
        raise ValueError("WAREHOUSE_NOT_FOUND")
    if not items:
        raise ValueError("PURCHASE_ITEMS_REQUIRED")
    received = []
    for item in items:
        product_id = int(item["product_id"])
        quantity = Decimal(str(item["quantity"]))
        if quantity <= 0:
            raise ValueError("RECEIVED_QUANTITY_MUST_BE_POSITIVE")
        product = db.session.get(Product, product_id)
        if not product or not product.is_active:
            raise ValueError(f"PRODUCT_NOT_FOUND:{product_id}")
        stock = db.session.scalar(db.select(InventoryStock).where(
            InventoryStock.warehouse_id == warehouse_id,
            InventoryStock.product_id == product_id,
            InventoryStock.batch_id.is_(None),
        ))
        if not stock:
            stock = InventoryStock(warehouse_id=warehouse_id, product_id=product_id, quantity=0)
            db.session.add(stock)
            db.session.flush()
        stock.quantity += quantity
        db.session.add(InventoryMovement(
            warehouse_id=warehouse_id, product_id=product_id,
            movement_type="PURCHASE", quantity=quantity,
            reference_type="PURCHASE_RECEIPT",
            reference_id=str(reference_id) if reference_id is not None else None,
            user_id=user_id,
        ))
        received.append({"product_id": product_id, "quantity": str(quantity)})
    db.session.flush()
    return received
