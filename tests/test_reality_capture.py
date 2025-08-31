#!/usr/bin/env python3
"""
Test Suite for Reality Capture Agent v2

This test file validates the OCR functionality, dual LLM processing,
and arbitration logic of the Reality Capture Agent.
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image, ImageDraw, ImageFont
import io

# Add parent directory to path for imports
import sys
sys.path.append('..')

from agents.reality_capture_agent import RealityCaptureAgent, process_receipt


class TestRealityCaptureAgent(unittest.TestCase):
    """Test cases for Reality Capture Agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = RealityCaptureAgent()
        self.test_image_path = self._create_test_image()
        
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
    
    def _create_test_image(self) -> str:
        """Create a test receipt image for testing."""
        # Create a simple test image
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add some text to simulate a receipt
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw receipt content
        draw.text((20, 20), "CITY MART", fill='black', font=font)
        draw.text((20, 50), "Receipt #12345", fill='black', font=font)
        draw.text((20, 80), "Date: 2025-01-27", fill='black', font=font)
        draw.text((20, 110), "Rice 2kg x 45.50 = 91.00", fill='black', font=font)
        draw.text((20, 140), "Sugar 1kg x 32.00 = 32.00", fill='black', font=font)
        draw.text((20, 170), "Oil 1L x 120.00 = 120.00", fill='black', font=font)
        draw.text((20, 200), "Tax: 24.30", fill='black', font=font)
        draw.text((20, 230), "Total: 267.30", fill='black', font=font)
        draw.text((20, 260), "Payment: Card", fill='black', font=font)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img.save(temp_file.name, 'JPEG')
        return temp_file.name
    
    def test_agent_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(self.agent.openai_client)
        self.assertIsNotNone(self.agent.ocr_prompt)
        self.assertTrue(len(self.agent.ocr_prompt) > 0)
    
    def test_prompt_loading(self):
        """Test that prompts are loaded correctly."""
        prompt = self.agent._load_prompt("prompts/ocr_prompt.txt")
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)
        self.assertIn("JSON", prompt)
    
    def test_image_preprocessing(self):
        """Test image preprocessing functionality."""
        # Test with valid image
        image_bytes = self.agent.preprocess_image(self.test_image_path)
        self.assertIsInstance(image_bytes, bytes)
        self.assertTrue(len(image_bytes) > 0)
        
        # Test with non-existent image
        with self.assertRaises(Exception):
            self.agent.preprocess_image("non_existent_image.jpg")
    
    def test_json_parsing(self):
        """Test JSON response parsing."""
        # Test valid JSON
        valid_json = '{"items": [{"name": "Rice", "qty": 2, "price": 45.50}]}'
        result = self.agent._parse_json_response(valid_json)
        self.assertIsInstance(result, dict)
        self.assertIn("items", result)
        
        # Test JSON with markdown
        markdown_json = '```json\n{"items": [{"name": "Sugar", "qty": 1, "price": 32.00}]}\n```'
        result = self.agent._parse_json_response(markdown_json)
        self.assertIsInstance(result, dict)
        self.assertIn("items", result)
        
        # Test invalid JSON
        invalid_json = '{"items": [{"name": "Rice", "qty": 2, "price": 45.50]'  # Missing }
        result = self.agent._parse_json_response(invalid_json)
        self.assertIsNone(result)
    
    def test_arbitration_logic(self):
        """Test the arbitration logic for conflicting results."""
        # Test identical results
        gpt_output = {"items": [{"name": "Rice", "qty": 2, "price": 45.50}], "total": 91.00}
        gemini_output = {"items": [{"name": "Rice", "qty": 2, "price": 45.50}], "total": 91.00}
        
        result = self.agent.arbitrate_ocr(gpt_output, gemini_output)
        self.assertEqual(result["source"], "gpt+gemini_agree")
        self.assertEqual(result["total"], 91.00)
        
        # Test GPT only
        result = self.agent.arbitrate_ocr(gpt_output, None)
        self.assertEqual(result["source"], "gpt_only")
        
        # Test Gemini only
        result = self.agent.arbitrate_ocr(None, gemini_output)
        self.assertEqual(result["source"], "gemini_only")
        
        # Test both failed
        result = self.agent.arbitrate_ocr(None, None)
        self.assertEqual(result["source"], "both_failed")
        self.assertIn("error", result)
        
        # Test preference for more items
        gpt_output = {"items": [{"name": "Rice", "qty": 2, "price": 45.50}], "total": 91.00}
        gemini_output = {
            "items": [
                {"name": "Rice", "qty": 2, "price": 45.50},
                {"name": "Sugar", "qty": 1, "price": 32.00}
            ],
            "total": 123.00
        }
        
        result = self.agent.arbitrate_ocr(gpt_output, gemini_output)
        self.assertEqual(result["source"], "gemini_preferred")
        self.assertEqual(len(result["items"]), 2)
        
        # Test merging different items
        gpt_output = {"items": [{"name": "Rice", "qty": 2, "price": 45.50}], "total": 91.00}
        gemini_output = {"items": [{"name": "Sugar", "qty": 1, "price": 32.00}], "total": 32.00}
        
        result = self.agent.arbitrate_ocr(gpt_output, gemini_output)
        self.assertEqual(result["source"], "merged")
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["total"], 91.00)  # Should take max total
    
    @patch('agents.reality_capture_agent.RealityCaptureAgent.process_with_gpt_vision')
    @patch('agents.reality_capture_agent.RealityCaptureAgent.process_with_gemini_vision')
    def test_mock_processing(self, mock_gemini, mock_gpt):
        """Test processing with mocked LLM responses."""
        # Mock GPT response
        mock_gpt.return_value = {
            "items": [{"name": "Rice", "qty": 2, "price": 45.50}],
            "total": 91.00,
            "date": "2025-01-27"
        }
        
        # Mock Gemini response
        mock_gemini.return_value = {
            "items": [{"name": "Rice", "qty": 2, "price": 45.50}],
            "date": "2025-01-27"
        }
        
        # Process the image
        result = self.agent.process_receipt(self.test_image_path)
        
        # Verify the result
        self.assertIn("items", result)
        self.assertIn("total", result)
        self.assertIn("source", result)
        self.assertIn("image_path", result)
        
        # Verify mocks were called
        mock_gpt.assert_called_once()
        mock_gemini.assert_called_once()
    
    def test_results_storage(self):
        """Test that results are stored correctly."""
        # Create mock results
        gpt_result = {"items": [{"name": "Rice", "qty": 2, "price": 45.50}]}
        gemini_result = {"items": [{"name": "Rice", "qty": 2, "price": 45.50}]}
        final_result = {"items": [{"name": "Rice", "qty": 2, "price": 45.50}], "source": "gpt+gemini_agree"}
        
        # Store results
        self.agent._store_results(self.test_image_path, gpt_result, gemini_result, final_result)
        
        # Verify file was created
        self.assertTrue(self.agent.results_file.exists())
        
        # Verify content
        with open(self.agent.results_file, 'r') as f:
            stored_results = json.load(f)
        
        self.assertIsInstance(stored_results, list)
        self.assertTrue(len(stored_results) > 0)
        
        # Clean up
        if self.agent.results_file.exists():
            os.remove(self.agent.results_file)
    
    def test_processing_stats(self):
        """Test processing statistics functionality."""
        # Test with no results
        stats = self.agent.get_processing_stats()
        self.assertEqual(stats["total_processed"], 0)
        self.assertEqual(stats["success_rate"], 0)
        
        # Test with mock results file
        mock_results = [
            {
                "image_path": "test1.jpg",
                "final_result": {"items": [{"name": "Rice", "qty": 2, "price": 45.50}]}
            },
            {
                "image_path": "test2.jpg",
                "final_result": {"items": []}  # Failed extraction
            }
        ]
        
        # Create temporary results file
        with open(self.agent.results_file, 'w') as f:
            json.dump(mock_results, f)
        
        try:
            stats = self.agent.get_processing_stats()
            self.assertEqual(stats["total_processed"], 2)
            self.assertEqual(stats["successful_extractions"], 1)
            self.assertEqual(stats["success_rate"], 50.0)
        finally:
            # Clean up
            if self.agent.results_file.exists():
                os.remove(self.agent.results_file)


class TestRealityCaptureIntegration(unittest.TestCase):
    """Integration tests for Reality Capture Agent."""
    
    def test_convenience_function(self):
        """Test the convenience function."""
        # This would normally test with a real image
        # For now, just test that the function exists
        self.assertTrue(callable(process_receipt))
    
    def test_agent_imports(self):
        """Test that all required modules can be imported."""
        try:
            from agents.reality_capture_agent import RealityCaptureAgent
            self.assertTrue(True)  # Import successful
        except ImportError as e:
            self.fail(f"Failed to import RealityCaptureAgent: {e}")


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 Running Reality Capture Agent Tests")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    print(f"\n📊 Test Summary:")
    print(f"   - Test file: test_reality_capture.py")
    print(f"   - Test classes: 2")
    print(f"   - Test methods: 8+")
    print(f"   - Coverage: OCR, Arbitration, Storage, Stats")
