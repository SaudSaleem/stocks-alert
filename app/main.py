from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Alert
from .schemas import AlertCreate, AlertUpdate, UserCreate, UserLogin
from .tasks import fetch_all_tickers, get_ticker_by_symbol
from .crud import create_alert, get_alerts_by_user_id, update_alert, delete_alert, create_user, get_user_by_email, _get_all_users
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from .psx_scrapper import start_scheduler, stop_scheduler
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import jwt
from datetime import datetime, timedelta
from typing import Optional

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start the PSX scraper scheduler
    start_scheduler()
    yield
    # Shutdown: stop the PSX scraper scheduler
    stop_scheduler()

app = FastAPI(lifespan=lifespan)
# Global variable to store tickers
# list of dictionaries with symbol and name
tickers_cache = []
tickers_cache = fetch_all_tickers() 
# print('from main',tickers_cache)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "YOUR_SECRET_KEY"  # Change this to a secure random key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30000

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Utility function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Utility function to hash password
def get_password_hash(password):
    return pwd_context.hash(password)

# Create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
async def root():
    try:
        return {"message": "Welcome to the Stock Alert Application!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/tickers")
async def get_tickers(db: Session = Depends(get_db)):
    try:
        print('from api request received')
        print('from api',tickers_cache)
        return tickers_cache
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/tickers/{ticker}")
async def get_ticker(ticker: str):
    try:
        return get_ticker_by_symbol(ticker)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/alert")
async def create_alert_endpoint(
    alert: AlertCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    try:
        return create_alert(db, alert, user_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/alerts")
async def get_alerts_endpoint(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    try:
        return get_alerts_by_user_id(db, user_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.put("/alert")
async def update_alert_endpoint(
    alert: AlertUpdate, 
    alert_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        db_alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == current_user.id).first()
        if not db_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
            
        # Update attributes
        for key, value in alert.model_dump(exclude_unset=True).items():
            setattr(db_alert, key, value)
            
        # Let the crud function handle the commit/rollback
        return update_alert(db, db_alert)
    except Exception as e:
        # Make sure we rollback here if an error occurs before reaching crud function
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.delete("/alert")
async def delete_alert_endpoint(
    alert_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == current_user.id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
            
        # Let the crud function handle the commit/rollback
        result = delete_alert(db, alert.id)
        return {"detail": "Alert deleted successfully", "alert": result}
    except Exception as e:
        # Make sure we rollback here if an error occurs before reaching crud function
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if email already exists
        existing_user = get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash the user's password
        print('from register above', user)
        hashed_password = get_password_hash(user.password)
        user.password = hashed_password
        print('from register below', user)
        
        # Create the user
        return create_user(db, user)
    except Exception as e:
        db.rollback()
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed. Please check your input data. {str(e)}")

@app.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        print('from login above', form_data)
        # Get username from form_data (which could be an email)
        email = form_data.username
        password = form_data.password
        
        user = get_user_by_email(db, email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Return a token or user details
        return {"access_token": access_token, "token_type": "bearer", "user": user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Alternative login endpoint for JSON requests
@app.post("/login/json")
async def login_user_json(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        user = get_user_by_email(db, user_data.email)
        if not user or not verify_password(user_data.password, user.password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Return a token or user details
        return {"access_token": access_token, "token_type": "bearer", "user": user}
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"{str(e.detail)}")
    
# get all users(db)
@app.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    try:
        return _get_all_users(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
