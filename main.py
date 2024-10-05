from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

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

# Инициализация хешера паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/register/", response_class=HTMLResponse)
def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register/")
def register(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    hashed_password = pwd_context.hash(password)  # Хешируем пароль
    user = models.User(username=username, hashed_password=hashed_password)  # Измените здесь
    db.add(user)
    db.commit()
    db.refresh(user)
    return templates.TemplateResponse("login.html", {"request": request, "message": "Пользователь зарегистрирован!"})

@app.post("/send/")
def send_message(
        request: Request,
        recipient_id: int = Form(...),  # Получаем ID получателя
        content: str = Form(...),
        db: Session = Depends(get_db)
):
    user_id = 1  # Здесь вы должны использовать ID текущего пользователя
    message = models.Message(sender_id=user_id, recipient_id=recipient_id, message_content=content)  # Используем новые поля
    db.add(message)
    db.commit()
    db.refresh(message)
    return templates.TemplateResponse("messenger.html", {"request": request, "message": "Сообщение отправлено!"})

@app.get("/messenger/", response_class=HTMLResponse)
def get_messenger(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).all()  # Получаем всех пользователей
    return templates.TemplateResponse("messenger.html", {"request": request, "users": users})


@app.get("/register/", response_class=HTMLResponse)
def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login/", response_class=HTMLResponse)
def get_login(request: Request):
    return templates.TemplateResponse("messenger.html", {"request": request})

@app.post("/login/")
def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user and pwd_context.verify(password, user.hashed_password):  # Используем hashed_password
        # Здесь вы можете сохранить информацию о пользователе в сессии или токене
        return templates.TemplateResponse("messenger.html", {"request": request, "user": user.username})
    raise HTTPException(status_code=400, detail="Неверные имя пользователя или пароль")


