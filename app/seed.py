from app import db
from app.models import Brand, Category, Permission, Role, Unit, User, Warehouse

PERMISSIONS = [
    ("dashboard.view", "View dashboard"), ("users.manage", "Manage users"), ("roles.manage", "Manage roles and permissions"),
    ("branches.manage", "Manage branches"), ("warehouses.manage", "Manage warehouses"), ("settings.manage", "Manage system settings"),
    ("audit.view", "View audit logs"), ("products.view", "View products"), ("products.create", "Create products"),
    ("inventory.view", "View inventory"), ("inventory.adjust", "Adjust inventory"), ("inventory.transfer", "Transfer inventory"),
]
DEFAULT_ADMIN_PASSWORD = "ChangeMe123!"


def seed_database():
    branch = db.session.scalar(db.select(__import__("app.models", fromlist=["Branch"]).Branch).where(__import__("app.models", fromlist=["Branch"]).Branch.code == "MAIN"))
    if not branch:
        from app.models import Branch
        branch = Branch(code="MAIN", name="Main Branch")
        db.session.add(branch); db.session.flush()
    warehouse = db.session.scalar(db.select(Warehouse).where(Warehouse.branch_id == branch.id, Warehouse.code == "MAIN"))
    if not warehouse:
        db.session.add(Warehouse(branch_id=branch.id, code="MAIN", name="Main Warehouse"))

    permissions = {}
    for code, description in PERMISSIONS:
        permission = db.session.scalar(db.select(Permission).where(Permission.code == code))
        if not permission:
            permission = Permission(code=code, description=description); db.session.add(permission)
        permissions[code] = permission

    admin_role = db.session.scalar(db.select(Role).where(Role.name == "Super Admin"))
    if not admin_role:
        admin_role = Role(name="Super Admin", description="Full system access"); db.session.add(admin_role); db.session.flush()
    admin_role.permissions = list(permissions.values())

    admin = db.session.scalar(db.select(User).where(User.username == "admin"))
    if not admin:
        admin = User(username="admin", full_name="System Administrator", branch_id=branch.id); admin.set_password(DEFAULT_ADMIN_PASSWORD); admin.roles = [admin_role]; db.session.add(admin)

    defaults = [
        (Unit, {"code": "PCS", "name_ar": "قطعة", "name_en": "Piece", "allows_decimal": False}),
        (Unit, {"code": "KG", "name_ar": "كيلوجرام", "name_en": "Kilogram", "allows_decimal": True}),
        (Unit, {"code": "G", "name_ar": "جرام", "name_en": "Gram", "allows_decimal": True}),
        (Unit, {"code": "LTR", "name_ar": "لتر", "name_en": "Liter", "allows_decimal": True}),
    ]
    for model, values in defaults:
        if not db.session.scalar(db.select(model).where(model.code == values["code"])): db.session.add(model(**values))
    if not db.session.scalar(db.select(Category).where(Category.code == "GENERAL")):
        db.session.add(Category(code="GENERAL", name_ar="عام", name_en="General"))
    if not db.session.scalar(db.select(Brand).where(Brand.code == "GENERIC")):
        db.session.add(Brand(code="GENERIC", name_ar="عام", name_en="Generic"))
    db.session.commit()
    print("Seed completed. Initial admin: admin / ChangeMe123!")
