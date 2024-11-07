import pytest
from fastapi.testclient import TestClient
from src.main import app
from pathlib import Path


@pytest.fixture
def client():
    """Test client fixture for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_bill_url():
    """Sample bill URL for testing"""
    return "https://www.parl.ca/legisinfo/en/bill/44-1/s-2"


@pytest.fixture
def mock_bill_html():
    """Load mock bill HTML from file"""
    mock_path = Path(__file__).parent / "mocks" / "bill_page.html"
    if mock_path.exists():
        return mock_path.read_text()
    return """
    <html>
        <body>
            <div class="bill-card-type">Senate Public Bill</div>
            <div class="attribute-status-name">In Progress</div>
            <div class="bill-identity">
                <a href="/members/1234">John Doe</a>
            </div>
            <div class="session-date-range">2024-01-01</div>
        </body>
    </html>
    """
