from decimal import Decimal
from app import db
from app.models import Product, InventoryStock, InventoryMovement
from app.models.purchasing import PurchaseOrder, PurchaseOrderItem


def receive_purchase(order_id, warehouse_id, items, user_id):
    order = db.session.get(PurchaseOrder, order_id)
    if not order:
        raise ValueError("PURCHASE_ORDER_NOT_FOUND")
    if order.warehouse_id != warehouse_id:
        raise ValueError("WAREHOUSE_MISMATCH")
    if order.status in {"CANCELLED", "CLOSED"}:
        raise ValueError("PURCHASE_ORDER_NOT_RECEIVABLE")

    received_total = Decimal("0")
    for payload in items:
        line = db.session.get(PurchaseOrderItem, int(payload["item_id"]))
        qty = Decimal(str(payload["quantity"]))
        if not line or line.purchase_order_id != order.id:
            raise ValueError("PURCHASE_ITEM_NOT_FOUND")
        if qty <= 0 or qty > (line.quantity - line.received_quantity):
            raise ValueError("RECEIVE_QUANTITY_EXCEEDS_REMAINING")
        product = db.session.get(Product, line.product_id)
        stock = db.session.scalar(db.select(InventoryStock).where(
            InventoryStock.warehouse_id == warehouse_id,
            InventoryStock.product_id == product.id,
            InventoryStock.batch_id.is_(None),
        ))
        if not stock:
            stock = InventoryStock(warehouse_id=warehouse_id, product_id=product.id, quantity=0)
            db.session.add(stock)
        stock.quantity += qty
        db.session.add(InventoryMovement(
            warehouse_id=warehouse_id, product_id=product.id, movement_type="PURCHASE",
            quantity=qty, reference_type="PURCHASE_ORDER", reference_id=str(order.id), user_id=user_id,
        ))
        line.received_quantity += qty
        received_total += qty * line.unit_cost

    remaining = any(line.received_quantity < line.quantity for line in order.items)
    order.status = "PARTIALLY_RECEIVED" if remaining else "RECEIVED"
    db.session.flush()
    return order, received_total
