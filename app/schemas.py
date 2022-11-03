# Pydantic schemas for defining the structure of ... 
from pydantic import BaseModel, validator, EmailStr
from datetime import date, datetime
from typing import List, Optional

# REQUESTS
class RequestUserBase(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None

class RequestUserSignup(RequestUserBase):
    username: str
    email: EmailStr
    password: str

class RequestProject(BaseModel):
    name: str
    description: str
    status: Optional[str] = None
    start: Optional[date] = None
    deadline: Optional[date] = None

class RequestTicket(BaseModel):
    caption: str
    description: str
    priority: int
    category: str

class RequestComment(BaseModel):
    body_text: str

class RequestUserUpdate(RequestUserBase):
    username: Optional[str]
    email: Optional[EmailStr]
    access: Optional[str]

class RequestProjectUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    status: Optional[str]
    start: Optional[date]
    deadline: Optional[date]

class RequestTicketUpdate(BaseModel):
    caption: Optional[str]
    description: Optional[str]
    priority: Optional[int]
    status: Optional[str]
    category: Optional[str]

class RequestCommentUpdate(BaseModel):
    body_text: Optional[str]

class RequestProjectIds(BaseModel):
    ids: List[int]

class RequestAssignedUsers(BaseModel):
    ids: List[int]

# RESPONSES
class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    access: str
    name: Optional[str] = None
    surname: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class ProjectResponse(RequestProject):
    id: str
    created_at: datetime
    creator_id: int
    creator: UserResponse
    status: str

    @validator('start')
    def start_is_set(cls, v):
        if v is None:
            return f'not set'
        return v

    @validator('deadline')
    def deadline_is_set(cls, v):
        if v is None:
            return f'not set'
        return v

    class Config:
        orm_mode = True

class TicketResponse(BaseModel):
    id: str
    caption: str
    description: str
    priority: int
    category: str
    status: str
    creator_id: int
    project_id: int
    created_at: datetime
    project: ProjectResponse
    creator: UserResponse

    class Config:
        orm_mode = True

class CommentResponse(BaseModel):
    id: int
    body_text: str
    creator_id: int
    ticket_id: int
    created_at: datetime
    creator: UserResponse

    class Config:
        orm_mode = True

class ProjectUpdateHistoryResponse(BaseModel):
    id: int
    updated_at: datetime

    old_name: str
    new_name: str
    old_description: str
    new_description: str
    old_start: Optional[datetime] = None
    new_start: Optional[datetime] = None
    old_deadline: Optional[datetime] = None
    new_deadline: Optional[datetime] = None
    old_status: str
    new_status: str
    personnel_change: str

    editor: UserResponse
    # Use if retrieval of the original project is needed
    # project: ProjectResponse 

    class Config:
        orm_mode = True

class TicketUpdateHistoryResponse(BaseModel):
    id: int
    updated_at: datetime

    old_caption: str
    new_caption: str
    old_description: str
    new_description: str
    old_priority: str
    new_priority: str
    old_status: str
    new_status: str
    old_category: str
    new_category: str

    editor: UserResponse
    # Use if retrieval of the original ticket is needed:
    # ticket: TicketResponse

    class Config:
        orm_mode = True

class ProjectOut(BaseModel):
    project: ProjectResponse
    tickets: List[TicketResponse]
    personnel: List[UserResponse]
    update_history: List[ProjectUpdateHistoryResponse]

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    user: UserResponse
    tickets: List[TicketResponse]
    projects: List[ProjectResponse]

    class Config:
        orm_mode = True

class TicketOut(BaseModel):
    ticket: TicketResponse
    comments: List[CommentResponse]
    update_history: List[TicketUpdateHistoryResponse]

    class Config:
        orm_mode = True

class CommentOut(BaseModel):
    comment: CommentResponse
    ticket: TicketResponse

    class Config:
        orm_mode = True

# Authentication
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None
