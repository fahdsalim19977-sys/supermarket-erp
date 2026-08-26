from flask import Blueprint, jsonify, request
from flask_login import login_required

from app import db
from app.models.customer import Customer
from app.services.customer_service import create_customer

customers_bp = Blueprint("customers", __name__, url_prefix="/api/customers")


@customers_bp.get("")
@login_required
def list_customers():
    q = request.args.get("q", "").strip()
    stmt = db.select(Customer).where(Customer.is_active.is_(True)).order_by(Customer.name)
    if q:
        stmt = stmt.where(db.or_(Customer.name.ilike(f"%{q}%"), Customer.phone.ilike(f"%{q}%")))
    customers = db.session.scalars(stmt.limit(50)).all()
    return jsonify(success=True, data=[c.to_dict() for c in customers])


@customers_bp.post("")
@login_required
def add_customer():
    data = request.get_json(silent=True) or {}
    try:
        customer = create_customer(data.get("name"), data.get("phone"), data.get("email"), data.get("address"))
        db.session.commit()
        return jsonify(success=True, data=customer.to_dict()), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify(success=False, error=str(exc)), 400
