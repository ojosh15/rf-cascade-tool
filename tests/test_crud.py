import json
from datetime import datetime
from app.database import Session

def test_get_projects(test_app):
    response = test_app.get("/api/v1/projects")
    assert response.status_code == 200
    assert response.json() == []

def test_create_project(test_app):
    payload = {"name": "CAVALL", "description": "test project"}
    response = test_app.post("/api/v1/projects",content=json.dumps(payload))
    assert response.status_code == 201
    object = response.json()
    assert object['id']== 1
    assert object["name"] == payload["name"]
    assert object["description"] == payload["description"]
    created_at = datetime.strptime(object["created_at"], '%Y-%m-%dT%H:%M:%S.%f')
    modified_at = datetime.strptime(object["modified_at"], '%Y-%m-%dT%H:%M:%S.%f')
    assert created_at == modified_at

def test_create_path(test_app):
    payload = {"input": "J2", "output": "J8", "description": "A test path"}
    project_id = 1
    response = test_app.post(f"/api/v1/projects/{project_id}/paths", content=json.dumps(payload))
    assert response.status_code == 201
    object = response.json()
    assert object['id']== 1
    assert object['input']== payload["input"]
    assert object['output']== payload["output"]
    assert object['description']== payload["description"]
    created_at = datetime.strptime(object["created_at"], '%Y-%m-%dT%H:%M:%S.%f')
    modified_at = datetime.strptime(object["modified_at"], '%Y-%m-%dT%H:%M:%S.%f')
    assert created_at == modified_at

def test_get_component_types(test_app):
    pass

def test_create_component(test_app):
    payload = {
        "model": "CA0618-2515",
        "manufacturer": "Ciao Wireless",
        "type_id": 1,
        "source": "simulated",
        "start_freq": 0,
        "stop_freq": 18e9,
        "gain": None,
        "nf": None,
        "ip2": None,
        "ip3": None,
        "p1db": None,
        "max_input": None,
        "is_active": True,
        "is_variable": False,
        "description": "25 dB gain amplifier"
    }
    response = test_app.post("/api/v1/components", content=json.dumps(payload))
    # assert response.status_code == 201
    assert response.content == ""