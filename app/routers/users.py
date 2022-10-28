from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import models, schemas, oauth2
from ..database import get_db
from ..config import CHANGABLE_USER_ENTRIES
from typing import List

router = APIRouter(
    prefix='/users',
    tags=["Users"]
)

# Get all users
@router.get("/", response_model=List[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db)):

    users = db.query(models.User).all()
    return users

# Get user
@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    
    # Retieving the user
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {id} doesn't exist")

    # Retrieving all user's tickets
    tickets = db.query(models.Ticket).filter(models.Ticket.creator_id == id).all()
   
    # Retrieving all user's projects
    projects = db.query(models.Project).join(models.Personnel, models.Personnel.project_id == models.Project.id).filter(models.Personnel.user_id == id).all()
    # Retrieving all user's comments

    result = {"user": user, "tickets": tickets, "projects": projects}
    return result

# Edit user profile
@router.put("/{id}", status_code=status.HTTP_205_RESET_CONTENT, response_model=schemas.UserResponse)
def edit_user(id: str, user_request: schemas.RequestUserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    # Check if the user exists
    user_q = db.query(models.User).filter(models.User.id == id)
    user = user_q.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User (ID: {id}) doesn't exist")

    # Converting user_request to a dictionary, ignoring None values. user_request contains only values that need to be updated
    user_request = {key: val for key, val in user_request.dict().items() if val != None}

    # Making an exceptions for admins editing access type
    admin_access = False
    if current_user.access == 'admin':
        admin_access = True

    # Making sure the user edits their own profile
    if user.id != current_user.id and not admin_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Users can only edit their own profiles")
    # Preventing users from editing their own access type
    if 'access' in user_request.keys() and not admin_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can edit access type")

    # Fetching old user_data
    user_data = {col.name: getattr(user, col.name) for col in user.__table__.columns if col.name in CHANGABLE_USER_ENTRIES}

    # Creating a dictionary with the updated data. Writing old data changing only keys mentioned in user_request
    updated_data = {key: user_request.get(key, user_data[key]) for key in user_data.keys()}

    try:
        user_q.update(updated_data, synchronize_session=False)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Username or Email already exists")

    return user_q.first()

# Delete user
"""I have to logoff the user afterwords"""
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    print(current_user.id)
    
    # Retieving the user
    user_q = db.query(models.User).filter(models.User.id == id)
    user = user_q.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {id} doesn't exist")

    # CHECK IF THE USER HAS ACCESS
    # Check if the user has admin access
    if current_user.access != 'admin':
        # Check if the user selects themselves
        if id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permissions to delete user (ID:{project_id})")
    
    user_q.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Assign to one/multiple projects
"""I can use URL encoding to fetch project ids instead"""
@router.post("/{id}/assign", status_code=status.HTTP_201_CREATED)
def assign_to_project(id: int, projects: schemas.RequestProjectIds, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    # Check if the user exists
    user_q = db.query(models.User).filter(models.User.id == id)
    user = user_q.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User (ID: {id}) doesn't exist")

    # Check if projects with the specified IDs exist
    for project_id in projects.ids:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project (ID:{project_id}) doesn't exist")

    # Check if connection has already been made
    for project_id in projects.ids:
        connection = db.query(models.Personnel).filter(models.Personnel.project_id == project_id, models.Personnel.user_id == id).first()
        if connection:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'user (ID:{id}) is already assigned to the project (ID:{project.id})')

    # CHECK IF THE USER HAS ACCESS
    # Check if the user has admin access
    if current_user.access != 'admin':
        # Check if the user created the projects
        for project_id in projects.ids:
            project = db.query(models.Project).filter(models.Project.id == project_id).first()
            if project.creator_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permissions to assign to the project (ID:{project_id})")

    # Assign the user to projects
    for project_id in projects.ids:
        personnel = models.Personnel(user_id=id, project_id=project_id)
        db.add(personnel)
        db.commit()

    return Response(status_code=status.HTTP_201_CREATED)

# Remove from one/multiple projects
"""I can use URL encoding to fetch project ids instead"""
@router.post("/{id}/remove", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_projects(id: int, projects: schemas.RequestProjectIds, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    # Check if the user exists
    user_q = db.query(models.User).filter(models.User.id == id)
    user = user_q.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User (ID: {id}) doesn't exist")

    # Check if projects with the specified IDs exist
    for project_id in projects.ids:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project (ID:{project_id}) doesn't exist")

    # Check if connection has already been made
    for project_id in projects.ids:
        connection = db.query(models.Personnel).filter(models.Personnel.project_id == project_id, models.Personnel.user_id == id).first()
        if not connection:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'user (ID:{id}) is not assigned to the project (ID:{project.id})')

    # CHECK IF THE USER HAS ACCESS
    # Check if the user has admin access
    if current_user.access != 'admin':
        # Check if the user created the projects
        for project_id in projects.ids:
            project = db.query(models.Project).filter(models.Project.id == project_id).first()
            if project.creator_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permissions to remove from the project (ID:{project_id})")

    # Remove the user from projects
    for project_id in projects.ids:
        personnel_q = db.query(models.Personnel).filter(models.Personnel.user_id == id, models.Personnel.project_id == project_id)
        personnel_q.delete(synchronize_session=False)
        db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

