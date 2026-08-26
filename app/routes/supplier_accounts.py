from decimal import Decimal, InvalidOperation
from flask import Blueprint, jsonify, request
from flask_login import login_required
from app import db
from app.models.purchasing import Supplier
from app.services.supplier_account_service import add_supplier_balance, pay_supplier

supplier_accounts_bp = Blueprint("supplier_accounts", __name__, url_prefix="/api/purchasing/suppliers")

@supplier_accounts_bp.get("/<int:supplier_id>/balance")
@login_required
def balance(supplier_id):
    supplier = db.session.get(Supplier, supplier_id)
    if not supplier:
        return jsonify(success=False, error="SUPPLIER_NOT_FOUND"), 404
    return jsonify(success=True, data={"supplier_id": supplier.id, "balance": str(supplier.balance or 0)})

@supplier_accounts_bp.post("/<int:supplier_id>/payments")
@login_required
def payment(supplier_id):
    try:
        amount = Decimal(str((request.get_json(silent=True) or {})["amount"]))
        supplier = pay_supplier(supplier_id, amount)
        db.session.commit()
        return jsonify(success=True, data={"supplier_id": supplier.id, "balance": str(supplier.balance)})
    except (KeyError, ValueError, InvalidOperation, TypeError) as exc:
        db.session.rollback()
        return jsonify(success=False, error=str(exc)), 400
