from app import db
from app.models import Sale


def hold_sale(sale_id):
    sale = db.session.get(Sale, sale_id)
    if not sale:
        raise ValueError("SALE_NOT_FOUND")
    if sale.status != "DRAFT":
        raise ValueError("ONLY_DRAFT_SALES_CAN_BE_HELD")
    sale.status = "HELD"
    db.session.flush()
    return sale


def resume_sale(sale_id):
    sale = db.session.get(Sale, sale_id)
    if not sale:
        raise ValueError("SALE_NOT_FOUND")
    if sale.status != "HELD":
        raise ValueError("SALE_IS_NOT_HELD")
    sale.status = "DRAFT"
    db.session.flush()
    return sale
