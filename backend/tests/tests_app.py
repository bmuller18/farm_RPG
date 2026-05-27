import sys
from pathlib import Path

# Permite importar app al ejecutar pytest desde la raíz del repo
_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app import app


def test_home():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
