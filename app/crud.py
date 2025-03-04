from sqlalchemy.orm import Session
from . import models, schemas
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a new user
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email, password=user.password, phone=user.phone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get user by email
def get_user_by_email(db: Session, email: str):
    try:
        return db.query(models.User).filter(models.User.email == email).first()
    except Exception as e:
        raise

# Create a new alert
def create_alert(db: Session, alert: schemas.AlertCreate, user_id: int):
    db_alert = models.Alert(**alert.model_dump(), user_id=user_id)
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

# Get alerts by user_id
def get_alerts_by_user_id(db: Session, user_id: int):
    return db.query(models.Alert).filter(models.Alert.user_id == user_id).all()

# Update an alert
def update_alert(db: Session, db_alert: models.Alert):
    try:
        db.commit()
        db.refresh(db_alert)
        return db_alert
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
        raise

# Delete an alert
def delete_alert(db: Session, alert_id: int):
    try:
        db_alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
        db.delete(db_alert)
        db.commit() 
        return db_alert
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
        raise

# get all users
def _get_all_users(db: Session):
    return db.query(models.User).all()