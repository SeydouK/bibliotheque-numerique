from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import enum, os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin123@db:5432/bibliotheque")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
app = FastAPI(title="Service Utilisateurs")

class TypeUtilisateur(str, enum.Enum):
    etudiant = "Étudiant"
    professeur = "Professeur"
    personnel = "Personnel"

class UtilisateurDB(Base):
    __tablename__ = "utilisateurs"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    type_utilisateur = Column(String, default="Étudiant")

Base.metadata.create_all(bind=engine)

class UtilisateurCreate(BaseModel):
    nom: str
    prenom: str
    email: str
    type_utilisateur: TypeUtilisateur = TypeUtilisateur.etudiant

class UtilisateurUpdate(BaseModel):
    nom: Optional[str]
    prenom: Optional[str]
    type_utilisateur: Optional[TypeUtilisateur]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/utilisateurs")
def lister(db: Session = Depends(get_db)):
    return db.query(UtilisateurDB).all()

@app.get("/utilisateurs/{user_id}")
def get_utilisateur(user_id: int, db: Session = Depends(get_db)):
    u = db.query(UtilisateurDB).filter(UtilisateurDB.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return u

@app.post("/utilisateurs", status_code=201)
def creer(data: UtilisateurCreate, db: Session = Depends(get_db)):
    u = UtilisateurDB(**data.dict())
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

@app.put("/utilisateurs/{user_id}")
def modifier(user_id: int, data: UtilisateurUpdate, db: Session = Depends(get_db)):
    u = db.query(UtilisateurDB).filter(UtilisateurDB.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(u, k, v)
    db.commit()
    db.refresh(u)
    return u

@app.delete("/utilisateurs/{user_id}")
def supprimer(user_id: int, db: Session = Depends(get_db)):
    u = db.query(UtilisateurDB).filter(UtilisateurDB.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    db.delete(u)
    db.commit()
    return {"message": "Utilisateur supprimé"}

@app.get("/utilisateurs/type/{type_u}")
def par_type(type_u: str, db: Session = Depends(get_db)):
    return db.query(UtilisateurDB).filter(UtilisateurDB.type_utilisateur == type_u).all()