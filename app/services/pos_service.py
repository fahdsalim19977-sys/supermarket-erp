from decimal import Decimal

from app import db
from app.models import InventoryStock, Product, Sale, SaleItem, SalePayment
from app.services.inventory_service import adjust_stock


def create_sale(*, warehouse_id, user_id, items, payments, customer_id=None, discount=0, tax=0):
    if not items:
        raise ValueError("Sale must contain at least one item")

    sale = Sale(warehouse_id=warehouse_id, user_id=user_id, customer_id=customer_id,
                discount=Decimal(str(discount)), tax=Decimal(str(tax)), status="COMPLETED")
    db.session.add(sale)
    db.session.flush()

    subtotal = Decimal("0")
    for item in items:
        product = db.session.get(Product, int(item["product_id"]))
        if not product or not product.is_active:
            raise ValueError("Product not found")
        quantity = Decimal(str(item["quantity"]))
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        price = Decimal(str(item.get("unit_price", product.selling_price)))
        line_discount = Decimal(str(item.get("discount", 0)))
        line_total = quantity * price - line_discount
        if line_total < 0:
            raise ValueError("Line total cannot be negative")
        db.session.add(SaleItem(sale_id=sale.id, product_id=product.id, quantity=quantity,
                                unit_price=price, discount=line_discount, line_total=line_total))
        adjust_stock(warehouse_id=warehouse_id, product_id=product.id, quantity=-quantity,
                     movement_type="SALE", user_id=user_id, reference_type="SALE",
                     reference_id=str(sale.id))
        subtotal += line_total

    sale.subtotal = subtotal
    sale.total = subtotal - sale.discount + sale.tax
    if sale.total < 0:
        raise ValueError("Sale total cannot be negative")

    paid = Decimal("0")
    for payment in payments:
        amount = Decimal(str(payment["amount"]))
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        paid += amount
        db.session.add(SalePayment(sale_id=sale.id, method=payment["method"], amount=amount,
                                   reference=payment.get("reference")))
    if paid != sale.total:
        raise ValueError(f"Payment total must equal invoice total ({sale.total})")
    return sale
