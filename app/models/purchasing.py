from datetime import datetime, timezone
from app import db

class Supplier(db.Model):
    __tablename__ = "suppliers"
    id = db.Column(db.BigInteger, primary_key=True)
    code = db.Column(db.String(40), unique=True, nullable=False, index=True)
    name = db.Column(db.String(180), nullable=False, index=True)
    phone = db.Column(db.String(30), index=True)
    email = db.Column(db.String(255))
    address = db.Column(db.String(500))
    tax_number = db.Column(db.String(80), unique=True)
    credit_limit = db.Column(db.Numeric(14, 3), default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class PurchaseOrder(db.Model):
    __tablename__ = "purchase_orders"
    id = db.Column(db.BigInteger, primary_key=True)
    order_number = db.Column(db.String(40), unique=True, nullable=False, index=True)
    supplier_id = db.Column(db.BigInteger, db.ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True)
    status = db.Column(db.String(20), default="DRAFT", nullable=False, index=True)
    subtotal = db.Column(db.Numeric(14, 3), default=0, nullable=False)
    discount = db.Column(db.Numeric(14, 3), default=0, nullable=False)
    tax = db.Column(db.Numeric(14, 3), default=0, nullable=False)
    total = db.Column(db.Numeric(14, 3), default=0, nullable=False)
    notes = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    supplier = db.relationship("Supplier")
    items = db.relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan")

class PurchaseOrderItem(db.Model):
    __tablename__ = "purchase_order_items"
    id = db.Column(db.BigInteger, primary_key=True)
    purchase_order_id = db.Column(db.BigInteger, db.ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity = db.Column(db.Numeric(14, 3), nullable=False)
    received_quantity = db.Column(db.Numeric(14, 3), default=0, nullable=False)
    unit_cost = db.Column(db.Numeric(14, 3), nullable=False)
    line_total = db.Column(db.Numeric(14, 3), nullable=False)
    order = db.relationship("PurchaseOrder", back_populates="items")
    product = db.relationship("Product")
