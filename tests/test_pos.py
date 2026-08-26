from decimal import Decimal

import pytest

from app import db
from app.models import Branch, Category, Product, ProductBarcode, Unit, User, Warehouse
from app.services.inventory_service import adjust_stock
from app.services.pos_service import create_sale


def _setup(app):
    with app.app_context():
        branch = Branch(code="POS1", name="POS Branch")
        db.session.add(branch); db.session.flush()
        warehouse = Warehouse(branch_id=branch.id, code="POSW", name="POS Warehouse")
        unit = Unit(code="PPCS", name_ar="قطعة", name_en="Piece")
        category = Category(code="PCAT", name_ar="عام", name_en="General")
        db.session.add_all([warehouse, unit, category]); db.session.flush()
        product = Product(sku="POS-SKU-1", name_ar="منتج كاشير", category_id=category.id, unit_id=unit.id, selling_price=25)
        db.session.add(product); db.session.flush()
        db.session.add(ProductBarcode(product_id=product.id, barcode="622000000001", is_primary=True))
        user = User(username="pos-user", full_name="POS User"); user.set_password("password"); db.session.add(user)
        db.session.commit()
        adjust_stock(warehouse_id=warehouse.id, product_id=product.id, quantity=10, movement_type="PURCHASE", user_id=user.id)
        db.session.commit()
        return warehouse.id, product.id, user.id


def test_create_sale_updates_stock_and_accepts_mixed_payment(app):
    warehouse_id, product_id, user_id = _setup(app)
    with app.app_context():
        sale = create_sale(
            warehouse_id=warehouse_id, user_id=user_id,
            items=[{"product_id": product_id, "quantity": 2}],
            payments=[{"method": "CASH", "amount": "20"}, {"method": "VISA", "amount": "30"}],
        )
        db.session.commit()
        assert sale.invoice_number.startswith("INV-")
        assert Decimal(sale.total) == Decimal("50")
        assert len(sale.payments) == 2
        stock = db.session.scalar(db.select(__import__("app.models", fromlist=["InventoryStock"]).InventoryStock).where(__import__("app.models", fromlist=["InventoryStock"]).InventoryStock.product_id == product_id))
        assert Decimal(stock.quantity) == Decimal("8")


def test_sale_rolls_back_on_insufficient_stock(app):
    warehouse_id, product_id, user_id = _setup(app)
    with app.app_context():
        with pytest.raises(ValueError, match="Insufficient stock"):
            create_sale(warehouse_id=warehouse_id, user_id=user_id,
                        items=[{"product_id": product_id, "quantity": 99}],
                        payments=[{"method": "CASH", "amount": "2475"}])
        db.session.rollback()
        assert db.session.scalar(db.select(__import__("app.models", fromlist=["Sale"]).Sale)) is None
