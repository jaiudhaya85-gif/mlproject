# app.py
from flask import render_template
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Alert, LoginHistory
from datetime import datetime, timedelta
from sqlalchemy import func
from flask_cors import CORS

# ML imports
from joblib import load
import os

# Path to saved model
MODEL_PATH = "rf_model.joblib"

app = Flask(__name__)
CORS(app)   # allow requests from browser (dev only)

# ---------- MySQL DATABASE CONFIG ----------
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/mini_project_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key"

db.init_app(app)
jwt = JWTManager(app)

# Load ML model if exists
ml_model = None
if os.path.exists(MODEL_PATH):
    try:
        ml_model = load(MODEL_PATH)
        print("✅ ML model loaded from", MODEL_PATH)
    except Exception as e:
        print("⚠️ Failed loading ML model:", e)
else:
    print("⚠️ ML model not found. Run train_model.py to create rf_model.joblib")

# ✅ Create tables if they don’t exist
with app.app_context():
    db.create_all()

# Utility: feature extraction for ML prediction
def extract_features_for_user(username):
    """
    Build simple features from recent login history:
    - failed_5min: number of failed attempts in last 5 minutes
    - hour: current hour of day (0-23)
    - ip_change: 1 if same user had different IPs in last 10 attempts (simple proxy)
    - rapid: number of attempts in last 1 minute
    """
    now = datetime.utcnow()
    five_min_ago = now - timedelta(minutes=5)
    one_min_ago = now - timedelta(minutes=1)
    last_10 = LoginHistory.query.filter_by(username=username).order_by(LoginHistory.timestamp.desc()).limit(10).all()
    recent_5 = LoginHistory.query.filter(LoginHistory.username==username, LoginHistory.timestamp >= five_min_ago).all()
    recent_1 = LoginHistory.query.filter(LoginHistory.username==username, LoginHistory.timestamp >= one_min_ago).all()

    failed_5min = sum(1 for r in recent_5 if r.status == "failed")
    hour = now.hour
    ips = [r.ip_address for r in last_10 if r.ip_address]
    ip_change = 1 if len(set(ips)) > 1 else 0
    rapid = len(recent_1)

    return [failed_5min, hour, ip_change, rapid]

# -------- Authentication --------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    hashed_pw = generate_password_hash(data["password"])
    new_user = User(username=data["username"], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User registered"}), 201

# -------- Login --------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    ip_addr = request.remote_addr

    user = User.query.filter_by(username=username).first()

    # --- Case 1: invalid user or wrong password ---
    if not user or not check_password_hash(user.password, password):
        history = LoginHistory(username=username, status="failed", ip_address=ip_addr, timestamp=datetime.utcnow())
        db.session.add(history)

        alert = Alert(
            username=username,
            alert_type="failed_login",
            description="Failed login attempt",
            timestamp=datetime.utcnow()
        )
        db.session.add(alert)

        # suspicious activity check (rule-based)
        five_min_ago = datetime.utcnow() - timedelta(minutes=5)
        recent_fails = LoginHistory.query.filter(
            LoginHistory.username == username,
            LoginHistory.status == "failed",
            LoginHistory.timestamp >= five_min_ago
        ).count()

        if recent_fails >= 3:
            susp_alert = Alert(
                username=username,
                alert_type="suspicious_activity",
                description=f"Suspicious activity: {recent_fails} failed logins in 5 min",
                timestamp=datetime.utcnow()
            )
            db.session.add(susp_alert)

        # ML check (if model loaded) — optional secondary check
        if ml_model is not None:
            features = extract_features_for_user(username)
            try:
                pred = ml_model.predict([features])[0]
                if pred == 1:
                    ml_alert = Alert(
                        username=username,
                        alert_type="ml_suspicious",
                        description=f"ML flagged suspicious login (features={features})",
                        timestamp=datetime.utcnow(),
                        severity="high"
                    )
                    db.session.add(ml_alert)
            except Exception as e:
                print("ML prediction error:", e)

        db.session.commit()
        return jsonify({"msg": "Invalid username or password"}), 401

    # --- Case 2: success login ---
    history = LoginHistory(username=username, status="success", ip_address=ip_addr, timestamp=datetime.utcnow())
    db.session.add(history)

    alert = Alert(
        username=username,
        alert_type="login",
        description="Successful login",
        timestamp=datetime.utcnow()
    )
    db.session.add(alert)

    # ML check on success as well to detect anomalous success logins
    if ml_model is not None:
        features = extract_features_for_user(username)
        try:
            pred = ml_model.predict([features])[0]
            if pred == 1:
                ml_alert = Alert(
                    username=username,
                    alert_type="ml_suspicious",
                    description=f"ML flagged suspicious login after success (features={features})",
                    timestamp=datetime.utcnow(),
                    severity="high"
                )
                db.session.add(ml_alert)
        except Exception as e:
            print("ML prediction error:", e)

    db.session.commit()

    token = create_access_token(identity=username)
    return jsonify({"token": token, "msg": "Login success"}), 200

# -------- Alerts --------
@app.route("/alerts", methods=["GET"])
@jwt_required()
def get_alerts():
    alerts = Alert.query.order_by(Alert.timestamp.desc()).all()
    return jsonify([
        {
            "id": a.id,
            "username": a.username,
            "alert_type": a.alert_type,
            "description": a.description,
            "severity": a.severity,
            "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for a in alerts
    ]), 200

# -------- Create Manual Alert --------
# -------- Manual Alert --------
@app.route("/manual-alert", methods=["POST"])
@jwt_required()
def manual_alert():
    data = request.json

    alert = Alert(
        username=data.get("username"),
        alert_type=data.get("alert_type"),
        description=data.get("description"),
        timestamp=datetime.utcnow()
    )

    db.session.add(alert)
    db.session.commit()

    return jsonify({"msg": "Manual alert created"}), 201


# -------- Login History --------
@app.route("/login-history", methods=["GET"])
@jwt_required()
def login_history():
    current_user = get_jwt_identity()
    history = LoginHistory.query.filter_by(username=current_user).all()
    return jsonify([
        {
            "username": h.username,
            "status": h.status,
            "ip_address": h.ip_address,
            "timestamp": h.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for h in history
    ]), 200

# -------- Failed Logins Summary --------
@app.route("/failed-logins-summary", methods=["GET"])
@jwt_required()
def failed_logins_summary():
    results = (
        db.session.query(LoginHistory.username, func.count(LoginHistory.id))
        .filter_by(status="failed")
        .group_by(LoginHistory.username)
        .all()
    )
    summary = [{"username": username, "failed_attempts": count} for username, count in results]
    return jsonify(summary), 200

# -------- Alerts Summary for Charts --------
@app.route("/alerts-summary", methods=["GET"])
@jwt_required()
def alerts_summary():
    results = (
        db.session.query(Alert.alert_type, func.count(Alert.id))
        .group_by(Alert.alert_type)
        .all()
    )
    summary = [{"alert_type": t, "count": c} for t, c in results]
    return jsonify(summary), 200

# -------- Retrain ML Model (optional) --------
@app.route("/retrain-model", methods=["POST"])
@jwt_required()
def retrain_model():
    """
    This endpoint will call the local train_model.py to retrain and overwrite rf_model.joblib.
    In case you want to retrain from real labeled data, modify train_model.py to consume it.
    """
    # Only allow admin usage in production; for demo, any logged-in user can call it.
    try:
        # simple direct call
        from train_model import train_and_save
        train_and_save()
        global ml_model
        from joblib import load
        ml_model = load(MODEL_PATH)
        return jsonify({"msg": "Model retrained and loaded."}), 200
    except Exception as e:
        return jsonify({"msg": f"Retrain failed: {e}"}), 500

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
