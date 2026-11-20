"""API tests for repository, scan, and finding routes."""


def test_create_and_list_repository(client):
    payload = {
        "github_owner": "danishkumar26",
        "github_repo": "secure-open-source-devops",
        "html_url": "https://github.com/danishkumar26/secure-open-source-devops",
        "description": "A DevSecOps platform.",
        "default_branch": "main",
        "is_private": False,
    }
    response = client.post("/repositories", json=payload)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["full_name"] == "danishkumar26/secure-open-source-devops"
    assert body["id"] == 1

    # Duplicate is rejected.
    response = client.post("/repositories", json=payload)
    assert response.status_code == 409

    response = client.get("/repositories")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_and_delete_repository(client):
    client.post(
        "/repositories",
        json={
            "github_owner": "owner",
            "github_repo": "repo",
            "html_url": "https://github.com/owner/repo",
        },
    )
    response = client.get("/repositories/1")
    assert response.status_code == 200
    assert response.json()["full_name"] == "owner/repo"

    response = client.get("/repositories/42")
    assert response.status_code == 404

    response = client.delete("/repositories/1")
    assert response.status_code == 204

    response = client.get("/repositories")
    assert response.json() == []


def test_trigger_scan_and_findings(client):
    client.post(
        "/repositories",
        json={
            "github_owner": "owner",
            "github_repo": "repo",
            "html_url": "https://github.com/owner/repo",
        },
    )
    response = client.post("/repositories/1/scans")
    assert response.status_code == 202, response.text
    scan = response.json()
    assert scan["status"] == "pending"
    assert scan["trigger"] == "manual"

    response = client.get("/repositories/1/scans")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get("/repositories/1/scans/1/findings")
    assert response.status_code == 200
    assert response.json() == []
