from uuid import UUID

from app.db.session import SessionLocal
from app.models import GenerationRun


def project_payload():
    return {"name": "Study Planner", "description": "A planning tool for students to organize courses, tasks, and deadlines."}


def test_health_and_validation(client):
    assert client.get("/api/v1/health").json()["status"] == "ok"
    invalid = client.post("/api/v1/projects", json={"name": "x", "description": "short"})
    assert invalid.status_code == 422
    assert client.post("/api/v1/projects", json={"name": "", "description": "A valid enough description for this request."}).status_code == 422
    assert client.post("/api/v1/projects", json={"name": "Valid", "description": "x" * 10001}).status_code == 422


def test_full_mock_generation_flow(client):
    created = client.post("/api/v1/projects", json=project_payload())
    assert created.status_code == 201
    project_id = created.json()["id"]
    assert client.get(f"/api/v1/projects/{project_id}").json()["status"] == "draft"
    run = client.post(f"/api/v1/projects/{project_id}/analyze")
    assert run.status_code == 200
    assert run.json()["status"] == "completed"
    detail = client.get(f"/api/v1/projects/{project_id}").json()
    assert detail["status"] == "completed"
    assert detail["requirement_count"] >= 3
    assert detail["task_count"] >= 5
    assert detail["feature_count"] >= 3
    assert detail["api_count"] >= 3
    assert detail["document_count"] == 1
    assert len(client.get(f"/api/v1/projects/{project_id}/requirements").json()) >= 3
    assert client.get(f"/api/v1/projects/{project_id}/architecture").json()["style"] == "Modular monolith"
    assert len(client.get(f"/api/v1/projects/{project_id}/database").json()) >= 3
    tasks = client.get(f"/api/v1/projects/{project_id}/tasks").json()
    assert all(task["task_key"] for task in tasks)
    assert any(task["dependency_ids"] for task in tasks)
    assert any(task["assignee_id"] and task["owner_name"] for task in tasks)
    team = client.get(f"/api/v1/projects/{project_id}/team").json()
    assert len(team) >= 5
    assert any(role["task_count"] > 0 for role in team)
    assert len(client.get(f"/api/v1/projects/{project_id}/documentation").json()) == 1
    assert client.get(f"/api/v1/projects/{project_id}/generation-runs").json()[0]["status"] == "completed"
    assert client.get(f"/api/v1/projects/{project_id}/export?format=markdown").headers["content-type"].startswith("text/markdown")
    assert client.get(f"/api/v1/projects/{project_id}/export?format=json").headers["content-type"].startswith("application/json")


def test_missing_project_and_bad_export(client):
    missing = "00000000-0000-0000-0000-000000000000"
    assert client.get(f"/api/v1/projects/{missing}").status_code == 404
    assert client.get("/api/v1/projects/not-a-uuid").status_code == 422
    assert client.get(f"/api/v1/projects/{missing}/export?format=xml").status_code in (400, 404, 422)


def test_invalid_export_format_and_safe_generation_failure(client, monkeypatch):
    created = client.post("/api/v1/projects", json=project_payload())
    project_id = created.json()["id"]
    assert client.get(f"/api/v1/projects/{project_id}/export?format=xml").status_code == 400

    def fail_generation(*_args, **_kwargs):
        raise RuntimeError("secret database path should not reach the client")

    monkeypatch.setattr("app.services.planning_service.PlanningOrchestrator.run", fail_generation)
    response = client.post(f"/api/v1/projects/{project_id}/analyze")
    assert response.status_code == 422
    assert "secret database path" not in response.text
    runs = client.get(f"/api/v1/projects/{project_id}/generation-runs").json()
    assert runs[0]["status"] == "failed"
    assert "secret database path" not in (runs[0]["error_message"] or "")


def test_duplicate_generation_is_rejected(client):
    created = client.post("/api/v1/projects", json=project_payload())
    project_id = UUID(created.json()["id"])
    db = SessionLocal()
    run = GenerationRun(project_id=project_id, run_type="full", status="running")
    db.add(run)
    db.commit()
    try:
        response = client.post(f"/api/v1/projects/{project_id}/analyze")
        assert response.status_code == 409
    finally:
        db.delete(run)
        db.commit()


def test_workspace_seed_and_intelligence_relationships(client):
    workspace = client.get("/api/v1/projects/workspace")
    assert workspace.status_code == 200
    payload = workspace.json()
    assert len(payload["projects"]) >= 6
    assert payload["metrics"]["people"] >= 3
    sara = next(person for person in payload["people"] if person["name"] == "Sara Rahimi")
    assert sara["project_count"] >= 2
    project = next(item for item in payload["projects"] if item["name"] == "Food Delivery Platform")
    project_id = project["id"]
    assert client.get(f"/api/v1/projects/{project_id}/people").json()
    assert client.get(f"/api/v1/projects/{project_id}/activities").json()
    assert client.get(f"/api/v1/projects/{project_id}/milestones").json()
    assert client.get(f"/api/v1/projects/{project_id}/risks").json()
    assert client.get(f"/api/v1/projects/{project_id}/features").json()
    assert client.get(f"/api/v1/projects/{project_id}/apis").json()
    traceability = client.get(f"/api/v1/projects/{project_id}/traceability")
    assert traceability.status_code == 200
    assert all(item["feature_name"] for item in traceability.json())
    report = client.post(f"/api/v1/projects/{project_id}/reports?report_type=architecture")
    assert report.status_code == 201
    assert report.json()["project_id"] == project_id
    report_id = report.json()["id"]
    assert client.get(f"/api/v1/projects/reports/{report_id}").json()["title"] == "Architecture Analysis"
    assert client.patch(f"/api/v1/projects/reports/{report_id}", json={"status": "archived"}).json()["status"] == "archived"
    other_project = next(item for item in payload["projects"] if item["id"] != project_id)
    comparison = client.get(f"/api/v1/projects/compare?ids={project_id}&ids={other_project['id']}")
    assert comparison.status_code == 200
    assert len(comparison.json()) == 2
    updated = client.patch(f"/api/v1/projects/{project_id}", json={"status": "planning", "reason": "Reviewing integration scope"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "planning"
    search = client.get("/api/v1/projects/search?q=Sara")
    assert search.status_code == 200
    assert search.json()["groups"]["people"]
    module_search = client.get("/api/v1/projects/search?q=Next.js")
    assert module_search.status_code == 200
    insights = client.get(f"/api/v1/projects/{project_id}/insights")
    assert insights.status_code == 200
    assert {item["kind"] for item in insights.json()} >= {"architecture", "delivery", "requirements", "team", "risk"}


def test_public_people_reports_seed_and_regeneration_contracts(client):
    people = client.get("/api/v1/people")
    assert people.status_code == 200
    sara = next(item for item in people.json() if item["name"] == "Sara Rahimi")
    person_projects = client.get(f"/api/v1/people/{sara['id']}/projects")
    assert person_projects.status_code == 200
    assert len(person_projects.json()) >= 2

    reports = client.get("/api/v1/reports")
    assert reports.status_code == 200
    assert len(reports.json()) >= 6
    assert all(item["project_name"] for item in reports.json())

    project = next(item for item in client.get("/api/v1/projects").json() if item["name"] == "University Course Management")
    before = client.get(f"/api/v1/projects/{project['id']}/reports").json()
    seeded = client.post(f"/api/v1/projects/{project['id']}/seed-demo")
    assert seeded.status_code == 200
    after = client.get(f"/api/v1/projects/{project['id']}/reports").json()
    assert len(after) >= len(before)
    assert len(after) >= 4
    seeded_again = client.post(f"/api/v1/projects/{project['id']}/seed-demo")
    assert seeded_again.status_code == 200
    assert len(client.get(f"/api/v1/projects/{project['id']}/reports").json()) == len(after)

    source = next(item for item in after if item["report_type"] == "architecture")
    regenerated = client.post(f"/api/v1/projects/{project['id']}/reports/{source['id']}/regenerate")
    assert regenerated.status_code == 201
    assert regenerated.json()["title"] == source["title"]


def test_project_deletion_removes_project_but_not_shared_people(client):
    created = client.post("/api/v1/projects", json={"name": "Deletion Fixture", "description": "A temporary project used to verify safe project deletion and relationship cleanup."})
    assert created.status_code == 201
    project_id = created.json()["id"]
    assert client.delete(f"/api/v1/projects/{project_id}").status_code == 204
    assert client.get(f"/api/v1/projects/{project_id}").status_code == 404
