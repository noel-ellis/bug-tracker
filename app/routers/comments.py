from fastapi import status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db
from ..config import CHANGABLE_COMMENT_ENTRIES
from typing import List

router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)

# Get all comments
@router.get("/", response_model=List[schemas.CommentResponse])
def get_all_users(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    comments = db.query(models.Comment).all()
    return comments

# Get one Comment
@router.get("/{id}", response_model=schemas.CommentOut)
def get_a_comment(id: int, db: Session = Depends(get_db)):

    # Retrieve comment
    comment = db.query(models.Comment).filter(models.Comment.id == id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"comment {id} doesn't exist")
    
    # Retrieve ticket
    ticket = db.query(models.Ticket).filter(models.Ticket.id == comment.ticket_id).first()

    result = {"comment": comment, "ticket": ticket}
    return result

# Edit Comment
@router.put("/{id}", status_code=status.HTTP_205_RESET_CONTENT, response_model=schemas.CommentResponse)
def edit_comment(id: str, user_request: schemas.RequestCommentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    # ===================================================================================================================================
    # CHECKING THE POSSIBILY OF UPDATE
    # ===================================================================================================================================
    # Checking if the comment exists by fetching it from the DB
    comment_q = db.query(models.Comment).filter(models.Comment.id == id)
    comment = comment_q.first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment {id} doesn't exist")
   
    # Check if the user has access
    if current_user.access != 'admin':
        if comment.creator_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Users can only edit their own comments")
    # ===================================================================================================================================

    # ===================================================================================================================================
    # UPDATING COMMENTS DB
    # ===================================================================================================================================
    # Fetching current comment data without unchangable keys
    comment_data = {col.name: getattr(comment, col.name) for col in comment.__table__.columns if col.name in CHANGABLE_COMMENT_ENTRIES}

    # Fetching requested updates
    user_request = {key: val for key, val in user_request.dict().items() if val != None}

    # Updating comment_data with user_request data
    updated_data = {key: user_request.get(key, comment_data[key]) for key in comment_data.keys()}

    # Commit changes in the DB
    comment_q.update(updated_data, synchronize_session=False)   
    db.commit()
    # ===================================================================================================================================

    return comment_q.first()

# Delete Comment
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    # Checking if the ticket exists
    comment_q = db.query(models.Comment).filter(models.Comment.id == id)
    comment = comment_q.first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"comment {id} doesn't exist")
    
    # Checking access
    if comment.creator_id != current_user.id and current_user.access != 'admin':   
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized") 

    # Deleting the comment from db
    comment_q.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)