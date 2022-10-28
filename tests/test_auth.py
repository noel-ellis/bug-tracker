# Tests should be independable of one another

import pytest
from app import schemas
from jose import jwt
from app.config import settings

# Test functions
def test_signup(client):
    res = client.post("/signup", json={"username": "testuser1", "email": "test@email.com", "password": "password"})
    
    new_user = schemas.UserResponse(**res.json())
    assert new_user.username == "testuser1"
    assert res.status_code == 201

def test_login(client, test_user):
    res = client.post("/login", data={"username": test_user['username'], "password": test_user['password']})
    login_res = schemas.Token(**res.json())

    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = str(payload.get("user_id"))

    assert id == test_user['id']
    assert login_res.token_type == 'bearer'
    assert res.status_code == 200

@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail', 'password', 403),
    ('test@email.com', 'wrongpassword', 403),
    ('wrongemail', 'wrongpassword', 403),
    (None, 'password', 422),
    ('test@email.com', None, 422)
])
def test_incorrect_login(client, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})

    assert res.status_code == status_code

    