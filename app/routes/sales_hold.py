from flask import Blueprint, jsonify
from flask_login import login_required

from app import db
from app.services.sales_hold_service import hold_sale, resume_sale

sales_hold_bp = Blueprint("sales_hold", __name__, url_prefix="/api/pos/sales")

@ sales_hold_bp.post("/<int:sale_id>/hold")
@login_required
def hold(sale_id):
    try:
        sale = hold_sale(sale_id)
        db.session.commit()
        return jsonify(success=True, data={"id": sale.id, "status": sale.status})
    except ValueError as exc:
        db.session.rollback()
        return jsonify(success=False, error=str(exc)), 400

@ sales_hold_bp.post("/<int:sale_id>/resume")
@login_required
def resume(sale_id):
    try:
        sale = resume_sale(sale_id)
        db.session.commit()
        return jsonify(success=True, data={"id": sale.id, "status": sale.status})
    except ValueError as exc:
        db.session.rollback()
        return jsonify(success=False, error=str(exc)), 400
