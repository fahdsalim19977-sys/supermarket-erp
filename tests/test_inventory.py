from decimal import Decimal

import pytest

from app import db
from app.models import Branch, Category, Product, Unit, User, Warehouse
from app.services.inventory_service import adjust_stock


def _setup(app):
    with app.app_context():
        branch = Branch(code="B1", name="Branch 1")
        db.session.add(branch); db.session.flush()
        warehouse = Warehouse(branch_id=branch.id, code="W1", name="Warehouse 1")
        unit = Unit(code="PCS", name_ar="قطعة", name_en="Piece")
        category = Category(code="CAT", name_ar="عام", name_en="General")
        db.session.add_all([warehouse, unit, category]); db.session.flush()
        product = Product(sku="SKU-1", name_ar="منتج", category_id=category.id, unit_id=unit.id, selling_price=10)
        user = User(username="u1", full_name="User")
        user.set_password("password")
        db.session.add_all([product, user]); db.session.commit()
        return warehouse.id, product.id, user.id


def test_stock_add_and_remove(app):
    warehouse_id, product_id, user_id = _setup(app)
    with app.app_context():
        adjust_stock(warehouse_id=warehouse_id, product_id=product_id, quantity=10, movement_type="PURCHASE", user_id=user_id)
        adjust_stock(warehouse_id=warehouse_id, product_id=product_id, quantity=-3, movement_type="SALE", user_id=user_id)
        db.session.commit()
        stock = db.session.execute(db.select(__import__("app.models", fromlist=["InventoryStock"]).InventoryStock)).scalar_one()
        assert Decimal(stock.quantity) == Decimal("7")


def test_negative_stock_rejected(app):
    warehouse_id, product_id, user_id = _setup(app)
    with app.app_context():
        with pytest.raises(ValueError, match="Insufficient stock"):
            adjust_stock(warehouse_id=warehouse_id, product_id=product_id, quantity=-1, movement_type="SALE", user_id=user_id)
