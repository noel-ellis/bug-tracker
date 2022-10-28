# Tests should be independable of one another

# Get all projects
def test_get_all(client, dummy_projects):
    
    res = client.get("/projects/")
    new_projects = res.json()

    assert res.status_code == 200
    assert new_projects[0]['name'] == dummy_projects[0]['name']
    assert new_projects[1]['name'] == dummy_projects[1]['name']
    assert new_projects[2]['name'] == dummy_projects[2]['name']
    assert new_projects[0]['description'] == dummy_projects[0]['description']
    assert new_projects[1]['description'] == dummy_projects[1]['description']
    assert new_projects[2]['description'] == dummy_projects[2]['description']

# Get one project
def test_get_one(client, dummy_projects):
    
    res = client.get("/projects/1")
    new_project = res.json()

    assert res.status_code == 200
    assert new_project['project']['name'] == dummy_projects[0]['name']
    assert new_project['project']['description'] == dummy_projects[0]['description']
    assert new_project['project']['id'] == dummy_projects[0]['id']
    assert new_project['project']['creator']['id'] == str(new_project['project']['creator_id'])

# Get non-existent project
def test_get_one_wrong_id(client, dummy_projects):
    
    res = client.get("/projects/10")
    assert res.status_code == 404

# Create a new project
def test_create(authorized_client):
    project_data = {'name': 'project3', 'description': 'description3', 'start': '2022-10-17', 'deadline': '2022-11-01'}
    res = authorized_client.post('/projects/', json=project_data)
    new_project = res.json()

    assert res.status_code==201
    assert new_project['name'] == project_data['name']
    assert new_project['description'] == project_data['description']
    assert new_project['status'] == 'ongoing'
    assert new_project['start'] == project_data['start']
    assert new_project['deadline'] == project_data['deadline']

# Create a new project; Wrong data
def test_create_wrong_data(authorized_client):
    project_data = {'name': 'project3', 'description': 'description3', 'start': 'yesterday', 'deadline': 'today'}
    res = authorized_client.post('/projects/', json=project_data)

    assert res.status_code==422

# Edit a project
def test_edit(authorized_client, dummy_projects):
    update_data = {
        'name': 'edited',
        'description': 'edited',
        'status': 'finished',
        'start': '2022-10-18',
        'deadline': '2022-11-18'
    }
    res = authorized_client.put("/projects/1", json=update_data)
    project = authorized_client.get("/projects/1").json()

    assert len(project['update_history']) == 1
    assert res.status_code == 205

# Edit a project; Wrong id
def test_edit_wrong_id(authorized_client, dummy_projects):
    update_data = {
        'name': 'edited',
        'description': 'edited',
        'status': 'finished',
        'start': '2022-10-18',
        'deadline': '2022-11-18'
    }
    res = authorized_client.put("/projects/10", json=update_data)

    assert res.status_code == 404

# Edit a project; No access
def test_edit_no_access(dummy_projects, authorized_other_client):
    update_data = {
        'name': 'edited',
        'description': 'edited',
        'status': 'finished',
        'start': '2022-10-18',
        'deadline': '2022-11-18'
    }
    res = authorized_other_client.put("/projects/1", json=update_data)

    assert res.status_code == 403

# Edit a project; No access
def test_edit_wrong_data(dummy_projects, authorized_client):
    update_data = {
        'name': 'edited',
        'description': 'edited',
        'status': 'finished',
        'start': 'tomorrow',
        'deadline': 'yesterday'
    }
    res = authorized_client.put("/projects/1", json=update_data)

    assert res.status_code == 422

# User deletes their own project
def test_delete(dummy_projects, authorized_client):
    res = authorized_client.delete("projects/1")

    assert res.status_code == 204

# User tries to delete non-existing project
def test_delete_wrong_id(dummy_projects, authorized_client):
    res = authorized_client.delete("projects/10")

    assert res.status_code == 404

# User tries to delete someone else's project
def test_delete_no_access(dummy_projects, authorized_other_client):
    res = authorized_other_client.delete("projects/1")

    assert res.status_code == 403

# User (id:1) assigns users (id:2, 3) to their own project (id:1)
def test_assign(dummy_projects, dummy_users, authorized_client):
    data = {
        'ids': [2, 3]
    }

    res = authorized_client.post("/projects/1/addpersonnel", json=data)
    project = authorized_client.get("/projects/1")
    project = project.json()

    assert len(project['personnel']) == 3
    assert project['personnel'][1]['id'] == '2'
    assert project['personnel'][2]['id'] == '3'
    assert res.status_code == 201

# Admin (id:5) assigns users (id:2, 3) to user's (id:1) project (id:1)
def test_assign_by_admin(dummy_projects, dummy_users, authorized_client_admin):
    data = {
        'ids': [2, 3]
    }

    res = authorized_client_admin.post("/projects/1/addpersonnel", json=data)
    project = authorized_client_admin.get("/projects/1")
    project = project.json()

    assert len(project['personnel']) == 3
    assert project['personnel'][1]['id'] == '2'
    assert project['personnel'][2]['id'] == '3'
    assert res.status_code == 201

# User (id:1) attempts to assign users (id:2, 3) to non-existent project
def test_assign_wrong_project_id(dummy_projects, dummy_users, authorized_client):
    data = {
        'ids': [2, 3]
    }

    res = authorized_client.post("/projects/10/addpersonnel", json=data)

    assert res.status_code == 404

# User (id:1) assigns non-existent users to their own project (id:1)
def test_assign_wrong_users(dummy_projects, dummy_users, authorized_client):
    data = {
        'ids': [20, 30]
    }

    res = authorized_client.post("/projects/1/addpersonnel", json=data)

    assert res.status_code == 404

# User (id:1) tries to assign users (id:2, 3) to their own project (id:1) twice
def test_assign_twice(dummy_projects, dummy_users, authorized_client):
    data = {
        'ids': [2, 3]
    }

    res = authorized_client.post("/projects/1/addpersonnel", json=data)
    project = authorized_client.get("/projects/1")
    project = project.json()

    assert len(project['personnel']) == 3
    assert project['personnel'][1]['id'] == '2'
    assert project['personnel'][2]['id'] == '3'
    assert res.status_code == 201

    res = authorized_client.post("/projects/1/addpersonnel", json=data)

    assert res.status_code == 409

# User (id:5) tries to assign users (id:2, 3) to someone else's (id:1) project (id:1)
def test_assign_no_access(dummy_projects, dummy_users, authorized_other_client):
    data = {
        'ids': [2, 3]
    }

    res = authorized_other_client.post("/projects/1/addpersonnel", json=data)
    assert res.status_code == 403

# User (id:1) removes users (id:2, 3) from their own project (id:1)
def test_remove(dummy_projects, dummy_users, authorized_client):
    # Assign
    data = {
        'ids': [2, 3]
    }

    res = authorized_client.post("/projects/1/addpersonnel", json=data)
    project = authorized_client.get("/projects/1")
    project = project.json()

    assert len(project['personnel']) == 3
    assert project['personnel'][1]['id'] == '2'
    assert project['personnel'][2]['id'] == '3'
    assert res.status_code == 201

    # Remove
    res = authorized_client.post("/projects/1/removepersonnel", json=data)
    project = authorized_client.get("/projects/1")
    project = project.json()

    assert len(project['personnel']) == 1
    assert res.status_code == 204

# Admin (id:5) removes users (id:2, 3) from user's (id:1) project (id:1)
def test_remove_by_admin(dummy_projects, dummy_users, authorized_client_admin):
    # Assign
    data = {
        'ids': [2, 3]
    }

    res = authorized_client_admin.post("/projects/1/addpersonnel", json=data)
    project = authorized_client_admin.get("/projects/1")
    project = project.json()

    assert len(project['personnel']) == 3
    assert project['personnel'][1]['id'] == '2'
    assert project['personnel'][2]['id'] == '3'
    assert res.status_code == 201

    # Remove
    res = authorized_client_admin.post("/projects/1/removepersonnel", json=data)
    project = authorized_client_admin.get("/projects/1")
    project = project.json()

    assert len(project['personnel']) == 1
    assert res.status_code == 204

# User (id:1) attempts to remove users (id:2, 3) from non-existent project
def test_remove_wrong_project_id(dummy_projects, dummy_users, authorized_client):
    data = {
        'ids': [2, 3]
    }

    res = authorized_client.post("/projects/10/removepersonnel", json=data)

    assert res.status_code == 404

# User (id:1) removes non-existent users from their own project (id:1)
def test_remove_wrong_users(dummy_projects, dummy_users, authorized_client):
    data = {
        'ids': [20, 30]
    }

    res = authorized_client.post("/projects/1/removepersonnel", json=data)

    assert res.status_code == 404

# User (id:1) tries to remove users (id:2, 3) from their own project (id:1) twice
def test_remove_twice(dummy_projects, dummy_users, authorized_client):
    data = {
        'ids': [2, 3]
    }

    # Assign
    res = authorized_client.post("/projects/1/addpersonnel", json=data)
    project = authorized_client.get("/projects/1")
    project = project.json()

    assert len(project['personnel']) == 3
    assert project['personnel'][1]['id'] == '2'
    assert project['personnel'][2]['id'] == '3'
    assert res.status_code == 201

    # Remove
    res = authorized_client.post("/projects/1/removepersonnel", json=data)
    project = authorized_client.get("/projects/1")
    project = project.json()

    assert len(project['personnel']) == 1
    assert res.status_code == 204

    # Remove second time
    res = authorized_client.post("/projects/1/removepersonnel", json=data)

    assert res.status_code == 404

# User (id:5) tries to remove users (id:2, 3) from someone else's (id:1) project (id:1)
def test_remove_no_access(dummy_projects, dummy_users, authorized_other_client):
    data = {
        'ids': [2, 3]
    }

    res = authorized_other_client.post("/projects/1/removepersonnel", json=data)
    assert res.status_code == 403

# User (id:2) creates a ticket to project (id:2)
def test_create_ticket(dummy_projects, authorized_other_client):
    data = {
        'caption': 'ticket1', 
        'description': 'description1', 
        'priority': 0, 
        'category': 'bug'
    }

    res = authorized_other_client.post('/projects/2/newticket', json=data)
    project = authorized_other_client.get('/projects/2')
    project = project.json()

    assert res.status_code == 201
    assert project['tickets'][0]['caption'] == data['caption']
    assert project['tickets'][0]['description'] == data['description']
    assert project['tickets'][0]['priority'] == data['priority']
    assert project['tickets'][0]['category'] == data['category']

# User (id:2) creates a ticket to non-existent project
def test_create_ticket_wrong_id(dummy_projects, authorized_other_client):
    data = {
        'caption': 'ticket1', 
        'description': 'description1', 
        'priority': 0, 
        'category': 'bug'
    }

    res = authorized_other_client.post('/projects/20/newticket', json=data)

    assert res.status_code == 404

# User (id:2) creates a ticket to project (id:2); Wrong data
def test_create_ticket_wrong_data(dummy_projects, authorized_other_client):
    data = {
        'caption': 'ticket1', 
        'description': 'description1', 
        'priority': 'HIGHEST', 
        'category': True
    }

    res = authorized_other_client.post('/projects/20/newticket', json=data)

    assert res.status_code == 422