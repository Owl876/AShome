from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import engine, get_db
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(password)
    user = models.User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"msg": "User created"}

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"msg": "Login successful", "user_id": user.id}

@app.post("/send_message")
def send_message(sender_id: int, recipient_id: int, content: str, db: Session = Depends(get_db)):
    message = models.Message(sender_id=sender_id, recipient_id=recipient_id, message_content=content, timestamp="now")
    db.add(message)
    db.commit()
    return {"msg": "Message sent"}

@app.get("/messages")
def get_messages(user_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(models.Message.recipient_id == user_id).all()
    return messages
