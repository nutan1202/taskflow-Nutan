"""End-to-end API integration tests for TaskFlow."""

from fastapi.testclient import TestClient


def _register(
    client: TestClient,
    *,
    name: str,
    email: str,
    password: str,
) -> dict:
    response = client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert response.status_code == 201
    return response.json()


def _login(client: TestClient, *, email: str, password: str) -> dict:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_register_happy_path(client: TestClient) -> None:
    data = _register(
        client,
        name="Alice",
        email="alice@example.com",
        password="password123",
    )
    assert "token" in data
    assert data["user"]["email"] == "alice@example.com"
    assert data["user"]["name"] == "Alice"


def test_login_happy_path(client: TestClient) -> None:
    _register(
        client,
        name="Bob",
        email="bob@example.com",
        password="password123",
    )
    data = _login(client, email="bob@example.com", password="password123")
    assert "token" in data
    assert data["user"]["email"] == "bob@example.com"


def test_unauthorized_access_to_protected_route_returns_401(client: TestClient) -> None:
    response = client.get("/projects")
    assert response.status_code == 401
    assert response.json() == {"error": "unauthorized"}


def test_validation_error_returns_exact_400_shape(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={"name": "Missing Email", "password": "password123"},
    )
    assert response.status_code == 400
    assert response.json() == {
        "error": "validation failed",
        "fields": {"email": "is required"},
    }


def test_only_project_owner_or_task_creator_can_delete_task(client: TestClient) -> None:
    owner = _register(
        client,
        name="Owner",
        email="owner@example.com",
        password="password123",
    )
    member = _register(
        client,
        name="Member",
        email="member@example.com",
        password="password123",
    )
    outsider = _register(
        client,
        name="Outsider",
        email="outsider@example.com",
        password="password123",
    )
    owner_token = owner["token"]
    member_token = member["token"]
    outsider_token = outsider["token"]
    member_user_id = member["user"]["id"]

    project_response = client.post(
        "/projects",
        headers=_auth_header(owner_token),
        json={"name": "Delete Permission Project", "description": "test"},
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    # Bootstrap access for member by assigning one task from owner.
    bootstrap_task = client.post(
        f"/projects/{project_id}/tasks",
        headers=_auth_header(owner_token),
        json={
            "title": "Bootstrap member access",
            "description": "owner-created",
            "priority": "medium",
            "assignee_id": member_user_id,
        },
    )
    assert bootstrap_task.status_code == 201

    # Member now creates their own task in the same project.
    member_task = client.post(
        f"/projects/{project_id}/tasks",
        headers=_auth_header(member_token),
        json={
            "title": "Member-owned task",
            "description": "creator should be member",
            "priority": "high",
            "assignee_id": member_user_id,
        },
    )
    assert member_task.status_code == 201
    member_task_id = member_task.json()["id"]

    forbidden_delete = client.delete(
        f"/tasks/{member_task_id}",
        headers=_auth_header(outsider_token),
    )
    assert forbidden_delete.status_code == 403
    assert forbidden_delete.json() == {"error": "forbidden"}

    creator_delete = client.delete(
        f"/tasks/{member_task_id}",
        headers=_auth_header(member_token),
    )
    assert creator_delete.status_code == 204


def test_project_stats_returns_expected_count_buckets(client: TestClient) -> None:
    user = _register(
        client,
        name="Stats User",
        email="stats@example.com",
        password="password123",
    )
    token = user["token"]
    user_id = user["user"]["id"]

    project_response = client.post(
        "/projects",
        headers=_auth_header(token),
        json={"name": "Stats Project", "description": "stats"},
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    create_payloads = [
        {"title": "Todo task", "priority": "low", "assignee_id": user_id},
        {"title": "In progress task", "priority": "medium", "assignee_id": user_id},
        {"title": "Done task", "priority": "high", "assignee_id": user_id},
    ]
    task_ids: list[str] = []
    for payload in create_payloads:
        created = client.post(
            f"/projects/{project_id}/tasks",
            headers=_auth_header(token),
            json=payload,
        )
        assert created.status_code == 201
        task_ids.append(created.json()["id"])

    assert len(task_ids) == 3
    client.patch(
        f"/tasks/{task_ids[1]}",
        headers=_auth_header(token),
        json={"status": "in_progress"},
    )
    client.patch(
        f"/tasks/{task_ids[2]}",
        headers=_auth_header(token),
        json={"status": "done"},
    )

    stats = client.get(
        f"/projects/{project_id}/stats",
        headers=_auth_header(token),
    )
    assert stats.status_code == 200
    body = stats.json()
    assert body["project_id"] == project_id
    assert body["counts_by_status"]["todo"] == 1
    assert body["counts_by_status"]["in_progress"] == 1
    assert body["counts_by_status"]["done"] == 1


def test_projects_pagination_returns_stable_structure(client: TestClient) -> None:
    user = _register(
        client,
        name="Pager",
        email="pager@example.com",
        password="password123",
    )
    token = user["token"]

    for i in range(3):
        response = client.post(
            "/projects",
            headers=_auth_header(token),
            json={"name": f"Project {i}", "description": "pagination"},
        )
        assert response.status_code == 201

    page_1 = client.get(
        "/projects?page=1&limit=2",
        headers=_auth_header(token),
    )
    assert page_1.status_code == 200
    body = page_1.json()
    assert set(body.keys()) == {"projects", "page", "limit", "total"}
    assert body["page"] == 1
    assert body["limit"] == 2
    assert body["total"] >= 3
    assert len(body["projects"]) <= 2
