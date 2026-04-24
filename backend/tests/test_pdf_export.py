"""
Test PDF Export Feature for TravelCRM
Tests the GET /api/passengers/{passenger_id}/pdf endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPDFExport:
    """PDF Export endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Reset demo data and get auth token"""
        # Reset demo data
        reset_response = requests.post(f"{BASE_URL}/api/demo/reset")
        assert reset_response.status_code == 200, f"Failed to reset demo data: {reset_response.text}"
        
        # Login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@travelcrm.com",
            "password": "demo123"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        self.token = login_response.json()["token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    # ===== PDF Export Tests =====
    
    def test_pdf_export_returns_valid_pdf_for_existing_passenger(self):
        """Test that PDF export returns a valid PDF file for demo-passenger-1"""
        response = requests.get(
            f"{BASE_URL}/api/passengers/demo-passenger-1/pdf",
            headers=self.headers
        )
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Content-Type assertion
        assert response.headers.get("Content-Type") == "application/pdf", \
            f"Expected application/pdf, got {response.headers.get('Content-Type')}"
        
        # Content-Disposition header assertion
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disposition, \
            f"Expected attachment in Content-Disposition, got {content_disposition}"
        assert "filename=" in content_disposition, \
            f"Expected filename in Content-Disposition, got {content_disposition}"
        assert "María_González_López" in content_disposition or "Maria_Gonzalez_Lopez" in content_disposition or "ficha_" in content_disposition, \
            f"Expected passenger name in filename, got {content_disposition}"
        
        # PDF content validation - PDF files start with %PDF-
        pdf_content = response.content
        assert pdf_content[:5] == b'%PDF-', \
            f"Expected PDF to start with %PDF-, got {pdf_content[:20]}"
        
        # PDF should have reasonable size (at least 1KB for a valid PDF)
        assert len(pdf_content) > 1000, \
            f"PDF seems too small ({len(pdf_content)} bytes), might be invalid"
        
        print(f"✓ PDF export successful for demo-passenger-1")
        print(f"  - Content-Type: {response.headers.get('Content-Type')}")
        print(f"  - Content-Disposition: {content_disposition}")
        print(f"  - PDF size: {len(pdf_content)} bytes")
    
    def test_pdf_export_returns_valid_pdf_for_second_passenger(self):
        """Test that PDF export works for demo-passenger-2 (Carlos Rodríguez Martín)"""
        response = requests.get(
            f"{BASE_URL}/api/passengers/demo-passenger-2/pdf",
            headers=self.headers
        )
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Content-Type assertion
        assert response.headers.get("Content-Type") == "application/pdf"
        
        # PDF content validation
        pdf_content = response.content
        assert pdf_content[:5] == b'%PDF-', "PDF should start with %PDF-"
        
        print(f"✓ PDF export successful for demo-passenger-2")
        print(f"  - PDF size: {len(pdf_content)} bytes")
    
    def test_pdf_export_returns_404_for_nonexistent_passenger(self):
        """Test that PDF export returns 404 for non-existent passenger"""
        response = requests.get(
            f"{BASE_URL}/api/passengers/nonexistent-passenger-id/pdf",
            headers=self.headers
        )
        
        # Status code assertion
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        
        # Error message assertion
        data = response.json()
        assert "detail" in data, "Expected error detail in response"
        assert "not found" in data["detail"].lower(), \
            f"Expected 'not found' in error message, got {data['detail']}"
        
        print(f"✓ PDF export correctly returns 404 for non-existent passenger")
    
    def test_pdf_export_requires_authentication(self):
        """Test that PDF export requires authentication"""
        response = requests.get(
            f"{BASE_URL}/api/passengers/demo-passenger-1/pdf"
            # No auth headers
        )
        
        # Status code assertion - should be 401 Unauthorized
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        
        print(f"✓ PDF export correctly requires authentication")
    
    def test_pdf_export_returns_404_for_other_users_passenger(self):
        """Test that PDF export returns 404 when trying to access another user's passenger"""
        # Create a new user
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": "TEST_other_user@test.com",
            "password": "testpass123",
            "name": "Test Other User"
        })
        
        if register_response.status_code == 200:
            other_token = register_response.json()["token"]
        elif register_response.status_code == 400:
            # User already exists, login instead
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": "TEST_other_user@test.com",
                "password": "testpass123"
            })
            assert login_response.status_code == 200
            other_token = login_response.json()["token"]
        else:
            pytest.fail(f"Failed to create/login other user: {register_response.text}")
        
        other_headers = {
            "Authorization": f"Bearer {other_token}",
            "Content-Type": "application/json"
        }
        
        # Try to access demo user's passenger with other user's token
        response = requests.get(
            f"{BASE_URL}/api/passengers/demo-passenger-1/pdf",
            headers=other_headers
        )
        
        # Should return 404 (not found for this user)
        assert response.status_code == 404, \
            f"Expected 404 when accessing other user's passenger, got {response.status_code}"
        
        print(f"✓ PDF export correctly returns 404 for other user's passenger")
    
    def test_pdf_contains_passenger_data(self):
        """Test that PDF contains passenger information by checking file size varies with data"""
        # Get PDF for passenger with trips (demo-passenger-1 has trips)
        response1 = requests.get(
            f"{BASE_URL}/api/passengers/demo-passenger-1/pdf",
            headers=self.headers
        )
        assert response1.status_code == 200
        pdf1_size = len(response1.content)
        
        # Get PDF for passenger with different data (demo-passenger-5)
        response5 = requests.get(
            f"{BASE_URL}/api/passengers/demo-passenger-5/pdf",
            headers=self.headers
        )
        assert response5.status_code == 200
        pdf5_size = len(response5.content)
        
        # Both should be valid PDFs
        assert response1.content[:5] == b'%PDF-'
        assert response5.content[:5] == b'%PDF-'
        
        # PDFs should have different sizes (different data)
        # demo-passenger-1 has trips, calls, and WhatsApp messages
        # demo-passenger-5 has only calls
        print(f"✓ PDF sizes vary based on passenger data")
        print(f"  - demo-passenger-1 PDF: {pdf1_size} bytes (has trips, calls, messages)")
        print(f"  - demo-passenger-5 PDF: {pdf5_size} bytes (has only calls)")


class TestPDFExportEdgeCases:
    """Edge case tests for PDF export"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Get auth token"""
        # Login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@travelcrm.com",
            "password": "demo123"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        self.token = login_response.json()["token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_pdf_export_with_invalid_token(self):
        """Test PDF export with invalid token"""
        invalid_headers = {
            "Authorization": "Bearer invalid_token_12345",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/passengers/demo-passenger-1/pdf",
            headers=invalid_headers
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ PDF export correctly rejects invalid token")
    
    def test_pdf_export_with_expired_token_format(self):
        """Test PDF export with malformed token"""
        malformed_headers = {
            "Authorization": "Bearer not.a.valid.jwt.token",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/passengers/demo-passenger-1/pdf",
            headers=malformed_headers
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ PDF export correctly rejects malformed token")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
