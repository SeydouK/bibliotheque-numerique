import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import pickle, os

MODEL_PATH = os.getenv("MODEL_PATH", "model.pkl")
DATA_PATH  = os.getenv("DATA_PATH",  "loans.csv")

def train_from_file(path: str):
    df = pd.read_csv(path)
    pivot = df.pivot_table(index="user_id", columns="livre_id", aggfunc="size", fill_value=0)
    matrix = csr_matrix(pivot.values)
    model = NearestNeighbors(metric="cosine", algorithm="brute")
    model.fit(matrix)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "pivot": pivot}, f)
    print(f"Modèle sauvegardé → {MODEL_PATH}")
    return pivot

def generate_dummy_data():
    """Génère des données fictives pour l'entraînement initial."""
    np.random.seed(42)
    rows = []
    for user_id in range(1, 21):
        nb_livres = np.random.randint(2, 6)
        livre_ids = np.random.choice(range(1, 16), nb_livres, replace=False)
        for livre_id in livre_ids:
            rows.append({"user_id": user_id, "livre_id": int(livre_id)})
    df = pd.DataFrame(rows)
    df.to_csv(DATA_PATH, index=False)
    print(f"Données fictives générées → {DATA_PATH}")
    return df

if __name__ == "__main__":
    if not os.path.exists(DATA_PATH):
        generate_dummy_data()
    train_from_file(DATA_PATH)