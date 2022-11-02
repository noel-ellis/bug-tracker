from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
import pytest

# Setting up testing database
SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Drop the previous testing DB and create a new one
@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Use testing db instead of prod db
@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    # Overriding get_db with testing db
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

# Authorized clients
@pytest.fixture()
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client

@pytest.fixture()
def authorized_other_client(client, other_token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {other_token}"
    }

    return client

@pytest.fixture()
def authorized_client_admin(client, admin_token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {admin_token}"
    }

    return client

# Test users
@pytest.fixture
def test_user(client):
    user_data = {"username": "testuser1", "email": "test@email.com", "password": "password"}
    res = client.post("/signup", json=user_data)
    new_user = res.json()
    new_user['password'] = user_data["password"]
    assert res.status_code==201

    return new_user

@pytest.fixture
def test_other_user(client):
    user_data = {"username": "testuser5", "email": "test5@email.com", "password": "password"}
    res = client.post("/signup", json=user_data)
    new_user = res.json()
    new_user['password'] = user_data["password"]
    assert res.status_code==201

    return new_user

@pytest.fixture
def test_admin(client):
    user_data = {"username": "admin", "email": "admin@email.com", "password": "password"}
    res = client.post("/signup", json=user_data)
    new_user = res.json()
    new_user['password'] = user_data["password"]
    assert res.status_code==201

    return new_user

# Three tokens for every type of authorized users
@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})

@pytest.fixture
def other_token(test_other_user):
    return create_access_token({"user_id": test_other_user["id"]})

@pytest.fixture
def admin_token(test_admin):
    return create_access_token({"user_id": test_admin["id"]})

# Dummy objects
@pytest.fixture
def dummy_users(client):
    user_data = [
                {"username": "testuser2", "email": "test1@email.com", "password": "password"},
                {"username": "testuser3", "email": "test2@email.com", "password": "password"},
                {"username": "testuser4", "email": "test3@email.com", "password": "password"}
                ]
                
    users = []
    for user in user_data:
        res = client.post("/signup", json=user)
        assert res.status_code==201
        new_user = res.json()
        new_user['password'] = user["password"]
        users.append(new_user)

    return users

@pytest.fixture
# Created by test_user
def dummy_projects(authorized_client):
    projects = [
        {'name': 'project1', 'description': 'description1'},
        {'name': 'project2', 'description': 'description2', 'status': 'ongoing'},
        {'name': 'project3', 'description': 'description3', 'status': 'finished', 'start': '2022-10-17', 'deadline': '2022-11-01'}
    ]

    new_projects = []
    for project in projects:
        res = authorized_client.post('/projects/', json=project)
        assert res.status_code==201
        new_project = res.json()
        new_projects.append(new_project)


    return new_projects


@pytest.fixture
# Created by test_user
def dummy_tickets(authorized_client):
    # Projects
    projects = [
        {'name': 'project1', 'description': 'description1'},
        {'name': 'project2', 'description': 'description2', 'status': 'ongoing'},
        {'name': 'project3', 'description': 'description3', 'status': 'ongoing', 'start': '2022-10-17', 'deadline': '2022-11-01'}
    ]

    for project in projects:
        res = authorized_client.post('/projects/', json=project)
        assert res.status_code==201

    # Tickets
    new_tickets = []
    tickets = [
        {'caption': 'ticket1', 'description': 'description1', 'priority': 0, 'category': 'bug'},
        {'caption': 'ticket2', 'description': 'description2', 'priority': 1, 'category': 'feature request'},
        {'caption': 'ticket3', 'description': 'description3', 'priority': 2, 'category': 'other'}
    ]

    for ticket in tickets:
        res = authorized_client.post('/projects/1/newticket', json=ticket)
        assert res.status_code == 201
        new_tickets.append(res.json())

    return new_tickets

@pytest.fixture
# Created by test_user
def dummy_comments(authorized_client):
    # Projects
    projects = [
        {'name': 'project1', 'description': 'description1'},
        {'name': 'project2', 'description': 'description2', 'status': 'ongoing'},
        {'name': 'project3', 'description': 'description3', 'status': 'ongoing', 'start': '2022-10-17', 'deadline': '2022-11-01'}
    ]

    for project in projects:
        res = authorized_client.post('/projects/', json=project)
        assert res.status_code==201

    # Tickets
    new_tickets = []
    tickets = [
        {'caption': 'ticket1', 'description': 'description1', 'priority': 0, 'category': 'bug'},
        {'caption': 'ticket2', 'description': 'description2', 'priority': 1, 'category': 'feature request'},
        {'caption': 'ticket3', 'description': 'description3', 'priority': 2, 'category': 'other'}
    ]

    for ticket in tickets:
            res = authorized_client.post('/projects/1/newticket', json=ticket)
            assert res.status_code == 201

    # Comments
    i = 1
    new_comments = []
    comments = [
        {'body_text': "comment1"},
        {'body_text': "comment2"},
        {'body_text': "comment3"}
    ]

    for comment in comments:
            res = authorized_client.post(f'/tickets/{i}/comment', json=comment)
            i += 1
            assert res.status_code == 201
            new_comments.append(res.json())

    return new_comments
