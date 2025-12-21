import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# CONFIG
DATA = "cleaned_data.xlsx"
SEED = 42
K = 3
FEATURES = ["StudyHours","SleepHours","SocialMedia","Exercise"]

sns.set()

# 1) Load & validate
df = pd.read_excel(DATA, engine="openpyxl")
missing = [c for c in FEATURES if c not in df.columns]
if missing:
    raise SystemExit(f"Missing columns: {missing}")

X = df[FEATURES].copy()

# 2) Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3) KMeans (k=3)
kmeans = KMeans(n_clusters=K, random_state=SEED, n_init=10)
labels = kmeans.fit_predict(X_scaled)
df["Cluster"] = labels
df.to_csv("kmeans_clusters.csv", index=False)

# 4) Centers (back to original scale)
centers = scaler.inverse_transform(kmeans.cluster_centers_)
center_df = pd.DataFrame(centers, columns=FEATURES)
center_df.to_csv("cluster_centers.csv", index=False)
print("Cluster centers:\n", center_df)

# 5) Simple center bar plot (one visual)
center_df.plot(kind="bar", figsize=(6,4))
plt.xticks(range(K), [f"Cluster {i}" for i in range(K)])
plt.ylabel("Value (original scale)")
plt.title("Cluster Centers")
plt.tight_layout(); plt.savefig("cluster_centers.png"); plt.show(); plt.close()
