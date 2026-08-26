from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app import db
from app.models import Sale
from app.services.pos_service import create_sale

pos_bp = Blueprint("pos", __name__, url_prefix="/pos")


@pos_bp.get("")
@login_required
def index():
    return render_template("pos/index.html")


@pos_bp.get("/api/lookup")
@login_required
def lookup():
    from app.models import Product, ProductBarcode

    barcode = request.args.get("barcode", "").strip()
    product = db.session.scalar(
        db.select(Product)
        .join(ProductBarcode)
        .where(ProductBarcode.barcode == barcode, Product.is_active.is_(True))
    ) if barcode else None
    if not product:
        return jsonify(success=False, error="PRODUCT_NOT_FOUND"), 404
    return jsonify(success=True, data={
        "id": product.id,
        "sku": product.sku,
        "name": product.name_ar,
        "price": str(product.selling_price),
        "unit": product.unit.code,
    })


@pos_bp.post("/api/sales")
@login_required
def sales_create():
    payload = request.get_json(silent=True) or {}
    try:
        sale = create_sale(
            warehouse_id=int(payload["warehouse_id"]),
            user_id=current_user.id,
            customer_id=payload.get("customer_id"),
            items=payload.get("items", []),
            payments=payload.get("payments", []),
            discount=Decimal(str(payload.get("discount", 0))),
            tax=Decimal(str(payload.get("tax", 0))),
        )
        db.session.commit()
        return jsonify(success=True, data={
            "id": sale.id,
            "invoice_number": sale.invoice_number,
            "total": str(sale.total),
        }), 201
    except (KeyError, ValueError, InvalidOperation, TypeError) as exc:
        db.session.rollback()
        return jsonify(success=False, error=str(exc)), 400


@pos_bp.get("/api/sales/<int:sale_id>")
@login_required
def sale_detail(sale_id):
    sale = db.session.get(Sale, sale_id)
    if not sale:
        return jsonify(success=False, error="SALE_NOT_FOUND"), 404
    return jsonify(success=True, data={
        "id": sale.id,
        "invoice_number": sale.invoice_number,
        "subtotal": str(sale.subtotal),
        "discount": str(sale.discount),
        "tax": str(sale.tax),
        "total": str(sale.total),
        "status": sale.status,
    })
