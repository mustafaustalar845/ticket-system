import requests
import random
import string

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def test_user_registration(base_url):

    username = f"user_{generate_random_string()}"
    res = requests.post(f"{base_url}/auth/register", json={
        "username": username,
        "password": "Password123",
        "full_name": "New User",
        "role": "employee"
    })
    assert res.status_code == 201
    data = res.json()
    assert "message" in data
    assert data["user"]["username"] == username

def test_user_login(base_url):
    username = f"user_{generate_random_string()}"
    password = "Password123"
    # Register
    requests.post(f"{base_url}/auth/register", json={
        "username": username,
        "password": password,
        "full_name": "New User",
        "role": "employee"
    })
    
    # Login
    res = requests.post(f"{base_url}/auth/login", json={
        "username": username,
        "password": password
    })
    
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
