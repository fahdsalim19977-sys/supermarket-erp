from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app import db
from app.services.cashier_service import close_shift, open_shift

shifts_bp = Blueprint("shifts", __name__, url_prefix="/api/shifts")

@shifts_bp.post("")
@login_required
def create_shift():
    data = request.get_json(silent=True) or {}
    try:
        shift = open_shift(current_user.id, int(data["warehouse_id"]), Decimal(str(data.get("opening_cash", 0))))
        db.session.commit()
        return jsonify(success=True, data={"id": shift.id, "status": shift.status, "opening_cash": str(shift.opening_cash)}), 201
    except (KeyError, ValueError, InvalidOperation, TypeError) as exc:
        db.session.rollback()
        return jsonify(success=False, error=str(exc)), 400

@shifts_bp.post("/<int:shift_id>/close")
@login_required
def close(shift_id):
    data = request.get_json(silent=True) or {}
    try:
        shift = close_shift(shift_id, Decimal(str(data["closing_cash"])))
        db.session.commit()
        return jsonify(success=True, data={"id": shift.id, "status": shift.status, "closing_cash": str(shift.closing_cash), "difference": str(shift.difference)})
    except (KeyError, ValueError, InvalidOperation, TypeError) as exc:
        db.session.rollback()
        return jsonify(success=False, error=str(exc)), 400
