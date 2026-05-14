import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.preprocessing import StandardScaler

DATA_PATH = "E:/Data Science Study/Project/Data Science/Autonomous Fraud Investigation Agentic AI System/data/raw/paysim.csv"

def main():
    print("Loading PaySim dataset...")
    df = pd.read_csv(DATA_PATH)

    # Use relevant features
    features = [
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest"
    ]

    # Only keep TRANSFER and CASH_OUT (fraud-relevant types)
    df = df[df["type"].isin(["TRANSFER", "CASH_OUT"])]

    X = df[features]
    y = df["isFraud"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.3,
        random_state=42,
        stratify=y
    )

    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Logistic Regression
    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)

    print("\n==============================")
    print(" BASELINE LOGISTIC RESULTS")
    print("==============================")
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F1-score: {f1:.3f}")
    print(f"Accuracy: {acc:.3f}")
    print("==============================")

if __name__ == "__main__":
    main()