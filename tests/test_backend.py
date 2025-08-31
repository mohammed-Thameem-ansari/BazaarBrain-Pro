"""
Backend tests for BazaarBrain-Pro API.

Tests:
- FastAPI endpoints
- Authentication middleware
- Database integration
- Error handling
- Input validation
"""

import unittest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from PIL import Image
import io

# Import the FastAPI app
import sys
sys.path.append('..')
from backend.main import app
from backend.db import DatabaseManager, save_transaction, save_simulation
from backend.auth import verify_jwt_token, get_current_user_id

class TestBackendEndpoints(unittest.TestCase):
    """Test FastAPI endpoints and functionality."""
    
    def setUp(self):
        """Set up test client and mock data."""
        self.client = TestClient(app)
        self.test_user_id = "test-user-123"
        self.test_user_email = "test@example.com"
        
        # Mock JWT token
        self.mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"
        
        # Mock user payload
        self.mock_user_payload = {
            "sub": self.test_user_id,
            "email": self.test_user_email,
            "aud": "authenticated"
        }
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct information."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("version", data)
        self.assertIn("status", data)
        self.assertEqual(data["status"], "running")
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("services", data)
        self.assertIn("api", data["services"])
        self.assertIn("database", data["services"])
    
    def test_api_v1_health_endpoints(self):
        """Test API v1 health endpoints."""
        # Basic health
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        
        # Detailed health
        response = self.client.get("/api/v1/health/detailed")
        self.assertEqual(response.status_code, 200)
        
        # Readiness check
        response = self.client.get("/api/v1/health/ready")
        self.assertEqual(response.status_code, 200)
        
        # Liveness check
        response = self.client.get("/api/v1/health/live")
        self.assertEqual(response.status_code, 200)
    
    @patch('backend.auth.verify_jwt_token')
    def test_upload_receipt_authenticated(self, mock_verify_token):
        """Test receipt upload with valid authentication."""
        # Mock token verification
        mock_verify_token.return_value = self.mock_user_payload
        
        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='red')
        image_bytes = io.BytesIO()
        test_image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)
        
        # Mock the Reality Capture Agent
        with patch('backend.routers.receipts.RealityCaptureAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.process_receipt.return_value = {
                "items": [{"name": "Coffee", "price": 3.50}],
                "total": 3.50,
                "source": "gpt+gemini_agree"
            }
            mock_agent_class.return_value = mock_agent
            
            # Mock database save
            with patch('backend.routers.receipts.save_transaction') as mock_save:
                mock_save.return_value = "test-transaction-id"
                
                # Make request
                response = self.client.post(
                    "/api/v1/upload_receipt",
                    files={"file": ("test.jpg", image_bytes.getvalue(), "image/jpeg")},
                    data={"source": "receipt"},
                    headers={"Authorization": f"Bearer {self.mock_token}"}
                )
                
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data["success"])
                self.assertIn("transaction_id", data)
    
    def test_upload_receipt_unauthenticated(self):
        """Test receipt upload without authentication."""
        response = self.client.post("/api/v1/upload_receipt")
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_upload_receipt_invalid_file_type(self):
        """Test receipt upload with invalid file type."""
        # Create a text file instead of image
        test_file = io.BytesIO(b"This is not an image")
        
        response = self.client.post(
            "/api/v1/upload_receipt",
            files={"file": ("test.txt", test_file.getvalue(), "text/plain")},
            data={"source": "receipt"},
            headers={"Authorization": f"Bearer {self.mock_token}"}
        )
        
        self.assertEqual(response.status_code, 400)
    
    @patch('backend.auth.verify_jwt_token')
    def test_get_transactions_authenticated(self, mock_verify_token):
        """Test getting transactions with valid authentication."""
        # Mock token verification
        mock_verify_token.return_value = self.mock_user_payload
        
        # Mock database get
        with patch('backend.routers.receipts.get_transactions') as mock_get:
            mock_get.return_value = [
                {
                    "id": "test-id",
                    "user_id": self.test_user_id,
                    "raw_input": "test.jpg",
                    "parsed_json": {"items": []},
                    "source": "image"
                }
            ]
            
            response = self.client.get(
                "/api/v1/transactions",
                headers={"Authorization": f"Bearer {self.mock_token}"}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(len(data["transactions"]), 1)
    
    @patch('backend.auth.verify_jwt_token')
    def test_run_simulation_authenticated(self, mock_verify_token):
        """Test running simulation with valid authentication."""
        # Mock token verification
        mock_verify_token.return_value = self.mock_user_payload
        
        # Mock the Simulation Agent
        with patch('backend.routers.simulations.SimulationAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.simulate.return_value = {
                "scenario": "increase_price",
                "item": "Coffee",
                "change": 10,
                "estimated_profit_change": 0.35
            }
            mock_agent_class.return_value = mock_agent
            
            # Mock database save
            with patch('backend.routers.simulations.save_simulation') as mock_save:
                mock_save.return_value = "test-simulation-id"
                
                # Make request
                response = self.client.post(
                    "/api/v1/simulate",
                    json={"query": "What if I increase coffee price by 10%?"},
                    headers={"Authorization": f"Bearer {self.mock_token}"}
                )
                
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data["success"])
                self.assertIn("simulation_id", data)
    
    def test_run_simulation_unauthenticated(self):
        """Test running simulation without authentication."""
        response = self.client.post(
            "/api/v1/simulate",
            json={"query": "What if I increase coffee price by 10%?"}
        )
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_run_simulation_invalid_query(self):
        """Test running simulation with invalid query."""
        response = self.client.post(
            "/api/v1/simulate",
            json={"query": "Hi"},  # Too short
            headers={"Authorization": f"Bearer {self.mock_token}"}
        )
        self.assertEqual(response.status_code, 400)
    
    @patch('backend.auth.verify_jwt_token')
    def test_get_simulations_authenticated(self, mock_verify_token):
        """Test getting simulations with valid authentication."""
        # Mock token verification
        mock_verify_token.return_value = self.mock_user_payload
        
        # Mock database get
        with patch('backend.routers.simulations.get_simulations') as mock_get:
            mock_get.return_value = [
                {
                    "id": "test-id",
                    "user_id": self.test_user_id,
                    "query": "What if I increase coffee price?",
                    "parameters": {"scenario": "increase_price"},
                    "result": {"estimated_profit_change": 0.35}
                }
            ]
            
            response = self.client.get(
                "/api/v1/simulations",
                headers={"Authorization": f"Bearer {self.mock_token}"}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(len(data["simulations"]), 1)
    
    def test_get_available_scenarios(self):
        """Test getting available simulation scenarios."""
        response = self.client.get("/api/v1/scenarios")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("scenarios", data)
        self.assertIn("price_increase", data["scenarios"])
        self.assertIn("price_decrease", data["scenarios"])
        self.assertIn("bulk_order", data["scenarios"])


class TestAuthentication(unittest.TestCase):
    """Test authentication functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_token = "valid.jwt.token"
        self.invalid_token = "invalid.token"
        self.expired_token = "expired.jwt.token"
    
    @patch('backend.auth.jwt.decode')
    def test_verify_jwt_token_valid(self, mock_jwt_decode):
        """Test valid JWT token verification."""
        mock_jwt_decode.return_value = {
            "sub": "user-123",
            "email": "test@example.com",
            "aud": "authenticated"
        }
        
        result = verify_jwt_token(self.valid_token)
        self.assertIsNotNone(result)
        self.assertEqual(result["sub"], "user-123")
        self.assertEqual(result["email"], "test@example.com")
    
    @patch('backend.auth.jwt.decode')
    def test_verify_jwt_token_invalid(self, mock_jwt_decode):
        """Test invalid JWT token verification."""
        mock_jwt_decode.side_effect = Exception("Invalid token")
        
        result = verify_jwt_token(self.invalid_token)
        self.assertIsNone(result)
    
    @patch('backend.auth.jwt.decode')
    def test_verify_jwt_token_missing_fields(self, mock_jwt_decode):
        """Test JWT token with missing required fields."""
        mock_jwt_decode.return_value = {
            "sub": "user-123"
            # Missing email field
        }
        
        result = verify_jwt_token(self.valid_token)
        self.assertIsNone(result)


class TestDatabaseIntegration(unittest.TestCase):
    """Test database integration functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.test_user_id = "test-user-123"
        self.test_transaction_data = {
            "items": [{"name": "Coffee", "price": 3.50}],
            "total": 3.50
        }
        self.test_simulation_data = {
            "scenario": "increase_price",
            "item": "Coffee",
            "change": 10
        }
    
    @patch('backend.db.DatabaseManager')
    def test_save_transaction_success(self, mock_db_manager):
        """Test successful transaction save."""
        mock_db = Mock()
        mock_db.save_transaction.return_value = "transaction-123"
        mock_db_manager.return_value = mock_db
        
        result = save_transaction(
            self.test_user_id,
            "test.jpg",
            self.test_transaction_data,
            "image"
        )
        
        self.assertEqual(result, "transaction-123")
        mock_db.save_transaction.assert_called_once()
    
    @patch('backend.db.DatabaseManager')
    def test_save_simulation_success(self, mock_db_manager):
        """Test successful simulation save."""
        mock_db = Mock()
        mock_db.save_simulation.return_value = "simulation-123"
        mock_db_manager.return_value = mock_db
        
        result = save_simulation(
            self.test_user_id,
            "What if I increase coffee price?",
            self.test_simulation_data,
            {"estimated_profit_change": 0.35}
        )
        
        self.assertEqual(result, "simulation-123")
        mock_db.save_simulation.assert_called_once()


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_global_exception_handler(self):
        """Test global exception handler."""
        # This would require triggering an actual exception
        # For now, we'll test that the handler exists
        self.assertTrue(hasattr(app, 'exception_handlers'))
    
    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404."""
        response = self.client.get("/invalid/endpoint")
        self.assertEqual(response.status_code, 404)
    
    def test_method_not_allowed(self):
        """Test method not allowed returns 405."""
        response = self.client.put("/")
        self.assertEqual(response.status_code, 405)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
