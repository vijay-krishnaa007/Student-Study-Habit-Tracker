import os, random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
import joblib

# CONFIG
DATA = "cleaned_data.xlsx"
SEED = 42
TEST_SIZE = 0.20
FEATURES = ["StudyHours","SleepHours","SocialMedia","Exercise"]
TARGET = "AttentionLevel"

random.seed(SEED); np.random.seed(SEED)
sns.set()

# 1) Load
df = pd.read_excel(DATA, engine="openpyxl")

# 2) Validate
missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
if missing:
    raise SystemExit(f"Missing columns: {missing}")

X = df[FEATURES]
y = df[TARGET]

# 3) EDA minimal: correlation heatmap (helps show relationships)
plt.figure(figsize=(5,4))
sns.heatmap(df[FEATURES + [TARGET]].corr(), annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation (minimal)")
plt.tight_layout(); plt.savefig("correlation_heatmap.png"); plt.show(); plt.close()

# 4) Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=SEED)
pd.concat([X_train, y_train], axis=1).to_csv("train.csv", index=False)
pd.concat([X_test, y_test], axis=1).to_csv("test.csv", index=False)

# 5) Train
model = RandomForestRegressor(n_estimators=100, random_state=SEED)
model.fit(X_train, y_train)

# 6) Eval
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"R2 (test): {r2:.3f}   RMSE (test): {rmse:.3f}")

# 7) Save model
joblib.dump(model, "model.pkl")

# 8) Feature importances plot
fi = pd.DataFrame({"feature": FEATURES, "importance": model.feature_importances_}).sort_values("importance", ascending=True)
plt.figure(figsize=(5,3))
plt.barh(fi["feature"], fi["importance"])
plt.title("Feature Importances")
plt.tight_layout(); plt.savefig("feature_importances.png"); plt.show(); plt.close()

# 9) True vs Predicted plot
plt.figure(figsize=(5,4))
plt.scatter(y_test, y_pred, alpha=0.8)
mn, mx = min(min(y_test), min(y_pred)), max(max(y_test), max(y_pred))
plt.plot([mn,mx],[mn,mx], '--r')
plt.xlabel("True"); plt.ylabel("Predicted"); plt.title("True vs Pred")
plt.tight_layout(); plt.savefig("true_vs_pred.png"); plt.show(); plt.close()
