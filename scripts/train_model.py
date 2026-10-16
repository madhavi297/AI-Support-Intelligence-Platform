"""
Training and evaluation script for ticket classification model.
Uses Scikit-learn Pipeline with TF-IDF Vectorizer and Logistic Regression.
Saves model artifact to models/classifier.joblib and metrics to models/metrics.json.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "sample_tickets.csv"
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "classifier.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"


def train_classifier():
    print(f"Loading dataset from: {DATA_PATH}")
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} sample tickets.")
    print("Class distribution:")
    print(df["category"].value_counts())

    # Feature representation: combine title and description
    X = df["title"] + " " + df["description"]
    y = df["category"]

    # Stratified Train/Test split to prevent data leakage and preserve class distribution
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    print(f"\nTraining set size: {len(X_train)} | Test set size: {len(X_test)}")

    # Build Pipeline: TF-IDF n-grams + Logistic Regression
    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words="english",
                sublinear_tf=True,
                min_df=1
            )
        ),
        (
            "clf",
            LogisticRegression(
                C=5.0,
                max_iter=300,
                random_state=42
            )
        )
    ])

    print("\nFitting model pipeline on training set...")
    pipeline.fit(X_train, y_train)

    print("Evaluating model pipeline on unseen test set...")
    y_pred = pipeline.predict(X_test)

    # Compute metrics
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    labels = sorted(list(y.unique()))
    cm = confusion_matrix(y_test, y_pred, labels=labels)

    print("\n" + "="*50)
    print(f"TEST ACCURACY: {acc:.4f} ({acc*100:.1f}%)")
    print("="*50)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    print("\nConfusion Matrix (Labels: " + ", ".join(labels) + "):")
    print(cm)

    # Ensure models directory exists
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Save model artifact
    joblib.dump(pipeline, MODEL_PATH)
    print(f"\nSaved model artifact to: {MODEL_PATH}")

    # Prepare metrics payload for dashboard & API audit
    metrics_payload = {
        "accuracy": float(acc),
        "total_samples": int(len(df)),
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "classes": labels,
        "classification_report": report,
        "confusion_matrix": cm.tolist()
    }

    with open(METRICS_PATH, "w") as f:
        json.dump(metrics_payload, f, indent=2)

    print(f"Saved evaluation metrics to: {METRICS_PATH}")
    return pipeline, metrics_payload


if __name__ == "__main__":
    train_classifier()
