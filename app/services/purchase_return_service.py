from decimal import Decimal
from app import db
from app.models import InventoryMovement, InventoryStock
from app.models.purchasing import PurchaseOrder, PurchaseOrderItem, Supplier


def return_purchase(order_id, warehouse_id, items, user_id):
    order = db.session.get(PurchaseOrder, order_id)
    if not order or order.warehouse_id != warehouse_id:
        raise ValueError("PURCHASE_ORDER_NOT_FOUND")
    if order.status not in {"RECEIVED", "PARTIALLY_RECEIVED"}:
        raise ValueError("PURCHASE_ORDER_NOT_RETURNABLE")
    total = Decimal("0")
    for payload in items:
        line = db.session.get(PurchaseOrderItem, int(payload["item_id"]))
        qty = Decimal(str(payload["quantity"]))
        if not line or line.purchase_order_id != order.id:
            raise ValueError("PURCHASE_ITEM_NOT_FOUND")
        if qty <= 0 or qty > line.received_quantity:
            raise ValueError("RETURN_QUANTITY_EXCEEDS_RECEIVED")
        stock = db.session.scalar(db.select(InventoryStock).where(
            InventoryStock.warehouse_id == warehouse_id,
            InventoryStock.product_id == line.product_id,
            InventoryStock.batch_id.is_(None),
        ))
        if not stock or stock.quantity < qty:
            raise ValueError("INSUFFICIENT_STOCK_FOR_RETURN")
        stock.quantity -= qty
        db.session.add(InventoryMovement(
            warehouse_id=warehouse_id, product_id=line.product_id,
            movement_type="PURCHASE_RETURN", quantity=-qty,
            reference_type="PURCHASE_ORDER", reference_id=str(order.id), user_id=user_id,
        ))
        line.received_quantity -= qty
        total += qty * line.unit_cost
    db.session.flush()
    return order, total
