from decimal import Decimal
from app import db
from app.models import Product
from app.models.purchasing import PurchaseOrder


def apply_purchase_cost(order_id):
    order = db.session.get(PurchaseOrder, order_id)
    if not order:
        raise ValueError("PURCHASE_ORDER_NOT_FOUND")
    received = [x for x in order.items if x.received_quantity > 0]
    if not received:
        raise ValueError("NO_RECEIVED_ITEMS")
    for item in received:
        product = db.session.get(Product, item.product_id)
        product.purchase_price = item.unit_cost
    db.session.flush()
    return order
