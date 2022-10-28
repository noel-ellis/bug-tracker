from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, models, utils, oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm


router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        user = db.query(models.User).filter(models.User.username == user_credentials.username).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    access_token = oauth2.create_access_token(data = {"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
    
# Create a new user
@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user_info: schemas.RequestUserSignup, db: Session = Depends(get_db)):
    
    # Hash the password and store it in user_info
    hashed_pwd = utils.hash(user_info.password)
    user_info.password = hashed_pwd

    user = models.User(**user_info.dict())
    
    # A way to create the first admin account
    if user.username == 'admin':
        user.access = 'admin'

    db.add(user)
    db.commit()
    db.refresh(user)

    return user