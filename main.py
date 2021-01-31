from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.functions import func
from models import Token
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db_conf import SessionLocal, engine
import models
import uuid
import datetime

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schema

# Token deletion


def delete_token_five_min(db: Session):
    not_alive_tokens = db.query(Token).filter(Token.is_assigned == False).all()
    for nat in not_alive_tokens:
        creation_time = nat.created_at.replace(microsecond=0)
        current_time = datetime.datetime.now().replace(microsecond=0)
        if current_time > (creation_time + datetime.timedelta(minutes=5)):
            db.delete(nat)
            db.commit()
        else:
            pass

# Token Release


def release_token_in_sixty_sec(db: Session):
    alive_tokens = db.query(Token).filter(Token.is_assigned == True).all()
    for at in alive_tokens:
        assign_at = at.assign_at.replace(microsecond=0)
        current_time = datetime.datetime.now().replace(microsecond=0)
        if current_time > (assign_at + datetime.timedelta(minutes=1)):
            at.is_assigned = False
            at.assign_at = datetime.datetime.now()
            db.add(at)
            db.commit()
        else:
            pass

# API Routes


@app.get("/")
def home():
    return {"app_details": "This is a Python Token Problem API build with FastAPI"}


@ app.post("/generate_token")
def generate_token(db: Session = Depends(get_db)):
    """
    This Api Route will Generate a Random Token on Every Request
    """
    release_token_in_sixty_sec(db)
    delete_token_five_min(db)
    token = uuid.uuid4()
    token_obj = Token(token_name=str(token), is_assigned=False)
    db.add(token_obj)
    db.commit()
    token_obj.token_name = f'{token}---{token_obj.id}'
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return token_obj


@ app.put("/assign_token")
def assign_token(db: Session = Depends(get_db)):
    """
    This Api route Assign a Token
    """
    release_token_in_sixty_sec(db)
    delete_token_five_min(db)
    if db.query(Token).filter(Token.is_assigned == False).count() > 0:
        token = db.query(Token).filter(Token.is_assigned == False).first()
        token.is_assigned = True
        token.assign_at = datetime.datetime.now()
        db.add(token)
        db.commit()
        last_obj = db.query(Token).get(token.id)
        return {
            "status": "token assigned successfully",
            "assigned_token": last_obj
        }
    else:
        raise HTTPException(
            status_code=404, detail="no token available to assign")


@ app.put("/unassign_token")
def unassign_token(db: Session = Depends(get_db)):
    """
    This Api route unassign a Token
    """
    release_token_in_sixty_sec(db)
    delete_token_five_min(db)
    if db.query(Token).filter(Token.is_assigned == True).count() > 0:
        token = db.query(Token).filter(Token.is_assigned == True).first()
        token.is_assigned = False
        db.add(token)
        db.commit()
        last_obj = db.query(Token).get(token.id)
        return {
            "status": "token unassigned successfully",
            "unassigned_token": last_obj
        }
    else:
        raise HTTPException(
            status_code=404, detail="no token available to unassign")


@ app.delete("/delete_token/{token_id}")
def delete_token(token_id: int, db: Session = Depends(get_db)):
    """
    This Api route delete a Token with provided id
    """
    release_token_in_sixty_sec(db)
    delete_token_five_min(db)
    token_obj_count = db.query(Token).filter(Token.id == int(token_id)).count()
    if token_obj_count > 0:
        token_obj = db.query(Token).get(int(token_id))
        print(token_obj)
        db.delete(token_obj)
        db.commit()
        return {
            "deletion successful": f'token id {token_id} deleted successfully'
        }
    else:
        raise HTTPException(
            status_code=404, detail=f'no token found with the id {token_id}, please check and try again')


@ app.put("/keep_alive/{token_id}")
def keep_alive(token_id: int, db: Session = Depends(get_db)):
    """
    This Api route keep a token alive for a minute
    """
    release_token_in_sixty_sec(db)
    delete_token_five_min(db)
    token_not_alive = db.query(Token).filter(
        Token.is_assigned == False).all()
    token_obj = db.query(Token).get(int(token_id))
    if token_obj:
        token_obj.is_assigned = True
        token_obj.assign_at = datetime.datetime.now()
        db.add(token_obj)
        db.commit()
        token_alive_obj = db.query(Token).get(token_id)
        return {
            "message": f'keep alive request set for token id {token_id}',
            "alive_token": token_alive_obj
        }

    else:
        raise HTTPException(
            status_code=404, detail=f'requested token with the id {token_id} is not available, please check and try again')
