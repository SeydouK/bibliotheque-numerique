from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import pandas as pd
import numpy as np
import pickle, os, requests
from train import train_from_file, generate_dummy_data, MODEL_PATH, DATA_PATH

app = FastAPI(title="Service Recommandation")

EMPRUNTS_URL = os.getenv("EMPRUNTS_URL", "http://emprunts:8003")


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Modèle non trouvé. Lancez POST /train d'abord.")
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


@app.on_event("startup")
def startup():
    if not os.path.exists(MODEL_PATH):
        print("Pas de modèle trouvé — entraînement initial avec données fictives...")
        if not os.path.exists(DATA_PATH):
            generate_dummy_data()
        train_from_file(DATA_PATH)

@app.get("/recommendations/{user_id}")
def recommend(user_id: int, n: int = 5):
    try:
        data = load_model()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    model  = data["model"]
    pivot  = data["pivot"]

    if user_id not in pivot.index:
        top = pivot.sum(axis=0).nlargest(n).index.tolist()
        return {"user_id": user_id, "recommandations": top, "methode": "populaires"}

    user_idx   = pivot.index.get_loc(user_id)
    user_vec   = pivot.iloc[user_idx].values.reshape(1, -1)
    distances, indices = model.kneighbors(user_vec, n_neighbors=min(6, len(pivot)))

    deja_lus   = set(pivot.columns[pivot.iloc[user_idx] > 0])
    suggestions = []

    for idx in indices.flatten()[1:]:
        livres_voisin = set(pivot.columns[pivot.iloc[idx] > 0])
        for livre in livres_voisin - deja_lus:
            if livre not in suggestions:
                suggestions.append(int(livre))
        if len(suggestions) >= n:
            break

    return {"user_id": user_id, "recommandations": suggestions[:n], "methode": "knn"}


@app.post("/train")
def train(background_tasks: BackgroundTasks):
    """Ré-entraîne le modèle à partir des emprunts réels ou de données fictives."""
    background_tasks.add_task(_do_train)
    return {"message": "Entraînement lancé en arrière-plan"}


def _do_train():
    try:
        resp = requests.get(f"{EMPRUNTS_URL}/emprunts/export/csv", timeout=5)
        if resp.status_code == 200 and resp.text.strip():
            with open(DATA_PATH, "w") as f:
                f.write(resp.text)
            print("Données réelles récupérées depuis le service emprunts.")
        else:
            raise ValueError("Export vide")
    except Exception as e:
        print(f"Impossible de récupérer les emprunts réels ({e}) → données fictives.")
        if not os.path.exists(DATA_PATH):
            generate_dummy_data()

    train_from_file(DATA_PATH)


@app.get("/health")
def health():
    model_ok = os.path.exists(MODEL_PATH)
    return {"status": "ok", "model_loaded": model_ok}