"""Backend API regression tests for admin auth, insights taxonomy/CRUD, uploads, and contact."""
import io
import os
import re
import uuid
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values
from pypdf import PdfWriter

frontend_env = dotenv_values("/app/frontend/.env")
BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or frontend_env.get("REACT_APP_BACKEND_URL") or "").rstrip("/")
if not BASE_URL:
    raise RuntimeError("REACT_APP_BACKEND_URL is missing")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="session")
def client():
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    return session


@pytest.fixture(scope="session")
def credentials():
    path = Path("/app/memory/test_credentials.md")
    if not path.exists():
        pytest.skip("Missing /app/memory/test_credentials.md")
    content = path.read_text(encoding="utf-8")
    email = re.search(r"(?im)^\s*-\s*\*\*Email:\*\*\s*(\S+)\s*$", content)
    password = re.search(r"(?im)^\s*-\s*\*\*Password:\*\*\s*(\S+)\s*$", content)
    if not email or not password:
        pytest.skip("Admin credentials are absent from test_credentials.md")
    return {"email": email.group(1), "password": password.group(1)}


@pytest.fixture(scope="session")
def auth_headers(client, credentials):
    response = client.post(f"{API}/admin/login", json=credentials, timeout=30)
    if response.status_code != 200:
        pytest.fail(f"Admin login failed: {response.status_code} {response.text[:300]}")
    data = response.json()
    assert data["email"] == credentials["email"]
    assert isinstance(data.get("token"), str) and data["token"]
    return {"Authorization": f"Bearer {data['token']}"}


# Health and public API availability.
class TestHealth:
    def test_api_root(self, client):
        response = client.get(f"{API}/", timeout=30)
        assert response.status_code == 200
        assert response.json() == {"message": "infocure technologies API", "status": "ok"}

    def test_health(self, client):
        response = client.get(f"{API}/health", timeout=30)
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


# JWT admin authentication and authorization behavior.
class TestAdminAuth:
    def test_protected_admin_endpoint_rejects_missing_token(self, client):
        response = client.get(f"{API}/admin/me", timeout=30)
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_admin_login_and_identity(self, client, credentials, auth_headers):
        response = client.get(f"{API}/admin/me", headers=auth_headers, timeout=30)
        assert response.status_code == 200
        assert response.json() == {"email": credentials["email"], "role": "admin"}


# Published insights taxonomy and seeded article validation.
class TestInsightsTaxonomy:
    def test_exactly_six_published_articles_and_no_blog(self, client):
        response = client.get(f"{API}/insights", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 6
        assert {item["type"] for item in data} == {"article"}
        assert all(item["status"] == "published" for item in data)
        assert all(isinstance(item["id"], str) and item["id"] for item in data)
        assert all("_id" not in item for item in data)

    def test_article_filter_returns_same_six(self, client):
        response = client.get(f"{API}/insights", params={"type": "article"}, timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 6
        assert all(item["type"] == "article" for item in data)

    def test_legacy_blog_filter_is_empty(self, client):
        response = client.get(f"{API}/insights", params={"type": "blog"}, timeout=30)
        assert response.status_code == 200
        assert response.json() == []

    def test_seed_article_detail_and_unknown_404(self, client):
        response = client.get(f"{API}/insights/cfo-guide-s4hana-migration", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "cfo-guide-s4hana-migration"
        assert data["type"] == "article"
        assert len(data["sections"]) > 0
        missing = client.get(f"{API}/insights/TEST-does-not-exist", timeout=30)
        assert missing.status_code == 404
        assert missing.json()["detail"] == "Article not found"

    def test_backend_rejects_removed_blog_type(self, client, auth_headers):
        slug = f"test-rejected-blog-{uuid.uuid4().hex[:10]}"
        payload = {
            "slug": slug,
            "title": "TEST Removed taxonomy value",
            "excerpt": "This legacy content type must be rejected.",
            "category": "QA",
            "type": "blog",
            "date": "July 2026",
            "status": "published",
            "sections": [{"p": "TEST body"}],
        }
        response = client.post(f"{API}/insights", json=payload, headers=auth_headers, timeout=30)
        if response.status_code in (200, 201):
            client.delete(f"{API}/insights/{slug}", headers=auth_headers, timeout=30)
        assert response.status_code == 422, f"Removed type 'blog' was accepted: {response.status_code} {response.text}"


# Authenticated resource Create→GET→Update→GET→Delete→404 lifecycle.
class TestResourceCRUD:
    def test_resource_crud_and_persistence(self, client, auth_headers):
        slug = f"test-resource-{uuid.uuid4().hex[:10]}"
        payload = {
            "slug": slug,
            "title": "TEST QA Resource",
            "excerpt": "TEST short resource description.",
            "category": "QA",
            "type": "resource",
            "date": "July 2026",
            "read_minutes": 3,
            "image": "",
            "pdf_url": "/resources/checklist-erp-programme-readiness.pdf",
            "status": "published",
            "seo_title": "TEST QA Resource SEO",
            "meta_description": "TEST resource metadata.",
            "sections": [{"h": None, "p": "TEST resource body."}],
        }
        try:
            created_response = client.post(f"{API}/insights", json=payload, headers=auth_headers, timeout=30)
            assert created_response.status_code == 200, created_response.text
            created = created_response.json()
            assert created["slug"] == slug
            assert created["type"] == "resource"
            assert created["pdf_url"] == payload["pdf_url"]
            assert created["status"] == "published"

            detail_response = client.get(f"{API}/insights/{slug}", timeout=30)
            assert detail_response.status_code == 200
            assert detail_response.json()["title"] == payload["title"]

            filtered_response = client.get(f"{API}/insights", params={"type": "resource"}, timeout=30)
            assert filtered_response.status_code == 200
            assert any(item["slug"] == slug and item["pdf_url"] == payload["pdf_url"] for item in filtered_response.json())

            update_response = client.put(
                f"{API}/insights/{slug}",
                json={"title": "TEST QA Resource Updated", "seo_title": "TEST Updated SEO"},
                headers=auth_headers,
                timeout=30,
            )
            assert update_response.status_code == 200
            assert update_response.json()["title"] == "TEST QA Resource Updated"
            persisted = client.get(f"{API}/insights/{slug}", timeout=30)
            assert persisted.status_code == 200
            assert persisted.json()["title"] == "TEST QA Resource Updated"
            assert persisted.json()["excerpt"] == payload["excerpt"]
        finally:
            deleted = client.delete(f"{API}/insights/{slug}", headers=auth_headers, timeout=30)
            assert deleted.status_code in (200, 404)
        removed = client.get(f"{API}/insights/{slug}", timeout=30)
        assert removed.status_code == 404


# PDF upload, object serving, and media validation.
class TestPdfUpload:
    def test_pdf_upload_and_download(self, client, auth_headers):
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        pdf = io.BytesIO()
        writer.write(pdf)
        response = client.post(
            f"{API}/admin/upload",
            headers=auth_headers,
            files={"file": ("TEST-qa-resource.pdf", pdf.getvalue(), "application/pdf")},
            timeout=120,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["url"].startswith("/api/files/infocure/uploads/")
        assert data["url"].endswith(".pdf")
        download = client.get(f"{BASE_URL}{data['url']}", timeout=120)
        assert download.status_code == 200
        assert download.headers["content-type"].startswith("application/pdf")
        assert download.content.startswith(b"%PDF")

    def test_upload_rejects_unsupported_type(self, client, auth_headers):
        response = client.post(
            f"{API}/admin/upload",
            headers=auth_headers,
            files={"file": ("TEST-qa.txt", b"not allowed", "text/plain")},
            timeout=30,
        )
        assert response.status_code == 400
        assert "Only JPEG" in response.json()["detail"]


# Contact submission validation and persistence verification.
class TestContact:
    def test_contact_submission_persists(self, client):
        marker = uuid.uuid4().hex[:10]
        payload = {
            "name": f"TEST QA Contact {marker}",
            "email": f"test.qa.{marker}@example.com",
            "phone": "+91 98765 43210",
            "company": "TEST Infocure QA",
            "interest": "Digital Transformation",
            "message": "TEST contact persistence verification.",
        }
        response = client.post(f"{API}/contact", json=payload, timeout=30)
        assert response.status_code == 200, response.text
        created = response.json()
        assert created["name"] == payload["name"]
        assert created["email"] == payload["email"]
        assert isinstance(created["id"], str) and created["id"]

        listing = client.get(f"{API}/contact", timeout=30)
        assert listing.status_code == 200
        stored = next((item for item in listing.json() if item["id"] == created["id"]), None)
        assert stored is not None
        assert stored["message"] == payload["message"]
        assert stored["company"] == payload["company"]

    @pytest.mark.parametrize(
        "payload",
        [
            {"name": "TEST", "email": "not-an-email", "message": "valid message"},
            {"name": " ", "email": "test@example.com", "message": "valid message"},
            {"name": "TEST", "email": "test@example.com", "message": " "},
            {"name": "TEST", "email": "test@example.com", "phone": "abc", "message": "valid message"},
        ],
    )
    def test_contact_rejects_invalid_input(self, client, payload):
        response = client.post(f"{API}/contact", json=payload, timeout=30)
        assert response.status_code == 422
        assert response.json()["detail"]
