"""
Flask backend for personal finance app (vibe-20260816-0040)
- Single file: app.py
- Stack: Flask, Flask-CORS, Flask-SQLAlchemy, PyJWT, bcrypt, python-dotenv
- Auth: JWT access token (15 min) + refresh token (7 days)
- DB: SQLite (file: finance.db)
"""

import os
import json
import datetime as dt
from functools import wraps
from typing import List, Optional

import bcrypt
import jwt
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, func, and_, or_
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound, Forbidden

# -------------------------- App & Config --------------------------

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///finance.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
app.config["JWT_ACCESS_EXPIRES"] = int(os.getenv("JWT_ACCESS_EXPIRES", 900))  # 15 min
app.config["JWT_REFRESH_EXPIRES"] = int(
    os.getenv("JWT_REFRESH_EXPIRES", 7 * 24 * 60 * 60)
)  # 7 days
app.config["CORS_ORIGINS"] = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173"
).split(",")  # Vite default

db = SQLAlchemy(app)
CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

# -------------------------- Models --------------------------

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    def set_password(self, pwd: str):
        self.password_hash = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

    def check_password(self, pwd: str) -> bool:
        return bcrypt.checkpw(pwd.encode(), self.password_hash.encode())


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(Enum("expense", "income", name="category_type"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "name", name="uq_user_category"),)


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=func.now())

    category = db.relationship("Category")


class Budget(db.Model):
    __tablename__ = "budgets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    period = db.Column(Enum("monthly", "weekly", name="budget_period"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "category_id",
            "period",
            "start_date",
            name="uq_user_budget_period",
        ),
    )
    category = db.relationship("Category")


# -------------------------- Helpers --------------------------

def create_access_token(user_id: int) -> str:
    payload = {
        "sub": user_id,
        "type": "access",
        "exp": dt.datetime.utcnow()
        + dt.timedelta(seconds=app.config["JWT_ACCESS_EXPIRES"]),
        "iat": dt.datetime.utcnow(),
    }
    return jwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")


def create_refresh_token(user_id: int) -> str:
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": dt.datetime.utcnow()
        + dt.timedelta(seconds=app.config["JWT_REFRESH_EXPIRES"]),
        "iat": dt.datetime.utcnow(),
    }
    return jwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        raise Unauthorized("Token expired")
    except jwt.InvalidTokenError:
        raise Unauthorized("Invalid token")


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise Unauthorized("Missing bearer token")
        token = auth_header.split()[1]
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise Unauthorized("Invalid token type")
        user = User.query.get(payload["sub"])
        if not user:
            raise Unauthorized("User not found")
        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper


def validate_json(schema: dict):
    """Simple schema validator: {field: (type, required)}"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True) or {}
            errors = {}
            for field, (typ, required) in schema.items():
                if required and field not in data:
                    errors[field] = "missing"
                    continue
                if field in data and not isinstance(data[field], typ):
                    errors[field] = f"expected {typ.__name__}"
            if errors:
                raise BadRequest(json.dumps(errors))
            g.validated_data = data
            return fn(*args, **kwargs)

        return wrapper

    return decorator


# -------------------------- Auth Endpoints --------------------------

@app.route("/api/auth/register", methods=["POST"])
@validate_json(
    {
        "email": (str, True),
        "password": (str, True),
    }
)
def register():
    data = g.validated_data
    if User.query.filter_by(email=data["email"].lower()).first():
        raise BadRequest("Email already registered")
    user = User(email=data["email"].lower())
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {"id": user.id, "email": user.email},
        }
    )


@app.route("/api/auth/login", methods=["POST"])
@validate_json(
    {
        "email": (str, True),
        "password": (str, True),
    }
)
def login():
    data = g.validated_data
    user = User.query.filter_by(email=data["email"].lower()).first()
    if not user or not user.check_password(data["password"]):
        raise Unauthorized("Invalid credentials")
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {"id": user.id, "email": user.email},
        }
    )


@app.route("/api/auth/refresh", methods=["POST"])
def refresh():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise Unauthorized("Missing bearer token")
    token = auth_header.split()[1]
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise Unauthorized("Invalid token type")
    new_access = create_access_token(payload["sub"])
    return jsonify({"access_token": new_access})


@app.route("/api/auth/logout", methods=["POST"])
@auth_required
def logout():
    # In a more robust setup we would token-blacklist; for simplicity just ack.
    return jsonify({"msg": "Logged out"})


# -------------------------- User --------------------------

@app.route("/api/users/me", methods=["GET"])
@auth_required
def get_me():
    return jsonify(
        {"id": g.current_user.id, "email": g.current_user.email}
    )


# -------------------------- Categories --------------------------

@app.route("/api/categories", methods=["GET"])
@auth_required
def list_categories():
    cats = Category.query.filter_by(user_id=g.current_user.id).all()
    return jsonify(
        [
            {"id": c.id, "name": c.name, "type": c.type}
            for c in cats
        ]
    )


@app.route("/api/categories", methods=["POST"])
@auth_required
@validate_json(
    {
        "name": (str, True),
        "type": (str, True),  # expense|income
    }
)
def create_category():
    data = g.validated_data
    if data["type"] not in ("expense", "income"):
        raise BadRequest("type must be 'expense' or 'income'")
    if Category.query.filter_by(
        user_id=g.current_user.id, name=data["name"]
    ).first():
        raise BadRequest("Category already exists")
    cat = Category(
        user_id=g.current_user.id,
        name=data["name"],
        type=data["type"],
    )
    db.session.add(cat)
    db.session.commit()
    return jsonify({"id": cat.id}), 201


@app.route("/api/categories/<int:cat_id>", methods=["PUT"])
@auth_required
@validate_json(
    {
        "name": (str, False),
        "type": (str, False),
    }
)
def update_category(cat_id):
    data = g.validated_data
    cat = Category.query.filter_by(
        id=cat_id, user_id=g.current_user.id
    ).first_or_404()
    if "name" in data:
        if Category.query.filter(
            Category.user_id == g.current_user.id,
            Category.name == data["name"],
            Category.id != cat_id,
        ).first():
            raise BadRequest("Category name already exists")
        cat.name = data["name"]
    if "type" in data:
        if data["type"] not in ("expense", "income"):
            raise BadRequest("type must be 'expense' or 'income'")
        cat.type = data["type"]
    db.session.commit()
    return jsonify({"id": cat.id})


@app.route("/api/categories/<int:cat_id>", methods=["DELETE"])
@auth_required
def delete_category(cat_id):
    cat = Category.query.filter_by(
        id=cat_id, user_id=g.current_user.id
    ).first_or_404()
    db.session.delete(cat)
    db.session.commit()
    return "", 204


# -------------------------- Transactions --------------------------

@app.route("/api/transactions", methods=["GET"])
@auth_required
def list_transactions():
    # Filtering via query params
    args = request.args
    q = Transaction.query.filter_by(user_id=g.current_user.id)
    if args.get("start"):
        q = q.filter(Transaction.date >= args["start"])
    if args.get("end"):
        q = q.filter(Transaction.date <= args["end"])
    if args.get("type"):
        q = q.join(Category).filter(Category.type == args["type"])
    if args.get("category_id"):
        q = q.filter(Transaction.category_id == args["category_id"])
    q = q.order_by(Transaction.date.desc())
    txns = q.all()
    return jsonify(
        [
            {
                "id": t.id,
                "amount": float(t.amount),
                "date": t.date.isoformat(),
                "description": t.description,
                "category": {
                    "id": t.category.id,
                    "name": t.category.name,
                    "type": t.category.type,
                },
            }
            for t in txns
        ]
    )


@app.route("/api/transactions", methods=["POST"])
@auth_required
@validate_json(
    {
        "amount": ( (int, float), True),
        "date": (str, True),  # YYYY-MM-DD
        "category_id": (int, True),
        "description": (str, False),
    }
)
def create_transaction():
    data = g.validated_data
    try:
        date_obj = dt.date.fromisoformat(data["date"])
    except ValueError:
        raise BadRequest("Invalid date format, expected YYYY-MM-DD")
    cat = Category.query.filter_by(
        id=data["category_id"], user_id=g.current_user.id
    ).first_or_404()
    txn = Transaction(
        user_id=g.current_user.id,
        category_id=cat.id,
        amount=data["amount"],
        date=date_obj,
        description=data.get("description"),
    )
    db.session.add(txn)
    db.session.commit()
    # Budget check (simple)
    _check_budgets(txn)
    return jsonify({"id": txn.id}), 201


@app.route("/api/transactions/<int:txn_id>", methods=["PUT"])
@auth_required
@validate_json(
    {
        "amount": ( (int, float), False),
        "date": (str, False),
        "category_id": (int, False),
        "description": (str, False),
    }
)
def update_transaction(txn_id):
    data = g.validated_data
    txn = Transaction.query.filter_by(
        id=txn_id, user_id=g.current_user.id
    ).first_or_404()
    if "amount" in data:
        txn.amount = data["amount"]
    if "date" in data:
        try:
            txn.date = dt.date.fromisoformat(data["date"])
        except ValueError:
            raise BadRequest("Invalid date format")
    if "category_id" in data:
        cat = Category.query.filter_by(
            id=data["category_id"], user_id=g.current_user.id
        ).first_or_404()
        txn.category_id = cat.id
    if "description" in data:
        txn.description = data["description"]
    db.session.commit()
    # Re-evaluate budgets
    _check_budgets(txn)
    return jsonify({"id": txn.id})


@app.route("/api/transactions/<int:txn_id>", methods=["DELETE"])
@auth_required
def delete_transaction(txn_id):
    txn = Transaction.query.filter_by(
        id=txn_id, user_id=g.current_user.id
    ).first_or_404()
    db.session.delete(txn)
    db.session.commit()
    return "", 204


def _check_budgets(txn: Transaction):
    """Update budget warnings/alerts (stub). In a full app we'd store alerts."""
    # Determine period start based on transaction date
    period_start = None
    # For simplicity we just check any budget that covers the date
    budgets = Budget.query.filter(
        Budget.user_id == g.current_user.id,
        Budget.category_id == txn.category_id,
        Budget.start_date <= txn.date,
        Budget.end_date >= txn.date,
    ).all()
    for b in budgets:
        # Sum of transactions in period for this category+user
        total = (
            db.session.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == g.current_user.id,
                Transaction.category_id == b.category_id,
                Transaction.date >= b.start_date,
                Transaction.date <= b.end_date,
            )
            .scalar()
            or 0
        )
        ratio = float(total) / float(b.amount)
        if ratio >= 1.0:
            # exceed - could fire alert
            pass
        elif ratio >= 0.8:
            # warning threshold
            pass
    # In a real implementation we would persist alerts/notifications.


# -------------------------- Budgets --------------------------

@app.route("/api/budgets", methods=["GET"])
@auth_required
def list_budgets():
    budgets = Budget.query.filter_by(user_id=g.current_user.id).all()
    return jsonify(
        [
            {
                "id": b.id,
                "amount": float(b.amount),
                "period": b.period,
                "start_date": b.start_date.isoformat(),
                "end_date": b.end_date.isoformat(),
                "category": {
                    "id": b.category.id,
                    "name": b.category.name,
                    "type": b.category.type,
                },
            }
            for b in budgets