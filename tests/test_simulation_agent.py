#!/usr/bin/env python3
"""
Test Suite for Simulation Agent

This test file validates the business simulation functionality, query parsing,
and mathematical calculations of the Simulation Agent.
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
import sys
sys.path.append('..')

from agents.simulation_agent import SimulationAgent, simulate


class TestSimulationAgent(unittest.TestCase):
    """Test cases for Simulation Agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = SimulationAgent()
        
    def test_agent_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(self.agent.openai_client)
        self.assertIsNotNone(self.agent.simulation_prompt)
        self.assertTrue(len(self.agent.simulation_prompt) > 0)
        
        # Check sample data
        self.assertIn("rice", self.agent.sample_data)
        self.assertIn("sugar", self.agent.sample_data)
        self.assertIn("wheat", self.agent.sample_data)
        
        # Verify data structure
        rice_data = self.agent.sample_data["rice"]
        self.assertIn("current_price", rice_data)
        self.assertIn("current_cost", rice_data)
        self.assertIn("weekly_sales", rice_data)
        self.assertIn("profit_margin", rice_data)
    
    def test_prompt_loading(self):
        """Test that prompts are loaded correctly."""
        prompt = self.agent._load_prompt("prompts/simulation_prompt.txt")
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)
        self.assertIn("JSON", prompt)
        self.assertIn("simulation", prompt)
    
    def test_sample_data_structure(self):
        """Test that sample data has correct structure."""
        for product, data in self.agent.sample_data.items():
            self.assertIsInstance(product, str)
            self.assertIsInstance(data, dict)
            
            required_fields = ["current_price", "current_cost", "weekly_sales", "profit_margin", "unit"]
            for field in required_fields:
                self.assertIn(field, data, f"Missing field {field} in {product}")
            
            # Verify data types
            self.assertIsInstance(data["current_price"], (int, float))
            self.assertIsInstance(data["current_cost"], (int, float))
            self.assertIsInstance(data["weekly_sales"], int)
            self.assertIsInstance(data["profit_margin"], float)
            self.assertIsInstance(data["unit"], str)
            
            # Verify logical constraints
            self.assertGreater(data["current_price"], 0)
            self.assertGreater(data["current_cost"], 0)
            self.assertGreater(data["weekly_sales"], 0)
            self.assertGreater(data["profit_margin"], 0)
            self.assertLess(data["profit_margin"], 1)
    
    def test_json_parsing(self):
        """Test JSON response parsing."""
        # Test valid JSON
        valid_json = '{"scenario": "increase_price", "item": "rice", "change": "+5"}'
        result = self.agent._parse_json_response(valid_json)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["scenario"], "increase_price")
        
        # Test JSON with markdown
        markdown_json = '```json\n{"scenario": "decrease_price", "item": "sugar", "change": "-10"}\n```'
        result = self.agent._parse_json_response(markdown_json)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["scenario"], "decrease_price")
        
        # Test invalid JSON
        invalid_json = '{"scenario": "increase_price", "item": "rice", "change": "+5"'  # Missing }
        result = self.agent._parse_json_response(invalid_json)
        self.assertIsNone(result)
    
    def test_arbitration_logic(self):
        """Test the arbitration logic for query parsing results."""
        # Test identical results
        gpt_output = {"scenario": "increase_price", "item": "rice", "change": "+5"}
        gemini_output = {"scenario": "increase_price", "item": "rice", "change": "+5"}
        
        result = self.agent.arbitrate_parsing(gpt_output, gemini_output)
        self.assertEqual(result["parsing_source"], "gpt+gemini_agree")
        
        # Test GPT only
        result = self.agent.arbitrate_parsing(gpt_output, None)
        self.assertEqual(result["parsing_source"], "gpt_only")
        
        # Test Gemini only
        result = self.agent.arbitrate_parsing(None, gemini_output)
        self.assertEqual(result["parsing_source"], "gemini_only")
        
        # Test both failed
        result = self.agent.arbitrate_parsing(None, None)
        self.assertEqual(result["parsing_source"], "fallback")
        
        # Test preference for more complete output
        gpt_output = {"scenario": "increase_price", "item": "rice"}
        gemini_output = {"scenario": "increase_price", "item": "rice", "change": "+5", "units": "%"}
        
        result = self.agent.arbitrate_parsing(gpt_output, gemini_output)
        self.assertEqual(result["parsing_source"], "gemini_preferred")
    
    def test_fallback_parsing(self):
        """Test fallback parsing when LLMs fail."""
        # Test price increase detection
        result = self.agent._fallback_parsing("increase rice price by 5%")
        self.assertEqual(result["scenario"], "increase_price")
        
        # Test price decrease detection
        result = self.agent._fallback_parsing("decrease sugar price by 10%")
        self.assertEqual(result["scenario"], "decrease_price")
        
        # Test bulk order detection
        result = self.agent._fallback_parsing("bulk buy together")
        self.assertEqual(result["scenario"], "bulk_order")
        
        # Test unknown scenario
        result = self.agent._fallback_parsing("hello world")
        self.assertEqual(result["scenario"], "unknown")
    
    def test_price_increase_simulation(self):
        """Test price increase simulation calculations."""
        # Test with 5% increase
        params = {"scenario": "increase_price", "item": "rice", "change": "+5"}
        product_data = self.agent.sample_data["rice"]
        
        result = self.agent._simulate_price_increase(params, product_data)
        
        # Verify result structure
        self.assertEqual(result["scenario"], "increase_price")
        self.assertEqual(result["item"], "rice")
        self.assertEqual(result["change"], "+5%")
        self.assertIn("current_price", result)
        self.assertIn("new_price", result)
        self.assertIn("profit_change", result)
        self.assertIn("sales_impact", result)
        
        # Verify calculations
        current_price = product_data["current_price"]
        expected_new_price = current_price * 1.05
        self.assertAlmostEqual(result["new_price"], expected_new_price, places=2)
        
        # Verify sales impact (should decrease with price increase)
        sales_impact = float(result["sales_impact"].replace("%", "")) / 100
        self.assertLess(sales_impact, 1.0)  # Sales should decrease
    
    def test_price_decrease_simulation(self):
        """Test price decrease simulation calculations."""
        # Test with 10% decrease
        params = {"scenario": "decrease_price", "item": "sugar", "change": "-10"}
        product_data = self.agent.sample_data["sugar"]
        
        result = self.agent._simulate_price_decrease(params, product_data)
        
        # Verify result structure
        self.assertEqual(result["scenario"], "decrease_price")
        self.assertEqual(result["item"], "sugar")
        self.assertEqual(result["change"], "-10%")
        self.assertIn("current_price", result)
        self.assertIn("new_price", result)
        self.assertIn("profit_change", result)
        self.assertIn("sales_impact", result)
        
        # Verify calculations
        current_price = product_data["current_price"]
        expected_new_price = current_price * 0.90
        self.assertAlmostEqual(result["new_price"], expected_new_price, places=2)
        
        # Verify sales impact (should increase with price decrease)
        sales_impact = float(result["sales_impact"].replace("%", "")) / 100
        self.assertGreater(sales_impact, 1.0)  # Sales should increase
    
    def test_bulk_order_simulation(self):
        """Test bulk order simulation calculations."""
        # Test with 10 shops
        params = {"scenario": "bulk_order", "item": "wheat", "change": "+10"}
        product_data = self.agent.sample_data["wheat"]
        
        result = self.agent._simulate_bulk_order(params, product_data)
        
        # Verify result structure
        self.assertEqual(result["scenario"], "bulk_order")
        self.assertEqual(result["item"], "wheat")
        self.assertIn("num_shops", result)
        self.assertIn("discount", result)
        self.assertIn("current_price", result)
        self.assertIn("bulk_price", result)
        self.assertIn("savings_per_unit", result)
        
        # Verify calculations
        self.assertEqual(result["num_shops"], 10)
        self.assertEqual(result["discount"], "10%")  # 10 shops = 10% discount
        
        current_price = product_data["current_price"]
        expected_bulk_price = current_price * 0.90
        self.assertAlmostEqual(result["bulk_price"], expected_bulk_price, places=2)
        
        # Verify savings calculation
        expected_savings = current_price - expected_bulk_price
        self.assertAlmostEqual(result["savings_per_unit"], expected_savings, places=2)
    
    def test_unknown_scenario(self):
        """Test handling of unknown simulation scenarios."""
        params = {"scenario": "unknown", "item": "unknown"}
        product_data = self.agent.sample_data["rice"]
        
        result = self.agent._simulate_unknown_scenario(params, product_data)
        
        self.assertEqual(result["scenario"], "unknown")
        self.assertIn("error", result)
        self.assertIn("supported_scenarios", result)
        self.assertIn("recommendation", result)
    
    @patch('agents.simulation_agent.SimulationAgent.parse_query_with_gpt')
    @patch('agents.simulation_agent.SimulationAgent.parse_query_with_gemini')
    def test_mock_simulation(self, mock_gemini, mock_gpt):
        """Test simulation with mocked LLM responses."""
        # Mock GPT response
        mock_gpt.return_value = {
            "scenario": "increase_price",
            "item": "rice",
            "change": "+5",
            "units": "%"
        }
        
        # Mock Gemini response
        mock_gemini.return_value = {
            "scenario": "increase_price",
            "item": "rice",
            "change": "+5",
            "units": "%"
        }
        
        # Run simulation
        result = self.agent.simulate("What if I increase rice price by 5%?")
        
        # Verify the result structure
        self.assertIn("query", result)
        self.assertIn("parsed_parameters", result)
        self.assertIn("simulation_results", result)
        self.assertIn("timestamp", result)
        
        # Verify simulation results
        sim_results = result["simulation_results"]
        self.assertEqual(sim_results["scenario"], "increase_price")
        self.assertEqual(sim_results["item"], "rice")
        
        # Verify mocks were called
        mock_gpt.assert_called_once()
        mock_gemini.assert_called_once()
    
    def test_results_storage(self):
        """Test that simulation results are stored correctly."""
        # Create mock results
        gpt_parsed = {"scenario": "increase_price", "item": "rice"}
        gemini_parsed = {"scenario": "increase_price", "item": "rice"}
        final_result = {
            "query": "test query",
            "parsed_parameters": {"scenario": "increase_price"},
            "simulation_results": {"scenario": "increase_price"}
        }
        
        # Store results
        self.agent._store_results("test query", gpt_parsed, gemini_parsed, final_result)
        
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
    
    def test_simulation_stats(self):
        """Test simulation statistics functionality."""
        # Test with no results
        stats = self.agent.get_simulation_stats()
        self.assertEqual(stats["total_simulations"], 0)
        self.assertEqual(stats["success_rate"], 0)
        
        # Test with mock results file
        mock_results = [
            {
                "query": "test1",
                "final_result": {"simulation_results": {"scenario": "increase_price"}}
            },
            {
                "query": "test2",
                "final_result": {"simulation_results": {"error": "failed"}}
            }
        ]
        
        # Create temporary results file
        with open(self.agent.results_file, 'w') as f:
            json.dump(mock_results, f)
        
        try:
            stats = self.agent.get_simulation_stats()
            self.assertEqual(stats["total_simulations"], 2)
            self.assertEqual(stats["successful_simulations"], 1)
            self.assertEqual(stats["success_rate"], 50.0)
        finally:
            # Clean up
            if self.agent.results_file.exists():
                os.remove(self.agent.results_file)


class TestSimulationIntegration(unittest.TestCase):
    """Integration tests for Simulation Agent."""
    
    def test_convenience_function(self):
        """Test the convenience function."""
        # This would normally test with real LLM calls
        # For now, just test that the function exists
        self.assertTrue(callable(simulate))
    
    def test_agent_imports(self):
        """Test that all required modules can be imported."""
        try:
            from agents.simulation_agent import SimulationAgent
            self.assertTrue(True)  # Import successful
        except ImportError as e:
            self.fail(f"Failed to import SimulationAgent: {e}")
    
    def test_mathematical_accuracy(self):
        """Test mathematical accuracy of simulations."""
        agent = SimulationAgent()
        
        # Test price increase math
        params = {"scenario": "increase_price", "item": "rice", "change": "+10"}
        product_data = agent.sample_data["rice"]
        
        result = agent._simulate_price_increase(params, product_data)
        
        # Verify 10% increase
        current_price = product_data["current_price"]
        expected_new_price = current_price * 1.10
        self.assertAlmostEqual(result["new_price"], expected_new_price, places=2)
        
        # Verify profit calculations
        current_cost = product_data["current_cost"]
        old_profit_per_unit = current_price - current_cost
        new_profit_per_unit = result["new_price"] - current_cost
        
        self.assertAlmostEqual(new_profit_per_unit, old_profit_per_unit * 1.10, places=2)


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
    print("🧪 Running Simulation Agent Tests")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    print(f"\n📊 Test Summary:")
    print(f"   - Test file: test_simulation_agent.py")
    print(f"   - Test classes: 2")
    print(f"   - Test methods: 12+")
    print(f"   - Coverage: Parsing, Arbitration, Math, Storage, Stats")
