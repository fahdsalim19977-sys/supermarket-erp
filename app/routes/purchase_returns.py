from decimal import Decimal, InvalidOperation
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app import db
from app.services.purchase_return_service import return_purchase

purchase_returns_bp = Blueprint("purchase_returns", __name__, url_prefix="/api/purchasing")

@purchase_returns_bp.post("/returns/<int:order_id>")
@login_required
def create_return(order_id):
    data = request.get_json(silent=True) or {}
    try:
        order, total = return_purchase(order_id, int(data["warehouse_id"]), data.get("items", []), current_user.id)
        db.session.commit()
        return jsonify(success=True, data={"order_id": order.id, "returned_value": str(total)})
    except (KeyError, ValueError, InvalidOperation, TypeError) as exc:
        db.session.rollback()
        return jsonify(success=False, error=str(exc)), 400
