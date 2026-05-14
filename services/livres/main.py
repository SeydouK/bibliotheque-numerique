from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin123@db:5432/bibliotheque")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI(title="Service Livres")

class LivreDB(Base):
    __tablename__ = "livres"
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, nullable=False)
    auteur = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    disponible = Column(Boolean, default=True)
    genre = Column(String)

Base.metadata.create_all(bind=engine)

class LivreCreate(BaseModel):
    titre: str
    auteur: str
    isbn: str
    genre: Optional[str] = None

class LivreUpdate(BaseModel):
    titre: Optional[str]
    auteur: Optional[str]
    genre: Optional[str]
    disponible: Optional[bool]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/livres")
def lister_livres(db: Session = Depends(get_db)):
    return db.query(LivreDB).all()

@app.get("/livres/{livre_id}")
def get_livre(livre_id: int, db: Session = Depends(get_db)):
    livre = db.query(LivreDB).filter(LivreDB.id == livre_id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return livre

@app.post("/livres", status_code=201)
def ajouter_livre(livre: LivreCreate, db: Session = Depends(get_db)):
    db_livre = LivreDB(**livre.dict())
    db.add(db_livre)
    db.commit()
    db.refresh(db_livre)
    return db_livre

@app.put("/livres/{livre_id}")
def modifier_livre(livre_id: int, data: LivreUpdate, db: Session = Depends(get_db)):
    livre = db.query(LivreDB).filter(LivreDB.id == livre_id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    for key, val in data.dict(exclude_unset=True).items():
        setattr(livre, key, val)
    db.commit()
    db.refresh(livre)
    return livre

@app.delete("/livres/{livre_id}")
def supprimer_livre(livre_id: int, db: Session = Depends(get_db)):
    livre = db.query(LivreDB).filter(LivreDB.id == livre_id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    db.delete(livre)
    db.commit()
    return {"message": "Livre supprimé"}

@app.get("/livres/recherche/{terme}")
def rechercher(terme: str, db: Session = Depends(get_db)):
    results = db.query(LivreDB).filter(
        (LivreDB.titre.ilike(f"%{terme}%")) |
        (LivreDB.auteur.ilike(f"%{terme}%")) |
        (LivreDB.isbn.ilike(f"%{terme}%"))
    ).all()
    return results