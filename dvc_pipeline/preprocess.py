import pandas as pd
import numpy as np
import os, sys

DATA_PATH   = os.getenv("DATA_PATH",   "data/loans.csv")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "data/loans_clean.csv")

def generate_data():
    """Génère des données fictives si pas de données réelles."""
    print("Génération de données fictives...")
    np.random.seed(42)
    rows = []
    for user_id in range(1, 51):
        nb_livres = np.random.randint(2, 8)
        livre_ids = np.random.choice(range(1, 31), nb_livres, replace=False)
        for livre_id in livre_ids:
            rows.append({
                "user_id": user_id,
                "livre_id": int(livre_id),
                "date_emprunt": pd.Timestamp("2025-01-01") + pd.Timedelta(days=int(np.random.randint(0, 365))),
                "retourne": True
            })
    return pd.DataFrame(rows)

def preprocess():
    os.makedirs("data", exist_ok=True)

    if os.path.exists(DATA_PATH):
        print(f"Chargement depuis {DATA_PATH}...")
        df = pd.read_csv(DATA_PATH)
    else:
        df = generate_data()
        df.to_csv(DATA_PATH, index=False)
        print(f"Données sauvegardées → {DATA_PATH}")

    print(f"Données brutes : {len(df)} lignes")

    df = df.dropna(subset=["user_id", "livre_id"])
    df["user_id"]  = df["user_id"].astype(int)
    df["livre_id"] = df["livre_id"].astype(int)

    if "retourne" in df.columns:
        df = df[df["retourne"] == True]

    df = df.drop_duplicates(subset=["user_id", "livre_id"])

    print(f"Données nettoyées : {len(df)} lignes")
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Sauvegardé → {OUTPUT_PATH}")

if __name__ == "__main__":
    preprocess()