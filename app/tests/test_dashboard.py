def test_dashboard(client):
    r = client.get("/dashboard")

    assert r.status_code == 200

    data = r.json()

    assert "active_orders" in data
    assert "revenue" in data
    assert "profit" in data