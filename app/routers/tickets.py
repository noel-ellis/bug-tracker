from fastapi import status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, oauth2
from ..database import get_db
from ..config import CHANGABLE_TICKET_ENTRIES
from typing import List, Optional

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)

# Get all Tickets
@router.get('/', response_model=List[schemas.TicketResponse])
def get_tickets(db: Session = Depends(get_db), 
                limit: int = 10, 
                priority: Optional[int] = '', 
                category: Optional[str] = '',
                status: Optional[str] = '', 
                search: Optional[str] = ''):

    tickets = db.query(models.Ticket)

    # Filter by priority
    if priority != '':
        tickets = tickets.filter(models.Ticket.priority == priority)

    # Filter by category
    if category != '':
        tickets = tickets.filter(models.Ticket.category == category)

    # Filter by status
    if status != '':
        tickets = tickets.filter(models.Ticket.status == status)

    # Search
    if search != '':
        tickets_by_descr = tickets.filter(func.lower(models.Ticket.description).contains(search.lower())).limit(limit).all()
        tickets_by_capt = tickets.filter(func.lower(models.Ticket.caption).contains(search.lower())).limit(limit).all()

        result = list(set(tickets_by_descr + tickets_by_capt))

        return result

    return tickets.limit(limit).all()

# Get one Ticket
@router.get("/{id}", response_model=schemas.TicketOut)
def get_a_ticket(id: int, db: Session = Depends(get_db)):

    # Retrieve ticket
    ticket = db.query(models.Ticket).filter(models.Ticket.id == id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"project {id} doesn't exist")

    # Retrieve comments
    comments = db.query(models.Comment).filter(models.Comment.ticket_id == id).all()

    # Retrieving update history
    update_history = db.query(models.TicketUpdateHistory).filter(models.TicketUpdateHistory.ticket_id == id).all()

    result = {"ticket": ticket, "comments": comments, "update_history": update_history}
    return result

# Edit Ticket
@router.put("/{id}", status_code=status.HTTP_205_RESET_CONTENT, response_model=schemas.TicketResponse)
def edit_ticket(id: str, user_request: schemas.RequestTicketUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    # ===================================================================================================================================
    # CHECKING THE POSSIBILY OF UPDATE
    # ===================================================================================================================================
    # Checking if the ticket exists by fetching it from the DB
    ticket_q = db.query(models.Ticket).filter(models.Ticket.id == id)
    ticket = ticket_q.first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket {id} doesn't exist")
   
    # Check if the user has access
    if current_user.access != 'admin':
        if ticket.creator_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Users can only edit their own tickets")
    # ===================================================================================================================================

    # ===================================================================================================================================
    # UPDATING TICKETS DB
    # ===================================================================================================================================
    # Fetching current ticket data without unchangable keys
    ticket_data = {col.name: getattr(ticket, col.name) for col in ticket.__table__.columns if col.name in CHANGABLE_TICKET_ENTRIES}

    # Fetching requested updates
    user_request = {key: val for key, val in user_request.dict().items() if val != None}

    # Updating ticket_data with user_request data
    updated_data = {key: user_request.get(key, ticket_data[key]) for key in ticket_data.keys()}

    # Commit changes in the DB
    ticket_q.update(updated_data, synchronize_session=False)   
    db.commit()
    # ===================================================================================================================================

    # ===================================================================================================================================
    # SAVING CHANGES IN THE TicketUpdateHistory
    # ===================================================================================================================================
    #Updating naming so dictionaries can be properly unpacked into the TicketUpdateHistory object
    entries_old = [f"old_{x}" for x in CHANGABLE_TICKET_ENTRIES]
    ticket_data = dict(zip(entries_old, list(ticket_data.values())))
    entries_new = [f"new_{x}" for x in CHANGABLE_TICKET_ENTRIES]
    updated_data = dict(zip(entries_new, list(updated_data.values())))

    # Creating a new ProjectUpdateHistory entry
    history_update = models.TicketUpdateHistory(editor_id = current_user.id, ticket_id = id, **ticket_data, **updated_data)
    db.add(history_update)
    db.commit()
    db.refresh(history_update)
    # ===================================================================================================================================
    return ticket_q.first()

# Delete Ticket
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    # Checking if the ticket exists
    ticket_q = db.query(models.Ticket).filter(models.Ticket.id == id)
    ticket = ticket_q.first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket {id} doesn't exist")

    # Checking access
    if ticket.creator_id != current_user.id and current_user.access != 'admin':   
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized")
    
    # Deleting the ticket from db
    ticket_q.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Comment a ticket
@router.post("/{id}/comment", status_code=status.HTTP_201_CREATED, response_model=schemas.CommentResponse)
def add_comment(id: int, comment_info: schemas.RequestComment, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    # Checking if the ticket exists
    ticket_q = db.query(models.Ticket).filter(models.Ticket.id == id)
    ticket = ticket_q.first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket {id} doesn't exist")
    
    comment = models.Comment(creator_id=current_user.id, ticket_id=id, **comment_info.dict())

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment