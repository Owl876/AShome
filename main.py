from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from fastapi import Form

# Создание таблиц
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/register/")
def register(username: str, password: str, db: Session = Depends(get_db)):
    user = models.User(username=username, password=password)  # Здесь можно добавить хеширование пароля
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/send/")
def send_message(user_id: int, content: str, db: Session = Depends(get_db)):
    message = models.Message(user_id=user_id, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message



@app.post("/register/")
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = models.User(username=username, password=password)  # Хешируйте пароль перед сохранением
    db.add(user)
    db.commit()
    db.refresh(user)
    return templates.TemplateResponse("index.html", {"request": request, "message": "Пользователь зарегистрирован!"})

@app.post("/send/")
def send_message(content: str = Form(...), db: Session = Depends(get_db)):
    user_id = 1  # Замените на логику получения ID текущего пользователя
    message = models.Message(user_id=user_id, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return templates.TemplateResponse("index.html", {"request": request, "message": "Сообщение отправлено!"})

