from decimal import Decimal, InvalidOperation
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app import db
from app.returns import create_return

returns_bp = Blueprint("returns", __name__, url_prefix="/api/pos/returns")

@returns_bp.post("")
@login_required
def create():
    data = request.get_json(silent=True) or {}
    try:
        doc = create_return(
            sale_id=int(data["sale_id"]),
            warehouse_id=int(data["warehouse_id"]),
            user_id=current_user.id,
            items=data.get("items", []),
            refund_method=data["refund_method"],
            reason=data.get("reason"),
        )
        db.session.commit()
        return jsonify(success=True, data={"id": doc.id, "return_number": doc.return_number, "total": str(doc.total), "status": doc.status}), 201
    except (KeyError, ValueError, InvalidOperation, TypeError) as exc:
        db.session.rollback()
        return jsonify(success=False, error=str(exc)), 400
