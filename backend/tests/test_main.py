# backend/tests/test_main.py
import pytest
from httpx import AsyncClient
# To make this import work, Pytest needs to understand the project structure.
# We'll ensure `main.py` is in the `backend` directory and run pytest from `backend`.
# If `main.py` is `backend/main.py` and tests are in `backend/tests/test_main.py`,
# the import should be `from ..main import app` or adjust pythonpath.
# For simplicity with initial setup, let's assume pytest is run from `backend/`
# and can see `main.py` in its root.
# If `main.py` is at `backend/src/main.py`, then `from ..src.main import app`
# Let's assume main.py is directly in `backend/` for now.
from main import app # Adjusted: Assuming main.py is in the same dir as where pytest is run (backend/)

@pytest.mark.asyncio
async def test_read_root():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from SoloRelms Backend"} 