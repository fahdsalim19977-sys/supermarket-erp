from decimal import Decimal


def build_receipt(sale):
    """Build a printer-friendly 80mm receipt payload."""
    return {
        "invoice_number": sale.invoice_number,
        "created_at": sale.created_at.isoformat() if sale.created_at else None,
        "items": [
            {
                "name": item.product.name_ar,
                "quantity": str(item.quantity),
                "unit_price": str(item.unit_price),
                "total": str(item.line_total),
            }
            for item in sale.items
        ],
        "subtotal": str(sale.subtotal),
        "discount": str(sale.discount),
        "tax": str(sale.tax),
        "total": str(sale.total),
    }
