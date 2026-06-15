import pytest
from fastapi.testclient import TestClient
from app.main import app


def fake_user():
    return {
        "uid": "test-user",
        "business_id": "test-business",
        "role": "OWNER"
    }


class FakeDoc:
    def __init__(self, data=None, doc_id="test-id"):
        self._data = data or {}
        self.id = doc_id

    @property
    def exists(self):
        return True

    def to_dict(self):
        return self._data


class FakeQuery:
    def where(self, *args, **kwargs):
        return self

    def stream(self):
        return []


class FakeCollection:
    def __init__(self):
        self.data = {}

    def where(self, *args, **kwargs):
        return FakeQuery()

    def stream(self):
        return []

    def add(self, data):
        class Doc:
            id = "test-id"
        return (None, Doc())

    def document(self, doc_id=None):
        class Ref:
            def get(self_inner):
                return FakeDoc({})
            def update(self_inner, *args, **kwargs):
                pass
        return Ref()


class FakeDB:
    def collection(self, name):
        return FakeCollection()


@pytest.fixture(autouse=True)
def client():
    import app.firebase as fb
    fb.db = FakeDB()

    from app.core import security
    app.dependency_overrides[security.get_current_user] = fake_user

    yield TestClient(app)

    app.dependency_overrides.clear()