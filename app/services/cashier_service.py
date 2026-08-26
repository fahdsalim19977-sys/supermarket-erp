from datetime import datetime, timezone
from decimal import Decimal

from app import db
from app.models import CashierShift


def open_shift(user_id, warehouse_id, opening_cash):
    existing = db.session.scalar(db.select(CashierShift).where(
        CashierShift.user_id == user_id,
        CashierShift.status == "OPEN",
    ))
    if existing:
        raise ValueError("OPEN_SHIFT_ALREADY_EXISTS")
    shift = CashierShift(
        user_id=user_id,
        warehouse_id=warehouse_id,
        opening_cash=Decimal(str(opening_cash)),
        status="OPEN",
    )
    db.session.add(shift)
    db.session.flush()
    return shift


def close_shift(shift_id, actual_cash, expected_cash=None):
    shift = db.session.get(CashierShift, shift_id)
    if not shift:
        raise ValueError("SHIFT_NOT_FOUND")
    if shift.status != "OPEN":
        raise ValueError("SHIFT_ALREADY_CLOSED")

    actual = Decimal(str(actual_cash))
    expected = Decimal(str(expected_cash)) if expected_cash is not None else shift.expected_cash
    shift.closing_cash = actual
    shift.expected_cash = expected
    shift.difference = actual - expected if expected is not None else None
    shift.status = "CLOSED"
    shift.closed_at = datetime.now(timezone.utc)
    db.session.flush()
    return shift
