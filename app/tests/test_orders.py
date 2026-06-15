def test_create_order(client):
    r = client.post("/orders", json={
        "title": "Test order",
        "client_name": "Client A",
        "budget": 100
    })

    assert r.status_code == 200
    assert "id" in r.json()


def test_get_orders(client):
    r = client.get("/orders")

    assert r.status_code == 200
    assert isinstance(r.json(), list)