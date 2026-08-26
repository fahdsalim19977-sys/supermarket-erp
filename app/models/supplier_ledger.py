from datetime import datetime, timezone
from app import db

class SupplierLedgerEntry(db.Model):
    __tablename__ = "supplier_ledger_entries"
    id = db.Column(db.BigInteger, primary_key=True)
    supplier_id = db.Column(db.BigInteger, db.ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False, index=True)
    entry_type = db.Column(db.String(30), nullable=False, index=True)
    reference_type = db.Column(db.String(40))
    reference_id = db.Column(db.String(80))
    debit = db.Column(db.Numeric(14, 3), default=0, nullable=False)
    credit = db.Column(db.Numeric(14, 3), default=0, nullable=False)
    balance_after = db.Column(db.Numeric(14, 3), nullable=False)
    notes = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    supplier = db.relationship("Supplier")
