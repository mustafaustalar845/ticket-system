import pytest
import requests
import random
import string

BASE_URL = "http://localhost:8000/api"

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def generate_random_tckn():
    return ''.join(random.choices(string.digits, k=11))

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def admin_credentials():
    username = f"admin_{generate_random_string(5)}"
    password = "AdminPassword123"
    
    # Register admin
    requests.post(f"{BASE_URL}/auth/register", json={
        "username": username,
        "password": password,
        "full_name": "Test Admin",
        "role": "admin"
    })
    
    return {"username": username, "password": password}

@pytest.fixture(scope="session")
def admin_token(base_url, admin_credentials):
    res = requests.post(f"{base_url}/auth/login", json=admin_credentials)
    return res.json()["access_token"]

@pytest.fixture(scope="session")
def admin_session(base_url, admin_token):
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {admin_token}"})
    return session

@pytest.fixture(scope="session")
def employee_credentials(base_url, admin_session):
    username = f"emp_{generate_random_string(5)}"
    password = "EmployeePassword123"
    
    # Admin creates an employee user
    res = admin_session.post(f"{base_url}/admin/users", json={
        "username": username,
        "password": password,
        "full_name": "Test Employee",
        "role": "employee"
    })
    
    return {"username": username, "password": password}

@pytest.fixture(scope="session")
def employee_token(base_url, employee_credentials):
    res = requests.post(f"{base_url}/auth/login", json=employee_credentials)
    return res.json()["access_token"]

@pytest.fixture(scope="session")
def employee_session(base_url, employee_token):
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {employee_token}"})
    return session
