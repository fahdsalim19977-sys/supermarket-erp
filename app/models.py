from datetime import datetime, timezone

from flask_login import UserMixin
from sqlalchemy import CheckConstraint, UniqueConstraint
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

user_roles = db.Table("user_roles", db.Column("user_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), db.Column("role_id", db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True))
role_permissions = db.Table("role_permissions", db.Column("role_id", db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True), db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True))

class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class Branch(TimestampMixin, db.Model):
    __tablename__ = "branches"
    id = db.Column(db.Integer, primary_key=True); code = db.Column(db.String(30), unique=True, nullable=False, index=True); name = db.Column(db.String(150), nullable=False); address = db.Column(db.String(300)); phone = db.Column(db.String(30)); is_active = db.Column(db.Boolean, default=True, nullable=False)
    warehouses = db.relationship("Warehouse", back_populates="branch", cascade="all, delete-orphan"); users = db.relationship("User", back_populates="branch")

class Warehouse(TimestampMixin, db.Model):
    __tablename__ = "warehouses"
    id = db.Column(db.Integer, primary_key=True); branch_id = db.Column(db.Integer, db.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=False, index=True); code = db.Column(db.String(30), nullable=False, index=True); name = db.Column(db.String(150), nullable=False); is_active = db.Column(db.Boolean, default=True, nullable=False)
    branch = db.relationship("Branch", back_populates="warehouses"); stocks = db.relationship("InventoryStock", back_populates="warehouse")
    __table_args__ = (UniqueConstraint("branch_id", "code", name="uq_warehouse_branch_code"),)

class Permission(TimestampMixin, db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True); code = db.Column(db.String(100), unique=True, nullable=False, index=True); description = db.Column(db.String(255))

class Role(TimestampMixin, db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True); name = db.Column(db.String(80), unique=True, nullable=False); description = db.Column(db.String(255))
    permissions = db.relationship("Permission", secondary=role_permissions, lazy="selectin"); users = db.relationship("User", secondary=user_roles, back_populates="roles")

class User(TimestampMixin, UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True); branch_id = db.Column(db.Integer, db.ForeignKey("branches.id", ondelete="SET NULL"), index=True); username = db.Column(db.String(80), unique=True, nullable=False, index=True); full_name = db.Column(db.String(150), nullable=False); password_hash = db.Column(db.String(255), nullable=False); is_active = db.Column(db.Boolean, default=True, nullable=False); last_login_at = db.Column(db.DateTime(timezone=True))
    branch = db.relationship("Branch", back_populates="users"); roles = db.relationship("Role", secondary=user_roles, back_populates="users", lazy="selectin")
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)
    def has_permission(self, permission_code): return any(permission_code == permission.code for role in self.roles for permission in role.permissions)

class SystemSetting(TimestampMixin, db.Model):
    __tablename__ = "system_settings"
    id = db.Column(db.Integer, primary_key=True); key = db.Column(db.String(100), unique=True, nullable=False, index=True); value = db.Column(db.Text); description = db.Column(db.String(255))

class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.BigInteger, primary_key=True); user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True); action = db.Column(db.String(100), nullable=False, index=True); entity_type = db.Column(db.String(100), index=True); entity_id = db.Column(db.String(100), index=True); old_value = db.Column(db.JSON); new_value = db.Column(db.JSON); ip_address = db.Column(db.String(45)); created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    user = db.relationship("User", backref=db.backref("audit_logs", lazy="dynamic"))

class Category(TimestampMixin, db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True); name_ar = db.Column(db.String(120), nullable=False); name_en = db.Column(db.String(120)); code = db.Column(db.String(40), unique=True, nullable=False, index=True); parent_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL"), index=True); is_active = db.Column(db.Boolean, default=True, nullable=False)
    parent = db.relationship("Category", remote_side=[id], backref="children"); products = db.relationship("Product", back_populates="category")

class Brand(TimestampMixin, db.Model):
    __tablename__ = "brands"
    id = db.Column(db.Integer, primary_key=True); name_ar = db.Column(db.String(120), nullable=False); name_en = db.Column(db.String(120)); code = db.Column(db.String(40), unique=True, nullable=False, index=True); is_active = db.Column(db.Boolean, default=True, nullable=False); products = db.relationship("Product", back_populates="brand")

class Unit(TimestampMixin, db.Model):
    __tablename__ = "units"
    id = db.Column(db.Integer, primary_key=True); code = db.Column(db.String(20), unique=True, nullable=False); name_ar = db.Column(db.String(60), nullable=False); name_en = db.Column(db.String(60)); allows_decimal = db.Column(db.Boolean, default=False, nullable=False); products = db.relationship("Product", back_populates="unit")

class Product(TimestampMixin, db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True); sku = db.Column(db.String(60), unique=True, nullable=False, index=True); name_ar = db.Column(db.String(200), nullable=False, index=True); name_en = db.Column(db.String(200), index=True); category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True); brand_id = db.Column(db.Integer, db.ForeignKey("brands.id", ondelete="SET NULL"), index=True); unit_id = db.Column(db.Integer, db.ForeignKey("units.id", ondelete="RESTRICT"), nullable=False); purchase_price = db.Column(db.Numeric(14, 3), default=0, nullable=False); selling_price = db.Column(db.Numeric(14, 3), default=0, nullable=False); min_stock = db.Column(db.Numeric(14, 3), default=0, nullable=False); track_expiry = db.Column(db.Boolean, default=False, nullable=False); track_batch = db.Column(db.Boolean, default=False, nullable=False); allow_negative_stock = db.Column(db.Boolean, default=False, nullable=False); is_active = db.Column(db.Boolean, default=True, nullable=False)
    category = db.relationship("Category", back_populates="products"); brand = db.relationship("Brand", back_populates="products"); unit = db.relationship("Unit", back_populates="products"); barcodes = db.relationship("ProductBarcode", back_populates="product", cascade="all, delete-orphan"); batches = db.relationship("ProductBatch", back_populates="product", cascade="all, delete-orphan"); stocks = db.relationship("InventoryStock", back_populates="product")
    __table_args__ = (CheckConstraint("purchase_price >= 0", name="ck_product_purchase_price_nonnegative"), CheckConstraint("selling_price >= 0", name="ck_product_selling_price_nonnegative"), CheckConstraint("min_stock >= 0", name="ck_product_min_stock_nonnegative"))

class ProductBarcode(db.Model):
    __tablename__ = "product_barcodes"
    id = db.Column(db.Integer, primary_key=True); product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True); barcode = db.Column(db.String(80), unique=True, nullable=False, index=True); is_primary = db.Column(db.Boolean, default=False, nullable=False); product = db.relationship("Product", back_populates="barcodes")

class ProductBatch(TimestampMixin, db.Model):
    __tablename__ = "product_batches"
    id = db.Column(db.Integer, primary_key=True); product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True); batch_number = db.Column(db.String(80), nullable=False); production_date = db.Column(db.Date); expiry_date = db.Column(db.Date, index=True); product = db.relationship("Product", back_populates="batches")
    __table_args__ = (UniqueConstraint("product_id", "batch_number", name="uq_product_batch"),)

class InventoryStock(TimestampMixin, db.Model):
    __tablename__ = "inventory_stock"
    id = db.Column(db.BigInteger, primary_key=True); warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True); product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True); batch_id = db.Column(db.Integer, db.ForeignKey("product_batches.id", ondelete="RESTRICT"), index=True); quantity = db.Column(db.Numeric(14, 3), default=0, nullable=False)
    warehouse = db.relationship("Warehouse", back_populates="stocks"); product = db.relationship("Product", back_populates="stocks"); batch = db.relationship("ProductBatch")
    __table_args__ = (UniqueConstraint("warehouse_id", "product_id", "batch_id", name="uq_inventory_stock_location_product_batch"), CheckConstraint("quantity >= 0", name="ck_inventory_quantity_nonnegative"))

class InventoryMovement(TimestampMixin, db.Model):
    __tablename__ = "inventory_movements"
    id = db.Column(db.BigInteger, primary_key=True); warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True); product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True); batch_id = db.Column(db.Integer, db.ForeignKey("product_batches.id", ondelete="RESTRICT"), index=True); movement_type = db.Column(db.String(30), nullable=False, index=True); quantity = db.Column(db.Numeric(14, 3), nullable=False); reference_type = db.Column(db.String(40)); reference_id = db.Column(db.String(80)); reason = db.Column(db.String(255)); user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True)
    __table_args__ = (CheckConstraint("quantity <> 0", name="ck_inventory_movement_nonzero"),)
