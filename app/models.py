from .database import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text


# SQLAlchemy model for 'projects' table in postgresql
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    name = Column(String)
    surname = Column(String)
    access = Column(String, server_default='user', nullable = False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    start = Column(Date)
    deadline = Column(Date)
    status = Column(String, server_default='ongoing', nullable = False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Fetch user object for given creator_id
    creator = relationship("User")

class Personnel(Base):
    __tablename__ = "personnel"

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    assigned_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, nullable=False)
    caption = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    status = Column(String, server_default='new', nullable = False)
    category = Column(String, nullable = False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    # Fetch creator/project connected to the ticket
    project = relationship("Project")
    creator = relationship("User")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, nullable=False)
    body_text = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)

    # Fetch user object for given creator_id
    creator = relationship("User")
    ticket = relationship("Ticket")

class TicketUpdateHistory(Base):
    __tablename__ = "ticket_updates"

    id = Column(Integer, primary_key=True, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    editor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
     
    old_caption = Column(String, server_default=None)
    old_description = Column(String, server_default=None)
    old_priority = Column(String, server_default=None)
    old_status = Column(String, server_default=None)
    old_category = Column(String, server_default=None)

    new_caption = Column(String, server_default=None)
    new_description = Column(String, server_default=None)
    new_priority = Column(String, server_default=None)
    new_status = Column(String, server_default=None)
    new_category = Column(String, server_default=None)

    # Fetch user object for given creator_id
    editor = relationship("User")
    ticket = relationship("Ticket")

class ProjectUpdateHistory(Base):
    __tablename__ = "project_updates"

    id = Column(Integer, primary_key=True, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    editor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    old_name = Column(String, server_default=None)
    old_description = Column(String, server_default=None)
    old_start = Column(TIMESTAMP(timezone=True), server_default=None)
    old_deadline = Column(TIMESTAMP(timezone=True), server_default=None)
    old_status = Column(String, server_default=None)

    new_name = Column(String, server_default=None)
    new_description = Column(String, server_default=None)
    new_start = Column(TIMESTAMP(timezone=True), server_default=None)
    new_deadline = Column(TIMESTAMP(timezone=True), server_default=None)
    new_status = Column(String, server_default=None)

    # Fetch user, project objects for given editor_id
    editor = relationship("User")
    project = relationship("Project")