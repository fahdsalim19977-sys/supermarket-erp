from decimal import Decimal, InvalidOperation

from flask import Blueprint, request
from flask_login import current_user, login_required

from app import db
from app.models import Product, ProductBarcode, Sale
from app.services.pos_service import create_sale

pos_bp = Blueprint("pos", __name__, url_prefix="/api/pos")


def _json_error(message, status=400):
    return {"success": False, "error": message}, status


@pos_bp.get("/lookup")
@login_required
def lookup():
    barcode = request.args.get("barcode", "").strip()
    if not barcode:
        return _json_error("BARCODE_REQUIRED")
    product = db.session.scalar(db.select(Product).join(ProductBarcode).where(ProductBarcode.barcode == barcode, Product.is_active.is_(True)))
    if not product:
        return _json_error("PRODUCT_NOT_FOUND", 404)
    return {"success": True, "data": {"id": product.id, "sku": product.sku, "name_ar": product.name_ar, "name_en": product.name_en, "price": str(product.selling_price), "unit": product.unit.code}}


@pos_bp.post("/sales")
@login_required
def sale():
    payload = request.get_json(silent=True) or {}
    try:
        warehouse_id = int(payload["warehouse_id"])
        result = create_sale(warehouse_id=warehouse_id, user_id=current_user.id,
                             customer_id=payload.get("customer_id"), items=payload.get("items", []),
                             payments=payload.get("payments", []), discount=payload.get("discount", 0),
                             tax=payload.get("tax", 0))
        db.session.commit()
        return {"success": True, "data": {"id": result.id, "invoice_number": result.invoice_number, "subtotal": str(result.subtotal), "discount": str(result.discount), "tax": str(result.tax), "total": str(result.total), "status": result.status}}, 201
    except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
        db.session.rollback()
        return _json_error(str(exc))


@pos_bp.get("/sales/<int:sale_id>")
@login_required
def get_sale(sale_id):
    result = db.session.get(Sale, sale_id)
    if not result:
        return _json_error("SALE_NOT_FOUND", 404)
    return {"success": True, "data": {"id": result.id, "invoice_number": result.invoice_number, "subtotal": str(result.subtotal), "discount": str(result.discount), "tax": str(result.tax), "total": str(result.total), "status": result.status, "items": [{"product_id": i.product_id, "quantity": str(i.quantity), "unit_price": str(i.unit_price), "discount": str(i.discount), "line_total": str(i.line_total)} for i in result.items], "payments": [{"method": p.method, "amount": str(p.amount), "reference": p.reference} for p in result.payments]}}
