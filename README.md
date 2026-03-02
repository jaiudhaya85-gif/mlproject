Here’s a clean, professional **README.md** you can directly paste into your project.

---

# 🔐 ML-Powered Login Anomaly Detection System

A security monitoring system that detects suspicious login activity using a hybrid approach of rule-based detection and machine learning. The system also includes a honeypot mechanism (honeyfile) to monitor unauthorized file access.

---

## 📌 Overview

This project is a **real-time login monitoring and anomaly detection system** built using Flask and Random Forest (scikit-learn).

It tracks user login behavior and detects anomalies such as:

* Multiple failed login attempts
* Rapid login retries
* Suspicious IP changes
* Unusual login times
* Honeyfile tampering

The system generates alerts and provides an admin dashboard for monitoring security events.

---

## 🚀 Key Features

* ✅ User Registration & Authentication
* ✅ JWT-based secure authentication
* ✅ Rule-based suspicious activity detection
* ✅ Machine Learning-based anomaly detection (Random Forest)
* ✅ Alert generation and monitoring dashboard
* ✅ Login history tracking
* ✅ Honeyfile (honeypot) monitoring system
* ✅ Model retraining endpoint

---

## 🏗️ System Architecture

```
User Login Request
        ↓
Flask Backend (/login endpoint)
        ↓
Feature Extraction
        ↓
Rule-Based Detection (3+ failures in 5 min)
        ↓
ML Model Prediction (Random Forest)
        ↓
Store Alerts + Login History in MySQL
        ↓
Return JWT Token (if successful)
```

---

## 🛠️ Tech Stack

| Layer               | Technology                   |
| ------------------- | ---------------------------- |
| Backend             | Flask (Python)               |
| Database            | MySQL                        |
| ORM                 | SQLAlchemy                   |
| Authentication      | Flask-JWT-Extended           |
| ML Model            | Random Forest (scikit-learn) |
| Model Serialization | Joblib                       |
| Monitoring          | Custom Honeyfile Script      |

---

## 📂 Project Structure

```
mlproject/
│
├── app.py                  # Main Flask application
├── models.py               # Database models (User, Alert, LoginHistory)
├── extensions.py           # Database initialization
├── train_model.py          # ML training pipeline
├── honeyfile_monitor.py    # Honeyfile monitoring script
├── rf_model.joblib         # Pre-trained ML model
├── requirements.txt        # Dependencies
├── templates/              # Frontend HTML files
├── static/                 # Static assets
└── .gitignore
```

---

## 🧠 Machine Learning Model

* **Algorithm**: Random Forest Classifier (100 trees)
* **Input Features**:

  * Failed login attempts in last 5 minutes
  * Current hour of login
  * IP address change detection
  * Rapid login attempts (1-minute window)
* **Output**:

  * 0 → Normal login
  * 1 → Suspicious login

The model is trained using simulated login patterns and can be retrained using the `/retrain-model` endpoint.

---

## 🗄️ Database Schema

### 1️⃣ Users Table

* id
* username
* password_hash

### 2️⃣ LoginHistory Table

* id
* user_id
* timestamp
* status (success/failed)
* ip_address

### 3️⃣ Alerts Table

* id
* user_id
* alert_type
* severity
* timestamp
* is_resolved

---

## 🔌 API Endpoints

| Method | Endpoint               | Description                           |
| ------ | ---------------------- | ------------------------------------- |
| POST   | /register              | Register new user                     |
| POST   | /login                 | Authenticate user + anomaly detection |
| GET    | /alerts                | View all alerts (JWT required)        |
| GET    | /login-history         | View user login history               |
| GET    | /alerts-summary        | Alert statistics                      |
| GET    | /failed-logins-summary | Failed login stats                    |
| POST   | /manual-alert          | Create manual alert                   |
| POST   | /retrain-model         | Retrain ML model                      |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```
git clone <repository-url>
cd mlproject
```

### 2️⃣ Create Virtual Environment

```
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file:

```
DATABASE_URL=mysql+pymysql://root:root@localhost/mini_project_db
JWT_SECRET_KEY=your_secret_key_here
```

### 5️⃣ Run Application

```
python app.py
```

Server will start at:

```
http://127.0.0.1:5000
```

---

## 🍯 Honeyfile Monitoring

The project includes a decoy file (`honeyfile.txt`).

The `honeyfile_monitor.py` script monitors unauthorized access attempts and generates alerts.

Run it separately:

```
python honeyfile_monitor.py
```

---

## 🔐 Security Measures

* Password hashing using Werkzeug
* JWT-based authentication
* Hybrid rule-based + ML detection
* Login history tracking
* Honeyfile trap monitoring

---

## ⚠️ Limitations

* Model trained on simulated data
* No production-grade rate limiting (can be added)
* Hardening required for production deployment
* Designed for academic demonstration purposes

---

## 🔮 Future Improvements

* Use real login data for training
* Implement anomaly detection models (Isolation Forest)
* Add rate limiting
* Deploy using Docker
* Integrate centralized logging
* Add email/SMS alert notifications

---

## 👨‍💻 Author

Developed as a Mini Project for demonstrating Machine Learning-based Security Monitoring.
