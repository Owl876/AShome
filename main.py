from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import models

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

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user_id(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")  # Читаем токен из cookies
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    return user_id


@app.get("/register/", response_class=HTMLResponse)
def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register/")
def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(password)
    user = models.User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return templates.TemplateResponse("login.html", {"request": request, "message": "Пользователь зарегистрирован!"})

@app.get("/login/", response_class=HTMLResponse)
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login/")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user and pwd_context.verify(password, user.hashed_password):
        token = jwt.encode({"sub": user.id}, "SECRET_KEY", algorithm="HS256")  # Замените на ваш секретный ключ

        # Отправляем токен в cookies для использования на других страницах
        response = templates.TemplateResponse("messenger.html", {"request": request, "user": user.username})
        response.set_cookie(key="access_token", value=token)  # Устанавливаем токен в cookies
        return response

    raise HTTPException(status_code=400, detail="Неверные имя пользователя или пароль")


@app.post("/send_message/")
def send_message(request: Request, recipient_id: int = Form(...), content: str = Form(...), db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    message = models.Message(sender_id=user_id, recipient_id=recipient_id, message_content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return {"message": "Сообщение отправлено!"}

@app.get("/messenger/", response_class=HTMLResponse)
def get_messenger(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return templates.TemplateResponse("messenger.html", {"request": request, "users": users})
