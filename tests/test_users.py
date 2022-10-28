# Tests should be independable of one another

# Get all users
def test_get_all(client, dummy_users):
    
    res = client.get("/users/")
    new_users = res.json()

    assert new_users[0]['username'] == dummy_users[0]['username']
    assert new_users[1]['username'] == dummy_users[1]['username']
    assert new_users[2]['username'] == dummy_users[2]['username']
    assert new_users[0]['email'] == dummy_users[0]['email']
    assert new_users[1]['email'] == dummy_users[1]['email']
    assert new_users[2]['email'] == dummy_users[2]['email']

# Get one user
def test_get_one(client, dummy_users):
    res = client.get("/users/1")
    user = res.json()

    assert user['user']['id'] == '1'
    assert user['user']['username'] == dummy_users[0]['username']
    assert user['user']['email'] == dummy_users[0]['email']
    assert user['user']['access'] == 'user'
    assert user['tickets'] == []
    assert user['projects'] == []

# Get non-existent user
def test_get_one_wrong_id(client):
    res = client.get("/users/4")
    assert res.status_code == 404

# User attempts to edit their own profile
def test_edit_user(authorized_client):
    update_data={
        "username": 'edited', 
        "email": 'edited@email.com',
        "name": "TestName",
        "surname": "TestSurname"
    }

    res = authorized_client.put("/users/1", json=update_data) 
    user = res.json()

    assert res.status_code == 205
    assert user['id'] == '1'
    assert user['username'] == update_data['username']
    assert user['email'] == update_data['email']
    assert user['name'] == update_data['name']
    assert user['surname'] == update_data['surname']
    assert user['access'] == 'user'

# Admin attempts to edit someone else's profile
def test_edit_user_from_admin(dummy_users, authorized_client_admin):
    update_data={
        "username": 'edited', 
        "email": 'edited@email.com',
        "name": "TestName",
        "surname": "TestSurname", 
        "access": 'admin'
    }
    
    res = authorized_client_admin.put("/users/1", json=update_data) 
    user = res.json()

    assert res.status_code == 205
    assert user['id'] == '1'
    assert user['username'] == update_data['username']
    assert user['email'] == update_data['email']
    assert user['name'] == update_data['name']
    assert user['surname'] == update_data['surname']
    assert user['access'] == 'admin'

# Admin attempts to edit non-existing profile
def test_edit_wrong_id(dummy_users, authorized_client_admin):
    update_data={
        "username": 'edited', 
        "email": 'edited@email.com',
        "name": "TestName",
        "surname": "TestSurname", 
        "access": 'admin'
    }
    
    res = authorized_client_admin.put("/users/10", json=update_data)
    assert res.status_code == 404

# User attempts to edit access level
def test_edit_access_fail(authorized_client):
    update_data={
        "username": 'edited', 
        "email": 'edited@email.com',
        "name": "TestName",
        "surname": "TestSurname", 
        "access": 'admin'
    }

    res = authorized_client.put("/users/1", json=update_data)
    assert res.status_code == 403

# User attempts to edit someone else's profile
def test_edit_forbidden(dummy_users, authorized_client):
    update_data={
        "username": 'edited', 
        "email": 'edited@email.com',
        "name": "TestName",
        "surname": "TestSurname"
    }

    res = authorized_client.put("/users/1", json=update_data)
    assert res.status_code == 403

# Wrond update data
def test_edit_wrong_data(authorized_client):
    update_data={
        "username": 'edited', 
        "email": 'edited',
        "name": "TestName",
        "surname": "TestSurname"
    }

    res = authorized_client.put("/users/1", json=update_data)
    assert res.status_code == 422

# Delete self
def test_delete(authorized_client):
    res = authorized_client.delete("/users/1")

    assert res.status_code == 204

# Admin attempts to delete user
def test_delete_by_admin(dummy_users, authorized_client_admin):
    res = authorized_client_admin.delete("/users/2")

    assert res.status_code == 204

# User attempts to delete another user
def test_delete_by_unathorized_user(dummy_users, authorized_client):
    res = authorized_client.delete("/users/2")

    assert res.status_code == 403

# Delete non-existent user
def test_delete_wrong_id(authorized_client_admin):
    res = authorized_client_admin.delete("/users/10")

    assert res.status_code == 404

# Assign user 2 to projects 1, 2 by creator of these projects
def test_assign(authorized_client, dummy_projects, dummy_users):
    data = {'ids': [1, 2]}
    res = authorized_client.post("users/2/assign", json=data)

    # Fetch project 1, 2 as project_a, project_b
    res_project_a = authorized_client.get("/projects/1")
    project_a = res_project_a.json()
    res_project_b = authorized_client.get("/projects/2")
    project_b = res_project_b.json()

    assert project_a['personnel'][1]['id'] == '2'
    assert project_b['personnel'][1]['id'] == '2'
    assert res.status_code == 201

# Assign user 2 to non-existent projects
def test_assign_wrong_project_ids(authorized_client, dummy_projects, dummy_users):
    data = {'ids': [5, 6]}
    res = authorized_client.post("users/2/assign", json=data)

    assert res.status_code == 404

# Assign non-existing user to projects 1, 2
def test_assign_wrong_user_id(authorized_client, dummy_projects, dummy_users):
    data = {'ids': [1, 2]}
    res = authorized_client.post("users/10/assign", json=data)

    assert res.status_code == 404

# Assign user 2 to projects they were already assigned to 
def test_assign_conflict(authorized_client, dummy_projects, dummy_users):
    data = {'ids': [1, 2]}
    res = authorized_client.post("users/2/assign", json=data)
    assert res.status_code == 201

    data = {'ids': [1, 2]}
    res = authorized_client.post("users/2/assign", json=data)
    assert res.status_code == 409

# Remove user (id:2) from project (id:1)
def test_remove(authorized_client, dummy_projects, dummy_users):
    data = {'ids': [1, 2]}
    res = authorized_client.post("users/2/assign", json=data)

    # Fetch project 1, 2 as project_a, project_b
    res_project_a = authorized_client.get("/projects/1")
    project_a = res_project_a.json()
    res_project_b = authorized_client.get("/projects/2")
    project_b = res_project_b.json()

    assert project_a['personnel'][1]['id'] == '2'
    assert project_b['personnel'][1]['id'] == '2'
    assert res.status_code == 201

    # Removing user (id:2) from project (id:1)
    data = {'ids': [1]}
    res = authorized_client.post('users/2/remove', json=data)

    # Fetch project 1, 2 as project_a, project_b
    res_project_a = authorized_client.get("/projects/1")
    project_a = res_project_a.json()
    res_project_b = authorized_client.get("/projects/2")
    project_b = res_project_b.json()

    assert len(project_a['personnel']) == 1
    assert project_b['personnel'][1]['id'] == '2'
    assert res.status_code == 204

# Remove non-existent user from project (id:1)
def test_remove_wrong_user_id(authorized_client, dummy_projects, dummy_users):
    data = {'ids': [1]}
    res = authorized_client.post('users/10/remove', json=data)

    assert res.status_code == 404

# Remove user (id:2) from non-existent project
def test_remove_wrong_project_id(authorized_client, dummy_projects, dummy_users):
    data = {'ids': [10]}
    res = authorized_client.post('users/2/remove', json=data)

    assert res.status_code == 404

# Remove user (id:2) from project (id:1); user has never been assigned to this project before
def test_remove_conflict(authorized_client, dummy_projects, dummy_users):
    data = {'ids': [1]}
    res = authorized_client.post('users/2/remove', json=data)

    assert res.status_code == 409