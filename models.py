# models.py
from extensions import db
from datetime import datetime

# ---------------- User Model ----------------
class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"

# ---------------- Alert Model ----------------
class Alert(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=True)        # Who triggered it
    alert_type = db.Column(db.String(50), nullable=True)      # e.g., "failed_login"
    description = db.Column(db.String(200), nullable=True)
    severity = db.Column(db.String(20), default="medium")     # low / medium / high
    is_resolved = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Alert {self.alert_type} by {self.username}>"

# ---------------- LoginHistory Model ----------------
class LoginHistory(db.Model):
    __tablename__ = "login_history"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)       # User who tried login
    status = db.Column(db.String(20), nullable=False)         # "success" / "failed"
    ip_address = db.Column(db.String(45), nullable=True)      # Optional IP tracking
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LoginHistory {self.username} - {self.status}>"
