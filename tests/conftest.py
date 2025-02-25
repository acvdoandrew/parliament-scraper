import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from src.main import app
import xml.etree.ElementTree as ET


@pytest.fixture
def app_client():
    """Synchronous test client"""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client():
    """Async test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_bill_url():
    """Sample bill URL for testing"""
    return "https://www.parl.ca/legisinfo/en/bill/44-1/c-422"


@pytest.fixture
def mock_bill_xml():
    """Mock bill XML response"""
    return """<?xml version="1.0" encoding="utf-8"?>
    <Bills>
        <Bill>
            <NumberCode>C-422</NumberCode>
            <BillDocumentTypeName>Private Member's Bill</BillDocumentTypeName>
            <StatusName>Outside the Order of Precedence</StatusName>
            <SponsorPersonId>105837</SponsorPersonId>
            <SponsorPersonOfficialFirstName>Bonita</SponsorPersonOfficialFirstName>
            <SponsorPersonOfficialLastName>Zarrillo</SponsorPersonOfficialLastName>
            <SponsorPersonName>Bonita Zarrillo</SponsorPersonName>
            <LatestBillEventDateTime>2024-12-02T11:00:00</LatestBillEventDateTime>
            <IsSenateBill>false</IsSenateBill>
        </Bill>
    </Bills>"""


@pytest.fixture
def mock_mp_xml():
    """Mock MP XML profile response"""
    return """<?xml version="1.0" encoding="utf-8"?>
    <Profile>
        <MemberOfParliamentRole>
            <CaucusShortName>NDP</CaucusShortName>
            <PersonOfficialFirstName>Bonita</PersonOfficialFirstName>
            <PersonOfficialLastName>Zarrillo</PersonOfficialLastName>
            <ConstituencyName>Port Moody—Coquitlam</ConstituencyName>
        </MemberOfParliamentRole>
    </Profile>"""


@pytest.fixture
def mock_senate_bill_xml():
    """Mock Senate bill XML response"""
    return """<?xml version="1.0" encoding="utf-8"?>
    <Bills>
        <Bill>
            <NumberCode>S-2</NumberCode>
            <BillDocumentTypeName>Senate Public Bill</BillDocumentTypeName>
            <StatusName>Royal Assent</StatusName>
            <SponsorPersonId>senate-1234</SponsorPersonId>
            <SponsorPersonName>Hon. Senator Smith</SponsorPersonName>
            <LatestBillEventDateTime>2024-01-01T00:00:00</LatestBillEventDateTime>
            <IsSenateBill>true</IsSenateBill>
        </Bill>
    </Bills>"""


@pytest.fixture
def mock_bill_element(mock_bill_xml):
    """Parsed bill element for testing"""
    root = ET.fromstring(mock_bill_xml)
    return root.find("Bill")
