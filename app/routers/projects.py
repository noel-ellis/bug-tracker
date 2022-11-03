from fastapi import status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, oauth2
from ..database import get_db
from ..config import CHANGABLE_PROJECT_ENTRIES
from typing import List, Optional

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

# Get all Projects
@router.get('/', response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db), 
                limit: Optional[int] = 10,
                search: Optional[str] = "",
                status: Optional[str] = "",
                ):

    projects = db.query(models.Project)

    # Filter by status
    if status != '':
        projects = projects.filter(models.Project.status == status)

    # Search
    if search != '':
        projects_by_descr = projects.filter(func.lower(models.Project.description).contains(search.lower())).limit(limit).all()
        projects_by_name = projects.filter(func.lower(models.Project.name).contains(search.lower())).limit(limit).all()

        result = list(set(projects_by_descr + projects_by_name))

        return result


    return projects.limit(limit).all()

# Get one Project
@router.get("/{id}", response_model=schemas.ProjectOut)
def select_project(id: int, db: Session = Depends(get_db)):

    # Retrieving project
    project = db.query(models.Project).filter(models.Project.id == id).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"project {id} doesn't exist")

    # Retrieving all the tickets connected to the project
    tickets = db.query(models.Ticket).filter(models.Ticket.project_id == id).all()

    # Retrieving all the users connected to the project
    personnel = db.query(models.User).join(models.Personnel, models.Personnel.user_id == models.User.id).filter(models.Personnel.project_id == id).all()

    # Retrieving update history
    update_history = db.query(models.ProjectUpdateHistory).filter(models.ProjectUpdateHistory.project_id == id).all()

    result = {"project": project, "tickets": tickets, "personnel": personnel, "update_history": update_history}
    return result

# Create a new Project
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ProjectResponse)
def new_project(project_info: schemas.RequestProject, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    project = models.Project(creator_id=current_user.id, **project_info.dict())
    db.add(project)
    db.commit()
    db.refresh(project)

    personnel = models.Personnel(user_id=current_user.id, project_id=project.id)
    db.add(personnel)
    db.commit()
    db.refresh(personnel)

    return project

# Edit Project
@router.put("/{id}", status_code=status.HTTP_205_RESET_CONTENT, response_model=schemas.ProjectResponse)
def edit_project(id: str, user_request: schemas.RequestProjectUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    # ===================================================================================================================================
    # CHECKING THE POSSIBILY OF UPDATE
    # ===================================================================================================================================
    # Checking if the project exists by fetching it from the DB
    project_q = db.query(models.Project).filter(models.Project.id == id)
    project = project_q.first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {id} doesn't exist")
   
    # Check if the user has access
    if current_user.access != 'admin':
        if project.creator_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Users can only edit their own projects")
    # ===================================================================================================================================

    # ===================================================================================================================================
    # UPDATING PROJECTS DB
    # ===================================================================================================================================
    # Fetching current project data without unchangable keys
    project_data = {col.name: getattr(project, col.name) for col in project.__table__.columns if col.name in CHANGABLE_PROJECT_ENTRIES}

    # Fetching requested updates
    user_request = {key: val for key, val in user_request.dict().items() if val != None}

    # Updating project_data with user_request data
    updated_data = {key: user_request.get(key, project_data[key]) for key in project_data.keys()}

    # Commit changes in the DB
    project_q.update(updated_data, synchronize_session=False)   
    db.commit()
    # ===================================================================================================================================

    # ===================================================================================================================================
    # SAVING CHANGES IN THE ProjectUpdateHistory
    # ===================================================================================================================================
    # Updating naming so dictionaries can be properly unpacked into the ProjectUpdateHistory object
    entries_old = [f"old_{x}" for x in CHANGABLE_PROJECT_ENTRIES]
    project_data = dict(zip(entries_old, list(project_data.values())))
    entries_new = [f"new_{x}" for x in CHANGABLE_PROJECT_ENTRIES]
    updated_data = dict(zip(entries_new, list(updated_data.values())))
    
    # Creating a new ProjectUpdateHistory entry
    history_update = models.ProjectUpdateHistory(editor_id = current_user.id, project_id = id, **project_data, **updated_data, personnel_change = '')
    db.add(history_update)
    db.commit()
    db.refresh(history_update)
    # ===================================================================================================================================

    return project_q.first()

# Delete Project
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    # Checking if the project exists
    project_q = db.query(models.Project).filter(models.Project.id == id)
    project = project_q.first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"project {id} doesn't exist")

    # Checking if the user has access
    if project.creator_id != current_user.id:   
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized")

    project_q.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Create a new Ticket 
@router.post("/{id}/newticket", status_code=status.HTTP_201_CREATED, response_model=schemas.TicketResponse)
def new_ticket(id: int, ticket_info: schemas.RequestTicket, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    # Check if project exists
    project = db.query(models.Project).filter(models.Project.id == id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {id} doesn't exist")

    ticket = models.Ticket(creator_id=current_user.id, project_id=id, **ticket_info.dict())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket

# PERSONNEL
# Assign personnel
"""It's probably possible to use URL encoding to fetch user ids instead"""
@router.post("/{id}/addpersonnel", status_code=status.HTTP_201_CREATED)
def assign_user(id: int, users: schemas.RequestAssignedUsers, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    # ===================================================================================================================================
    # CHECKING THE POSSIBILY OF UPDATE
    # ===================================================================================================================================
    # Check if project exists
    project = db.query(models.Project).filter(models.Project.id == id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {id} doesn't exist")
   
    # CHECK IF THE USER HAS ACCESS
    # Check if the user has admin access
    if current_user.access != 'admin':
        # Check if the user created the project
        if project.creator_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Users can only assign personnel to their own projects")

    # Check if users with the specified IDs exist
    for user_id in users.ids:
        target_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User (ID:{user_id}) doesn't exist")

    # Check if connection has already been made
    for user_id in users.ids:
        connection = db.query(models.Personnel).filter(models.Personnel.project_id == id, models.Personnel.user_id == user_id).first()
        if connection:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'user (ID:{user_id}) is already assigned to the project (ID:{id})')
    # ===================================================================================================================================

    # Add personnel to the project
    personnel_change_entry = 'a;' # Logging
    for user_id in users.ids:
        personnel_change_entry += str(user_id) + ';' # Logging
        personnel = models.Personnel(user_id=user_id, project_id=id)
        db.add(personnel)
        db.commit()
        db.refresh(personnel)
    
    # ===================================================================================================================================
    # SAVING CHANGES IN THE ProjectUpdateHistory
    # ===================================================================================================================================
    # Fixing log format
    personnel_change_entry = personnel_change_entry[:-1]

    # Logging event into project_updates table
    # Fetching current project data without unchangable keys
    project_data = {col.name: getattr(project, col.name) for col in project.__table__.columns if col.name in CHANGABLE_PROJECT_ENTRIES}

    # Updating naming so dictionaries can be properly unpacked into the ProjectUpdateHistory object
    entries_old = [f"old_{x}" for x in CHANGABLE_PROJECT_ENTRIES]
    entries_new = [f"new_{x}" for x in CHANGABLE_PROJECT_ENTRIES]
    updated_data = dict(zip(entries_new, list(project_data.values())))
    project_data = dict(zip(entries_old, list(project_data.values())))
    
    # Creating a new ProjectUpdateHistory entry
    history_update = models.ProjectUpdateHistory(editor_id = current_user.id, project_id = id, **project_data, **updated_data, personnel_change = personnel_change_entry)
    db.add(history_update)
    db.commit()
    db.refresh(history_update)
    # ===================================================================================================================================

    return Response(status_code=status.HTTP_201_CREATED)

# Remove personnel
"""I can use URL encoding to fetch user ids instead"""
@router.post("/{id}/removepersonnel", status_code=status.HTTP_204_NO_CONTENT)
def assign_user(id: int, users: schemas.RequestAssignedUsers, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    # ===================================================================================================================================
    # CHECKING THE POSSIBILY OF UPDATE
    # ===================================================================================================================================
    # Check if project exists
    project = db.query(models.Project).filter(models.Project.id == id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {id} doesn't exist")
   
    # CHECK IF THE USER HAS ACCESS
    # Check if the user has admin access
    if current_user.access != 'admin':
        # Check if the user created the project
        if project.creator_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Users can only remove personnel from their own projects")

    # Check if users with the specified IDs exist
    for user_id in users.ids:
        target_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User (ID:{user_id}) doesn't exist")

    # Check if users were never assigned
    for user_id in users.ids:
        connection = db.query(models.Personnel).filter(models.Personnel.project_id == id, models.Personnel.user_id == user_id).first()
        if not connection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user (ID:{user_id}) is not assigned to the project (ID:{id})')
    # ===================================================================================================================================

    # Remove personnel from the project
    personnel_change_entry = 'r;' # Logging
    for user_id in users.ids:
        personnel_change_entry += str(user_id) + ';' # Logging
        personnel_q = db.query(models.Personnel).filter(models.Personnel.user_id == user_id, models.Personnel.project_id == id)
        personnel_q.delete(synchronize_session=False)
        db.commit()

    # ===================================================================================================================================
    # SAVING CHANGES IN THE ProjectUpdateHistory
    # ===================================================================================================================================
    # Fixing log format
    personnel_change_entry = personnel_change_entry[:-1]

    # Logging event into project_updates table
    # Fetching current project data without unchangable keys
    project_data = {col.name: getattr(project, col.name) for col in project.__table__.columns if col.name in CHANGABLE_PROJECT_ENTRIES}

    # Updating naming so dictionaries can be properly unpacked into the ProjectUpdateHistory object
    entries_old = [f"old_{x}" for x in CHANGABLE_PROJECT_ENTRIES]
    entries_new = [f"new_{x}" for x in CHANGABLE_PROJECT_ENTRIES]
    updated_data = dict(zip(entries_new, list(project_data.values())))
    project_data = dict(zip(entries_old, list(project_data.values())))
    
    # Creating a new ProjectUpdateHistory entry
    history_update = models.ProjectUpdateHistory(editor_id = current_user.id, project_id = id, **project_data, **updated_data, personnel_change = personnel_change_entry)
    db.add(history_update)
    db.commit()
    db.refresh(history_update)
    # ===================================================================================================================================

    return Response(status_code=status.HTTP_204_NO_CONTENT)


