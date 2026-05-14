from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional
from fastapi.responses import StreamingResponse
import time, os, csv, io

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin123@db:5432/bibliotheque")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class EmpruntDB(Base):
    __tablename__ = "emprunts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    livre_id = Column(Integer, nullable=False)
    date_emprunt = Column(DateTime, default=datetime.utcnow)
    date_retour_prevue = Column(DateTime)
    date_retour_effective = Column(DateTime, nullable=True)
    retourne = Column(Boolean, default=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    for i in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            print("Tables emprunts créées.")
            break
        except Exception as e:
            print(f"DB pas prête, retry {i+1}/10...")
            time.sleep(3)
    yield

app = FastAPI(title="Service Emprunts", lifespan=lifespan)

class EmpruntCreate(BaseModel):
    user_id: int
    livre_id: int
    duree_jours: int = 14

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/emprunts")
def lister(db: Session = Depends(get_db)):
    return db.query(EmpruntDB).all()

@app.post("/emprunts", status_code=201)
def emprunter(data: EmpruntCreate, db: Session = Depends(get_db)):
    emprunt = EmpruntDB(
        user_id=data.user_id,
        livre_id=data.livre_id,
        date_retour_prevue=datetime.utcnow() + timedelta(days=data.duree_jours)
    )
    db.add(emprunt)
    db.commit()
    db.refresh(emprunt)
    return emprunt

@app.put("/emprunts/{emprunt_id}/retour")
def retourner(emprunt_id: int, db: Session = Depends(get_db)):
    e = db.query(EmpruntDB).filter(EmpruntDB.id == emprunt_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé")
    e.retourne = True
    e.date_retour_effective = datetime.utcnow()
    db.commit()
    db.refresh(e)
    return e

@app.get("/emprunts/utilisateur/{user_id}")
def historique_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(EmpruntDB).filter(EmpruntDB.user_id == user_id).all()

@app.get("/emprunts/retards")
def retards(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    return db.query(EmpruntDB).filter(
        EmpruntDB.retourne == False,
        EmpruntDB.date_retour_prevue < now
    ).all()

@app.get("/emprunts/export/csv")
def export_csv(db: Session = Depends(get_db)):
    emprunts = db.query(EmpruntDB).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "user_id", "livre_id", "date_emprunt", "date_retour_prevue", "retourne"])
    for e in emprunts:
        writer.writerow([e.id, e.user_id, e.livre_id, e.date_emprunt, e.date_retour_prevue, e.retourne])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=loans.csv"})