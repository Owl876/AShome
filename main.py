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

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
    return templates.TemplateResponse("index.html", {"request": request, "message": "Пользователь зарегистрирован!"})

@app.post("/send/")
def send_message(
        request: Request,
        content: str = Form(...),
        db: Session = Depends(get_db)
):
    user_id = 1  # Замените на логику получения ID текущего пользователя
    message = models.Message(user_id=user_id, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return templates.TemplateResponse("index.html", {"request": request, "message": "Сообщение отправлено!"})


@app.get("/register/", response_class=HTMLResponse)
def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login/", response_class=HTMLResponse)
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login/")
def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user and pwd_context.verify(password, user.password):
        # Здесь вы можете сохранить информацию о пользователе в сессии или токене
        return templates.TemplateResponse("messenger.html", {"request": request, "user": user.username})
    raise HTTPException(status_code=400, detail="Неверные имя пользователя или пароль")

