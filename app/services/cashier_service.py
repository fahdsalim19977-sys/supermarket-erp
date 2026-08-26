from decimal import Decimal

from app import db
from app.models import CashierShift


def open_shift(user_id, branch_id, opening_cash):
    existing = db.session.scalar(db.select(CashierShift).where(
        CashierShift.user_id == user_id,
        CashierShift.status == "OPEN",
    ))
    if existing:
        raise ValueError("OPEN_SHIFT_ALREADY_EXISTS")
    shift = CashierShift(
        user_id=user_id,
        branch_id=branch_id,
        opening_cash=Decimal(str(opening_cash)),
        status="OPEN",
    )
    db.session.add(shift)
    db.session.flush()
    return shift


def close_shift(shift_id, actual_cash):
    shift = db.session.get(CashierShift, shift_id)
    if not shift:
        raise ValueError("SHIFT_NOT_FOUND")
    if shift.status != "OPEN":
        raise ValueError("SHIFT_ALREADY_CLOSED")
    shift.actual_cash = Decimal(str(actual_cash))
    shift.status = "CLOSED"
    db.session.flush()
    return shift
