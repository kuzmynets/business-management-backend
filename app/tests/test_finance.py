def test_finance_dashboard(client):
    r = client.get("/finance")

    assert r.status_code == 200

    data = r.json()
    assert "items" in data
    assert "summary" in data