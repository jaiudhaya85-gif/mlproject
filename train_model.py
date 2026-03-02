# train_model.py
import random
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from joblib import dump
from datetime import datetime, timedelta

# Synthetic dataset generator
def generate_synthetic_data(n=2000, seed=42):
    random.seed(seed)
    rows = []
    for _ in range(n):
        # features:
        # failed_5min: number of failed attempts in last 5 minutes (0-6)
        failed_5min = random.choices([0,1,2,3,4,5,6], weights=[40,25,15,8,6,4,2])[0]
        # hour_of_day: 0-23
        hour = random.randint(0,23)
        # ip_change_flag: 1 if login IP changed recently (0/1)
        ip_change = random.choices([0,1], weights=[85,15])[0]
        # rapid_attempts: average attempts per minute recently (0-10)
        rapid = random.choices(range(0,11), weights=[40,25,15,8,5,3,2,1,1,0,0])[0]
        # label: suspicious if failed_5min >=3 or ip_change==1 and hour in odd hours etc.
        suspicious = 1 if (failed_5min >= 3 or (ip_change==1 and hour in [0,1,2,3,4])) else 0

        rows.append([failed_5min, hour, ip_change, rapid, suspicious])

    df = pd.DataFrame(rows, columns=["failed_5min", "hour", "ip_change", "rapid", "label"])
    return df

def train_and_save(path="rf_model.joblib"):
    df = generate_synthetic_data(4000)
    X = df[["failed_5min", "hour", "ip_change", "rapid"]]
    y = df["label"]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    dump(model, path)
    print(f"Model trained and saved to {path}")

if __name__ == "__main__":
    train_and_save()
