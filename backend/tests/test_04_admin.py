import requests

def test_admin_stats_and_logs(base_url, admin_session):
    # 1. İstatistikleri Kontrol Et
    res = admin_session.get(f"{base_url}/tickets/stats")
    assert res.status_code == 200
    stats = res.json()
    assert "waiting" in stats
    assert "serving" in stats
    assert "completed" in stats
    assert "total" in stats
    
    # 2. Sistem Loglarını Kontrol Et
    res = admin_session.get(f"{base_url}/admin/logs")
    assert res.status_code == 200
    logs = res.json()
    assert isinstance(logs, list)

def test_public_endpoints(base_url):
    # Public (şifresiz) kuyruk ekranı testi
    res = requests.get(f"{base_url}/public/tickets")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    res = requests.get(f"{base_url}/public/last-called")
    assert res.status_code in (200, 404) # Olabilir de olmayabilir de
