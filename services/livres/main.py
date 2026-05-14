from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Optional
import time, os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin123@db:5432/bibliotheque")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class LivreDB(Base):
    __tablename__ = "livres"
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, nullable=False)
    auteur = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    disponible = Column(Boolean, default=True)
    genre = Column(String)

@asynccontextmanager
async def lifespan(app: FastAPI):
    for i in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            print("Tables livres créées.")
            break
        except Exception as e:
            print(f"DB pas prête, retry {i+1}/10...")
            time.sleep(3)
    yield

app = FastAPI(title="Service Livres", lifespan=lifespan)

class LivreCreate(BaseModel):
    titre: str
    auteur: str
    isbn: str
    genre: Optional[str] = None

class LivreUpdate(BaseModel):
    titre: Optional[str] = None
    auteur: Optional[str] = None
    genre: Optional[str] = None
    disponible: Optional[bool] = None

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