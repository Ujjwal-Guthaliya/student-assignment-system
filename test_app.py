import pytest
import os
import tempfile

from app import app, create_database


@pytest.fixture
def client():

    db_fd, db_path = tempfile.mkstemp()

    app.config["TESTING"] = True

    global_original_database = app.config.get("DATABASE")

    import app as application

    original_database = application.DATABASE

    application.DATABASE = db_path

    create_database()

    with app.test_client() as client:
        yield client

    application.DATABASE = original_database

    os.close(db_fd)
    os.unlink(db_path)


def register(client):

    return client.post(
        "/register",
        data={
            "name": "Test Student",
            "email": "test@example.com",
            "password": "123456"
        },
        follow_redirects=True
    )


def login(client):

    return client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "123456"
        },
        follow_redirects=True
    )


def test_register(client):

    response = register(client)

    assert response.status_code == 200


def test_login(client):

    register(client)

    response = login(client)

    assert response.status_code == 200


def test_add_assignment(client):

    register(client)
    login(client)

    response = client.post(
        "/add",
        data={
            "title": "Jenkins Pipeline",
            "subject": "DevOps",
            "description": "CI/CD testing",
            "deadline": "2026-09-20",
            "priority": "High"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Jenkins Pipeline" in response.data


def test_delete_assignment(client):

    register(client)
    login(client)

    client.post(
        "/add",
        data={
            "title": "Docker Test",
            "subject": "DevOps",
            "description": "Docker testing",
            "deadline": "2026-09-20",
            "priority": "Medium"
        }
    )

    import app as application

    conn = application.get_db_connection()

    assignment = conn.execute(
        "SELECT id FROM assignments"
    ).fetchone()

    conn.close()

    response = client.get(
        f"/delete/{assignment['id']}",
        follow_redirects=True
    )

    assert response.status_code == 200