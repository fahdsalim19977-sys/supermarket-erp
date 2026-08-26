from decimal import Decimal, InvalidOperation
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app import db
from app.models.purchasing import Supplier, PurchaseOrder
from app.services.purchasing_service import receive_purchase

purchasing_bp = Blueprint("purchasing", __name__, url_prefix="/api/purchasing")

@purchasing_bp.get("/suppliers")
@login_required
def suppliers():
    q = request.args.get("q", "").strip()
    stmt = db.select(Supplier).where(Supplier.is_active.is_(True)).order_by(Supplier.name)
    if q:
        stmt = stmt.where(db.or_(Supplier.name.ilike(f"%{q}%"), Supplier.code.ilike(f"%{q}%"), Supplier.phone.ilike(f"%{q}%")))
    rows = db.session.scalars(stmt.limit(50)).all()
    return jsonify(success=True, data=[{"id": x.id, "code": x.code, "name": x.name, "phone": x.phone, "credit_limit": str(x.credit_limit)} for x in rows])

@purchasing_bp.post("/receiving/<int:order_id>")
@login_required
def receive(order_id):
    data = request.get_json(silent=True) or {}
    try:
        order, value = receive_purchase(order_id, int(data["warehouse_id"]), data.get("items", []), current_user.id)
        db.session.commit()
        return jsonify(success=True, data={"order_id": order.id, "status": order.status, "received_value": str(value)})
    except (KeyError, ValueError, InvalidOperation, TypeError) as exc:
        db.session.rollback()
        return jsonify(success=False, error=str(exc)), 400
