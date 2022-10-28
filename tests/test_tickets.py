# Tests should be independable of one another

# Get all tickets
def test_get_all(client, dummy_tickets):
    res = client.get("/tickets/")
    tickets = res.json()
    
    assert res.status_code == 200
    for i in range(0, 2):
        assert tickets[i]['caption'] == dummy_tickets[i]['caption']
        assert tickets[i]['description'] == dummy_tickets[i]['description']
        assert tickets[i]['priority'] == dummy_tickets[i]['priority']
        assert tickets[i]['category'] == dummy_tickets[i]['category']

# Get one ticket
def test_get_one(client, dummy_tickets):
    res = client.get("/tickets/1")
    ticket = res.json()

    assert res.status_code == 200
    assert ticket['ticket']['caption'] == dummy_tickets[0]['caption']
    assert ticket['ticket']['description'] == dummy_tickets[0]['description']
    assert ticket['ticket']['priority'] == dummy_tickets[0]['priority']
    assert ticket['ticket']['category'] == dummy_tickets[0]['category']

# Get non-existent ticket
def test_get_one_wrong_id(client, dummy_tickets):
    res = client.get("/tickets/10")

    assert res.status_code == 404

# Edit ticket
def test_edit(dummy_tickets, authorized_client):
    data = {
        'caption': 'edited',
        'description': 'edited',
        'priority': 2,
        'status': 'edited',
        'category': 'edited'
    }
    res = authorized_client.put("/tickets/1", json=data)
    ticket = res.json()

    assert res.status_code == 205
    assert ticket['caption'] == data['caption']
    assert ticket['description'] == data['description']
    assert ticket['priority'] == data['priority']
    assert ticket['category'] == data['category']
    assert ticket['status'] == data['status']

# Edit non-existent ticket
def test_edit_wrong_id(dummy_tickets, authorized_client):
    data = {
        'caption': 'edited',
        'description': 'edited',
        'priority': 2,
        'status': 'edited',
        'category': 'edited'
    }
    res = authorized_client.put("/tickets/10", json=data)

    assert res.status_code == 404

# Edit ticket; no access
def test_edit_no_access(dummy_tickets, authorized_other_client):
    data = {
        'caption': 'edited',
        'description': 'edited',
        'priority': 2,
        'status': 'edited',
        'category': 'edited'
    }
    res = authorized_other_client.put("/tickets/1", json=data)

    assert res.status_code == 403

# Edit ticket; wrong data
def test_edit_wrong_data(dummy_tickets, authorized_other_client):
    data = {
        'caption': True,
        'description': 'edited',
        'priority': 'high',
        'status': 'edited',
        'category': 'edited'
    }
    res = authorized_other_client.put("/tickets/1", json=data)

    assert res.status_code == 422

# Delete ticket
def test_delete(dummy_tickets, authorized_client):
    res = authorized_client.delete("/tickets/1")

    assert res.status_code == 204

# Delete non-existent ticket
def test_delete_wrong_id(dummy_tickets, authorized_client):
    res = authorized_client.delete("/tickets/10")

    assert res.status_code == 404

# Delete ticket, no access
def test_delete_no_access(dummy_tickets, authorized_other_client):
    res = authorized_other_client.delete("/tickets/1")

    assert res.status_code == 403

# Create a new comment
def test_comment(dummy_tickets, authorized_client):
    data = {
        'body_text': 'test comment'
    }
    res = authorized_client.post("/tickets/1/comment", json=data)

    assert res.status_code == 201
    assert res.json()['body_text'] == data['body_text']

# Comment non-existent ticket
def test_comment_wrong_id(dummy_tickets, authorized_client):
    data = {
        'body_text': 'test comment'
    }
    res = authorized_client.post("/tickets/10/comment", json=data)

    assert res.status_code == 404

# Comment; Wrong data
def test_comment_wrong_data(dummy_tickets, authorized_client):
    data = {
        'body_text': ['wrong', 'format']
    }
    res = authorized_client.post("/tickets/1/comment", json=data)

    assert res.status_code == 422