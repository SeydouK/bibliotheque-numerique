import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import pickle, os, yaml

CLEAN_DATA_PATH = os.getenv("CLEAN_DATA_PATH", "data/loans_clean.csv")
MODEL_PATH      = os.getenv("MODEL_PATH",      "data/model.pkl")
PARAMS_PATH     = "dvc_pipeline/params.yaml"

def train():
    os.makedirs("data", exist_ok=True)

    with open(PARAMS_PATH) as f:
        params = yaml.safe_load(f)["model"]

    print(f"Paramètres : {params}")

    df = pd.read_csv(CLEAN_DATA_PATH)
    print(f"Données chargées : {len(df)} lignes")

    pivot = df.pivot_table(
        index="user_id",
        columns="livre_id",
        aggfunc="size",
        fill_value=0
    )
    print(f"Matrice : {pivot.shape[0]} users × {pivot.shape[1]} livres")

    matrix = csr_matrix(pivot.values)

    model = NearestNeighbors(
        n_neighbors=params["n_neighbors"],
        metric=params["metric"],
        algorithm=params["algorithm"]
    )
    model.fit(matrix)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "pivot": pivot}, f)

    print(f"Modèle sauvegardé → {MODEL_PATH}")

if __name__ == "__main__":
    train()