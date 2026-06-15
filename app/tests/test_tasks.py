def test_create_task(client):
    order = client.post("/orders", json={
        "title": "Order"
    }).json()

    r = client.post("/tasks", json={
        "title": "Task",
        "order_id": order["id"]
    })

    assert r.status_code == 200


def test_get_tasks(client):
    r = client.get("/tasks")

    assert r.status_code == 200