import requests
import concurrent.futures
import random
import string

def generate_random_tckn():
    return ''.join(random.choices(string.digits, k=11))

def take_ticket(base_url):

    """Müşteri simülasyonu: Bilet alır"""
    tckn = generate_random_tckn()
    res = requests.post(f"{base_url}/tickets/new", json={
        "tckn": tckn,
        "prefix": "C"
    })
    return res.status_code

def test_concurrent_ticket_creation(base_url):
    """Aynı anda 20 müşterinin bilet almasını simüle eder."""
    num_requests = 20
    results = []
    
    # ThreadPool ile aynı anda çoklu istek at
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(take_ticket, base_url) for _ in range(num_requests)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    # Tüm biletlerin başarıyla oluşturulduğunu kontrol et
    assert all(status == 201 for status in results)
    assert len(results) == num_requests
