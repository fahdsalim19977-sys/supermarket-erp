from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Brand, Category, Product, ProductBarcode, Unit, Warehouse
from app.services.inventory_service import adjust_stock

products_bp = Blueprint("products", __name__, url_prefix="/products")


def _decimal(value, default="0"):
    try:
        return Decimal(value or default)
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid numeric value")


@products_bp.get("")
@login_required
def index():
    q = request.args.get("q", "").strip()
    query = db.select(Product).order_by(Product.id.desc())
    if q:
        query = query.where((Product.name_ar.ilike(f"%{q}%")) | (Product.name_en.ilike(f"%{q}%")) | (Product.sku.ilike(f"%{q}%")))
    products = db.session.scalars(query.limit(100)).all()
    warehouses = db.session.scalars(db.select(Warehouse).where(Warehouse.is_active.is_(True)).order_by(Warehouse.name)).all()
    return render_template("products/index.html", products=products, warehouses=warehouses, q=q)


@products_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    categories = db.session.scalars(db.select(Category).where(Category.is_active.is_(True)).order_by(Category.name_ar)).all()
    brands = db.session.scalars(db.select(Brand).where(Brand.is_active.is_(True)).order_by(Brand.name_ar)).all()
    units = db.session.scalars(db.select(Unit).order_by(Unit.name_ar)).all()
    if request.method == "POST":
        try:
            product = Product(sku=request.form["sku"].strip(), name_ar=request.form["name_ar"].strip(), name_en=request.form.get("name_en", "").strip() or None, category_id=int(request.form["category_id"]), brand_id=int(request.form["brand_id"]) if request.form.get("brand_id") else None, unit_id=int(request.form["unit_id"]), purchase_price=_decimal(request.form.get("purchase_price")), selling_price=_decimal(request.form.get("selling_price")), min_stock=_decimal(request.form.get("min_stock")), track_expiry="track_expiry" in request.form, track_batch="track_batch" in request.form)
            db.session.add(product)
            db.session.flush()
            barcode = request.form.get("barcode", "").strip()
            if barcode:
                db.session.add(ProductBarcode(product_id=product.id, barcode=barcode, is_primary=True))
            db.session.commit()
            flash("تم إنشاء المنتج بنجاح", "success")
            return redirect(url_for("products.index"))
        except (ValueError, InvalidOperation) as exc:
            db.session.rollback()
            flash(str(exc), "error")
    return render_template("products/form.html", categories=categories, brands=brands, units=units)


@products_bp.post("/<int:product_id>/stock")
@login_required
def stock_adjustment(product_id):
    try:
        warehouse_id = int(request.form["warehouse_id"])
        quantity = _decimal(request.form["quantity"])
        adjust_stock(warehouse_id=warehouse_id, product_id=product_id, quantity=quantity, movement_type=request.form.get("movement_type", "ADJUSTMENT"), user_id=current_user.id, reason=request.form.get("reason"))
        db.session.commit()
        flash("تم تحديث المخزون بنجاح", "success")
    except (ValueError, InvalidOperation) as exc:
        db.session.rollback()
        flash(str(exc), "error")
    return redirect(url_for("products.index"))


@products_bp.get("/lookup")
@login_required
def lookup():
    barcode = request.args.get("barcode", "").strip()
    product = db.session.scalar(db.select(Product).join(ProductBarcode).where(ProductBarcode.barcode == barcode, Product.is_active.is_(True))) if barcode else None
    if not product:
        return {"success": False, "error": "PRODUCT_NOT_FOUND"}, 404
    return {"success": True, "data": {"id": product.id, "sku": product.sku, "name_ar": product.name_ar, "name_en": product.name_en, "selling_price": str(product.selling_price), "unit": product.unit.code}}
