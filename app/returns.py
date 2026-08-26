from datetime import datetime, timezone
from decimal import Decimal

from app import db


class SaleReturn(db.Model):
    __tablename__ = "sale_returns"
    id = db.Column(db.BigInteger, primary_key=True)
    return_number = db.Column(db.String(40), unique=True, nullable=False, index=True)
    sale_id = db.Column(db.BigInteger, db.ForeignKey("sales.id", ondelete="RESTRICT"), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    total = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    refund_method = db.Column(db.String(30), nullable=False)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default="COMPLETED")
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    items = db.relationship("SaleReturnItem", back_populates="return_doc", cascade="all, delete-orphan")


class SaleReturnItem(db.Model):
    __tablename__ = "sale_return_items"
    id = db.Column(db.BigInteger, primary_key=True)
    return_id = db.Column(db.BigInteger, db.ForeignKey("sale_returns.id", ondelete="CASCADE"), nullable=False, index=True)
    sale_item_id = db.Column(db.BigInteger, db.ForeignKey("sale_items.id", ondelete="RESTRICT"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = db.Column(db.Numeric(14, 3), nullable=False)
    unit_price = db.Column(db.Numeric(14, 3), nullable=False)
    line_total = db.Column(db.Numeric(14, 3), nullable=False)
    return_doc = db.relationship("SaleReturn", back_populates="items")


def create_return(*, sale_id, warehouse_id, user_id, items, refund_method, reason=None):
    from app.models import Sale, SaleItem, InventoryStock, InventoryMovement

    sale = db.session.get(Sale, sale_id)
    if not sale or sale.status != "COMPLETED":
        raise ValueError("COMPLETED_SALE_NOT_FOUND")
    if refund_method not in {"CASH", "VISA", "WALLET", "ORIGINAL"}:
        raise ValueError("INVALID_REFUND_METHOD")
    if not items:
        raise ValueError("RETURN_ITEMS_REQUIRED")

    sale_items = {item.id: item for item in sale.items}
    total = Decimal("0")
    return_doc = SaleReturn(
        return_number=f"RET-{sale.id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        sale_id=sale.id, warehouse_id=warehouse_id, user_id=user_id,
        refund_method=refund_method, reason=reason or "",
    )
    db.session.add(return_doc)

    for raw in items:
        sale_item = sale_items.get(int(raw["sale_item_id"]))
        qty = Decimal(str(raw["quantity"]))
        if not sale_item or qty <= 0 or qty > Decimal(str(sale_item.quantity)):
            raise ValueError("INVALID_RETURN_QUANTITY")
        existing = db.session.scalar(db.select(db.func.coalesce(db.func.sum(SaleReturnItem.quantity), 0)).where(SaleReturnItem.sale_item_id == sale_item.id))
        if qty + Decimal(str(existing or 0)) > Decimal(str(sale_item.quantity)):
            raise ValueError("RETURN_EXCEEDS_SOLD_QUANTITY")

        line_total = qty * Decimal(str(sale_item.unit_price))
        total += line_total
        db.session.add(SaleReturnItem(return_doc=return_doc, sale_item_id=sale_item.id,
                                      product_id=sale_item.product_id, quantity=qty,
                                      unit_price=sale_item.unit_price, line_total=line_total))
        stock = db.session.scalar(db.select(InventoryStock).where(
            InventoryStock.warehouse_id == warehouse_id,
            InventoryStock.product_id == sale_item.product_id,
            InventoryStock.batch_id.is_(None),
        ).with_for_update())
        if not stock:
            stock = InventoryStock(warehouse_id=warehouse_id, product_id=sale_item.product_id, quantity=0)
            db.session.add(stock)
            db.session.flush()
        stock.quantity += qty
        db.session.add(InventoryMovement(warehouse_id=warehouse_id, product_id=sale_item.product_id,
            movement_type="RETURN", quantity=qty, reference_type="SALE_RETURN",
            reference_id=str(return_doc.id), reason=reason or "Sale return", user_id=user_id))

    return_doc.total = total
    db.session.flush()
    return return_doc
