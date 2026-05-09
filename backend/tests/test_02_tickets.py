import requests
import random
import string

def generate_random_tckn():
    return ''.join(random.choices(string.digits, k=11))

def test_ticket_flow(base_url, employee_session):

    # 1. Müşteri bilet alır
    tckn = generate_random_tckn()
    res = requests.post(f"{base_url}/tickets/new", json={
        "tckn": tckn,
        "prefix": "B"
    })
    assert res.status_code == 201
    ticket_data = res.json()["ticket"]
    assert "ticket_number" in ticket_data
    
    # 2. Biletin kuyrukta olduğunu kontrol et
    res = employee_session.get(f"{base_url}/tickets/queue")
    assert res.status_code == 200
    queue = res.json()["queue"]
    
    # Kuyrukta biletin beklediğini onayla
    found = any(t["ticket_number"] == ticket_data["ticket_number"] for t in queue)
    assert found is True
    
    # 3. Çalışan müşteriyi çağırır
    res = employee_session.post(f"{base_url}/tickets/call-next", params={"counter": 3})
    assert res.status_code == 200
    called_ticket = res.json()["ticket"]
    ticket_id = called_ticket.get("id") or called_ticket.get("_id") # Beanie id'yi 'id' veya '_id' olarak dönebilir.

    
    # 4. Aktif biletin o bilet olduğunu doğrula
    res = employee_session.get(f"{base_url}/tickets/active")
    assert res.status_code == 200
    active_ticket = res.json()["active"]
    assert active_ticket["ticket_number"] == called_ticket["ticket_number"]
    
    # 5. Müşteri ile işlemi tamamla
    res = employee_session.post(f"{base_url}/tickets/{ticket_id}/complete")
    assert res.status_code == 200
    assert res.json()["message"] == "İşlem tamamlandı."
