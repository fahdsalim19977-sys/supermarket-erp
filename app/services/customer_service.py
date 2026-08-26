from app import db
from app.models import Customer


def create_customer(name, phone=None, email=None, address=None):
    if not name or not name.strip():
        raise ValueError("CUSTOMER_NAME_REQUIRED")
    customer = Customer(name=name.strip(), phone=phone, email=email, address=address)
    db.session.add(customer)
    db.session.flush()
    return customer
