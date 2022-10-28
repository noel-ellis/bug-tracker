# Tests should be independable of one another

# Get all comments
def test_get_all(dummy_comments, client):
    res = client.get('/comments/')
    comments = res.json()

    assert res.status_code == 200
    assert comments[0]['body_text'] == dummy_comments[0]['body_text']
    assert comments[0]['creator_id'] == dummy_comments[0]['creator_id']
    assert comments[0]['created_at'] == dummy_comments[0]['created_at']

# Get one comment
def test_get_one(dummy_comments, client):
    res = client.get('/comments/1')
    comment = res.json()

    assert res.status_code == 200
    assert comment['comment']['body_text'] == dummy_comments[0]['body_text']
    assert comment['comment']['creator_id'] == dummy_comments[0]['creator_id']
    assert comment['comment']['created_at'] == dummy_comments[0]['created_at']

# Get one comment
def test_get_one_wrong_id(dummy_comments, client):
    res = client.get('/comments/10')

    assert res.status_code == 404

# Edit comment
def test_edit(dummy_comments, authorized_client):
    data = {
        'body_text': 'edited'
    }
    res = authorized_client.put('comments/1', json=data)

    assert res.status_code == 205
    assert res.json()['body_text'] == data['body_text']

# Edit comment; wrong id
def test_edit_wrong_id(dummy_comments, authorized_client):
    data = {
        'body_text': 'edited'
    }
    res = authorized_client.put('comments/10', json=data)

    assert res.status_code == 404

# Edit comment; no access
def test_edit_no_access(dummy_comments, authorized_other_client):
    data = {
        'body_text': 'edited'
    }
    res = authorized_other_client.put('comments/1', json=data)

    assert res.status_code == 403

# Edit comment; wrong data
def test_edit_wrong_data(dummy_comments, authorized_client):
    data = {
        'body_text': ['edited', 'wrong']
    }
    res = authorized_client.put('comments/1', json=data)

    assert res.status_code == 422

# Delete comment
def test_delete(dummy_comments, authorized_client):
    res = authorized_client.delete('comments/1')

    assert res.status_code == 204

# Delete comment; wrong id
def test_delete_wrong_id(dummy_comments, authorized_client):
    res = authorized_client.delete('comments/10')

    assert res.status_code == 404

# Delete comment; no access
def test_delete_no_access(dummy_comments, authorized_other_client):
    res = authorized_other_client.delete('comments/1')

    assert res.status_code == 403