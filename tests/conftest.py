import pytest
from fastapi.testclient import TestClient
from src.main import app
from pathlib import Path


@pytest.fixture
def client():
    """
    Test client fixture for FastAPI app
    """
    return TestClient(app)


@pytest.fixture
def sample_bill_url():
    """
    Sample bill URL for testing
    """
    return "https://www.parl.ca/legisinfo/en/bill/44-1/s-2"


@pytest.fixture
def mock_bill_html():
    """
    Load mock bill HTML from file
    """
    mock_path = Path(__file__).parent / "mocks" / "bill_page.html"
    if mock_path.exists():
        return mock_path.read_text()
    return """
    <html>
        <div class="bill-type">Senate Public Bill</div>
        <div class="status-label">In Progress</div>
        <div class="sponsor-info">
            <a href="/members/1234">John Doe</a>
        </div>
        <div class="last-updated">2024-01-01</div>
    </html>
    """
