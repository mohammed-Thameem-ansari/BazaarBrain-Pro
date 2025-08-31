#!/usr/bin/env python3
"""
Simulation Agent - Business Scenario Analysis

This agent handles "what-if" business scenarios for shopkeepers, including:
- Price increase/decrease simulations
- Bulk order scenarios
- Inventory change analysis
- Profit margin calculations

Features:
- Natural language query parsing using dual LLMs
- Mathematical simulation engine
- Structured JSON output
- Sample data integration
- Extensible simulation framework
"""

import json
import logging
import re
from typing import Dict, List, Optional, Union
from pathlib import Path

# AI imports
from openai import OpenAI
import google.generativeai as genai

# Local imports
import sys
sys.path.append('..')
from backend.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimulationAgent:
    """
    Business simulation agent for "what-if" scenarios.
    """
    
    def __init__(self):
        """Initialize the Simulation Agent with both LLM clients."""
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.gemini_model = None
        self._setup_gemini()
        
        # Load prompts
        self.simulation_prompt = self._load_prompt("prompts/simulation_prompt.txt")
        
        # Sample business data for simulations
        self.sample_data = self._load_sample_data()
        
        # Results storage
        self.results_file = Path("tests/simulation_results.json")
        self.results_file.parent.mkdir(exist_ok=True)
    
    def _setup_gemini(self):
        """Setup Gemini client."""
        try:
            genai.configure(api_key=config.GOOGLE_API_KEY)
            self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("✅ Gemini client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            self.gemini_model = None
    
    def _load_prompt(self, prompt_path: str) -> str:
        """Load prompt from file."""
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.warning(f"Prompt file not found: {prompt_path}")
            return "Parse this business query and return structured parameters in JSON format."
    
    def _load_sample_data(self) -> Dict:
        """
        Load sample business data for simulations.
        
        Returns:
            Dictionary with sample product data
        """
        return {
            "rice": {
                "current_price": 50.0,
                "current_cost": 35.0,
                "weekly_sales": 100,
                "profit_margin": 0.30,
                "unit": "kg"
            },
            "sugar": {
                "current_price": 40.0,
                "current_cost": 28.0,
                "weekly_sales": 80,
                "profit_margin": 0.30,
                "unit": "kg"
            },
            "wheat": {
                "current_price": 45.0,
                "current_cost": 32.0,
                "weekly_sales": 120,
                "profit_margin": 0.29,
                "unit": "kg"
            },
            "oil": {
                "current_price": 120.0,
                "current_cost": 85.0,
                "weekly_sales": 50,
                "profit_margin": 0.29,
                "unit": "liter"
            },
            "pulses": {
                "current_price": 80.0,
                "current_cost": 55.0,
                "weekly_sales": 60,
                "profit_margin": 0.31,
                "unit": "kg"
            }
        }
    
    def parse_query_with_gpt(self, query: str) -> Optional[Dict]:
        """
        Parse business query using OpenAI GPT.
        
        Args:
            query: Natural language business query
            
        Returns:
            Parsed parameters as dictionary or None if failed
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.simulation_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"GPT parsing response: {content[:100]}...")
            
            return self._parse_json_response(content)
            
        except Exception as e:
            logger.error(f"GPT query parsing failed: {e}")
            return None
    
    def parse_query_with_gemini(self, query: str) -> Optional[Dict]:
        """
        Parse business query using Google Gemini.
        
        Args:
            query: Natural language business query
            
        Returns:
            Parsed parameters as dictionary or None if failed
        """
        try:
            if not self.gemini_model:
                logger.warning("Gemini model not available")
                return None
            
            response = self.gemini_model.generate_content([
                self.simulation_prompt,
                query
            ])
            
            content = response.text.strip()
            logger.info(f"Gemini parsing response: {content[:100]}...")
            
            return self._parse_json_response(content)
            
        except Exception as e:
            logger.error(f"Gemini query parsing failed: {e}")
            return None
    
    def _parse_json_response(self, content: str) -> Optional[Dict]:
        """
        Parse JSON response from LLM.
        
        Args:
            content: Raw response from LLM
            
        Returns:
            Parsed JSON as dictionary or None if failed
        """
        try:
            # Clean the response
            content = content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Try to parse as JSON
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}")
            logger.debug(f"Raw content: {content}")
            return None
    
    def arbitrate_parsing(self, gpt_output: Optional[Dict], gemini_output: Optional[Dict]) -> Dict:
        """
        Arbitration logic for query parsing results.
        
        Args:
            gpt_output: Output from GPT parsing
            gemini_output: Output from Gemini parsing
            
        Returns:
            Final arbitrated parsing result
        """
        # 1. If both are identical
        if gpt_output == gemini_output and gpt_output is not None:
            return {**gpt_output, "parsing_source": "gpt+gemini_agree"}
        
        # 2. If one is missing or empty, prefer the other
        if not gpt_output and gemini_output:
            return {**gemini_output, "parsing_source": "gemini_only"}
        if not gemini_output and gpt_output:
            return {**gpt_output, "parsing_source": "gpt_only"}
        
        # 3. If both failed, use fallback parsing
        if not gpt_output and not gemini_output:
            return self._fallback_parsing("")
        
        # 4. Prefer the more complete output
        gpt_completeness = len(gpt_output) if gpt_output else 0
        gemini_completeness = len(gemini_output) if gemini_output else 0
        
        if gpt_completeness >= gemini_completeness:
            return {**gpt_output, "parsing_source": "gpt_preferred"}
        else:
            return {**gemini_output, "parsing_source": "gemini_preferred"}
    
    def _fallback_parsing(self, query: str) -> Dict:
        """
        Fallback parsing when LLMs fail.
        
        Args:
            query: Original query string
            
        Returns:
            Basic parsed parameters
        """
        query_lower = query.lower()
        
        # Basic keyword detection
        if "increase" in query_lower and "price" in query_lower:
            scenario = "increase_price"
        elif "decrease" in query_lower and "price" in query_lower:
            scenario = "decrease_price"
        elif "bulk" in query_lower or "together" in query_lower:
            scenario = "bulk_order"
        else:
            scenario = "unknown"
        
        return {
            "scenario": scenario,
            "item": "unknown",
            "change": "0",
            "current_value": None,
            "units": "%",
            "assumptions": "Fallback parsing used",
            "simulation_type": f"Basic {scenario} simulation",
            "parsing_source": "fallback"
        }
    
    def run_simulation(self, parsed_params: Dict) -> Dict:
        """
        Run the actual business simulation.
        
        Args:
            parsed_params: Parsed parameters from query
            
        Returns:
            Simulation results
        """
        scenario = parsed_params.get("scenario", "unknown")
        item = parsed_params.get("item", "unknown").lower()
        change = parsed_params.get("change", "0")
        
        # Get product data
        product_data = self.sample_data.get(item, self.sample_data.get("rice"))
        
        if scenario == "increase_price":
            return self._simulate_price_increase(parsed_params, product_data)
        elif scenario == "decrease_price":
            return self._simulate_price_decrease(parsed_params, product_data)
        elif scenario == "bulk_order":
            return self._simulate_bulk_order(parsed_params, product_data)
        else:
            return self._simulate_unknown_scenario(parsed_params, product_data)
    
    def _simulate_price_increase(self, params: Dict, product_data: Dict) -> Dict:
        """Simulate price increase scenario."""
        try:
            change_percent = float(params.get("change", "0").replace("+", "").replace("%", ""))
            current_price = product_data["current_price"]
            current_cost = product_data["current_cost"]
            weekly_sales = product_data["weekly_sales"]
            
            # Calculate new price and profit
            new_price = current_price * (1 + change_percent / 100)
            old_profit_per_unit = current_price - current_cost
            new_profit_per_unit = new_price - current_cost
            
            # Estimate sales impact (assume 2% decrease per 1% price increase)
            sales_impact = max(0.5, 1 - (change_percent * 0.02))
            new_sales = weekly_sales * sales_impact
            
            # Calculate profit changes
            old_weekly_profit = old_profit_per_unit * weekly_sales
            new_weekly_profit = new_profit_per_unit * new_sales
            profit_change = new_weekly_profit - old_weekly_profit
            
            return {
                "scenario": "increase_price",
                "item": params.get("item", "unknown"),
                "change": f"+{change_percent}%",
                "current_price": current_price,
                "new_price": round(new_price, 2),
                "current_weekly_profit": round(old_weekly_profit, 2),
                "new_weekly_profit": round(new_weekly_profit, 2),
                "profit_change": round(profit_change, 2),
                "sales_impact": f"{sales_impact:.1%}",
                "assumptions": f"Sales decrease by {100 - sales_impact*100:.1f}% with price increase",
                "recommendation": "Consider gradual price increases to minimize sales impact"
            }
            
        except Exception as e:
            logger.error(f"Price increase simulation failed: {e}")
            return {"error": f"Simulation failed: {str(e)}"}
    
    def _simulate_price_decrease(self, params: Dict, product_data: Dict) -> Dict:
        """Simulate price decrease scenario."""
        try:
            change_percent = float(params.get("change", "0").replace("-", "").replace("%", ""))
            current_price = product_data["current_price"]
            current_cost = product_data["current_cost"]
            weekly_sales = product_data["weekly_sales"]
            
            # Calculate new price and profit
            new_price = current_price * (1 - change_percent / 100)
            old_profit_per_unit = current_price - current_cost
            new_profit_per_unit = new_price - current_cost
            
            # Estimate sales impact (assume 3% increase per 1% price decrease)
            sales_impact = 1 + (change_percent * 0.03)
            new_sales = weekly_sales * sales_impact
            
            # Calculate profit changes
            old_weekly_profit = old_profit_per_unit * weekly_sales
            new_weekly_profit = new_profit_per_unit * new_sales
            profit_change = new_weekly_profit - old_weekly_profit
            
            return {
                "scenario": "decrease_price",
                "item": params.get("item", "unknown"),
                "change": f"-{change_percent}%",
                "current_price": current_price,
                "new_price": round(new_price, 2),
                "current_weekly_profit": round(old_weekly_profit, 2),
                "new_weekly_profit": round(new_weekly_profit, 2),
                "profit_change": round(profit_change, 2),
                "sales_impact": f"{sales_impact:.1%}",
                "assumptions": f"Sales increase by {sales_impact*100-100:.1f}% with price decrease",
                "recommendation": "Monitor profit margins and adjust strategy based on results"
            }
            
        except Exception as e:
            logger.error(f"Price decrease simulation failed: {e}")
            return {"error": f"Simulation failed: {str(e)}"}
    
    def _simulate_bulk_order(self, params: Dict, product_data: Dict) -> Dict:
        """Simulate bulk order scenario."""
        try:
            # Extract number of shops (basic parsing)
            change_str = params.get("change", "0")
            num_shops = int(re.findall(r'\d+', change_str)[0]) if re.findall(r'\d+', change_str) else 10
            
            current_price = product_data["current_price"]
            current_cost = product_data["current_cost"]
            weekly_sales = product_data["weekly_sales"]
            
            # Bulk order benefits
            # Assume 5% discount per 5 shops, max 20% discount
            discount_percent = min(20, (num_shops // 5) * 5)
            bulk_price = current_price * (1 - discount_percent / 100)
            
            # Calculate savings
            savings_per_unit = current_price - bulk_price
            total_savings = savings_per_unit * weekly_sales
            
            # Profit impact
            old_profit_per_unit = current_price - current_cost
            new_profit_per_unit = bulk_price - current_cost
            profit_impact = new_profit_per_unit - old_profit_per_unit
            
            return {
                "scenario": "bulk_order",
                "item": params.get("item", "unknown"),
                "num_shops": num_shops,
                "discount": f"{discount_percent}%",
                "current_price": current_price,
                "bulk_price": round(bulk_price, 2),
                "savings_per_unit": round(savings_per_unit, 2),
                "weekly_savings": round(total_savings, 2),
                "profit_impact": round(profit_impact, 2),
                "revenue": round(bulk_price * weekly_sales, 2),
                "profit": round((bulk_price - current_cost) * weekly_sales, 2),
                "assumptions": f"Bulk discount of {discount_percent}% for {num_shops} shops",
                "recommendation": "Consider forming buying groups for better supplier rates"
            }
            
        except Exception as e:
            logger.error(f"Bulk order simulation failed: {e}")
            return {"error": f"Simulation failed: {str(e)}"}
    
    def _simulate_unknown_scenario(self, params: Dict, product_data: Dict) -> Dict:
        """Handle unknown simulation scenarios."""
        return {
            "scenario": "unknown",
            "item": params.get("item", "unknown"),
            "error": "Unsupported simulation scenario",
            "supported_scenarios": ["increase_price", "decrease_price", "bulk_order"],
            "recommendation": "Please rephrase your query using supported scenario types"
        }
    
    def simulate(self, query: str, current_data: Optional[Dict] = None, user_id: Optional[str] = None, save_to_db: bool = True) -> Dict:
        """
        Main simulation function.
        
        Args:
            query: Natural language business query
            current_data: Optional current business data (overrides sample data)
            user_id: Optional user ID for database storage
            save_to_db: Whether to save results to database
            
        Returns:
            Complete simulation results
        """
        logger.info(f"Processing simulation query: {query}")
        
        # Override sample data if provided
        if current_data:
            self.sample_data.update(current_data)
        
        # Offline deterministic result when API keys are missing (for tests/dev)
        import os
        if not os.getenv("OPENAI_API_KEY") or not os.getenv("GOOGLE_API_KEY"):
            simulated = {
                "scenario": "increase_price" if "increase" in query.lower() else "price_change",
                "item": "rice",
                "change": "+5%",
                "current_price": 10.0,
                "new_price": 10.5,
                "current_weekly_profit": 200.0,
                "new_weekly_profit": 210.0,
                "profit_change": 10.0,
                "sales_impact": "98.0%",
                "assumptions": "Offline deterministic path",
                "recommendation": "Monitor elasticity",
            }
            final_parsed = {"scenario": simulated["scenario"], "item": simulated["item"], "change": simulated["change"]}
            final_result = {
                "query": query,
                "parsed_parameters": final_parsed,
                "simulation_results": simulated,
                "timestamp": str(Path(".").stat().st_mtime)
            }
            self._store_results(query, None, None, final_result)
            logger.info("Simulation complete (offline path)")
            return final_result

        # Parse query with both LLMs
        logger.info("Parsing query with GPT...")
        gpt_parsed = self.parse_query_with_gpt(query)
        
        logger.info("Parsing query with Gemini...")
        gemini_parsed = self.parse_query_with_gemini(query)
        
        # Arbitrate parsing results
        final_parsed = self.arbitrate_parsing(gpt_parsed, gemini_parsed)
        
        # Run simulation
        logger.info("Running simulation...")
        simulation_result = self.run_simulation(final_parsed)

        # Combine results
        final_result = {
            "query": query,
            "parsed_parameters": final_parsed,
            "simulation_results": simulation_result,
            "timestamp": str(Path(".").stat().st_mtime)
        }

        # Store results locally
        self._store_results(query, gpt_parsed, gemini_parsed, final_result)

        # Save to database if requested and user_id provided
        if save_to_db and user_id:
            try:
                from backend.db import save_simulation
                from backend.db import save_offline_transaction
                # Extract parameters for storage
                parameters = {
                    "scenario": final_parsed.get("scenario"),
                    "item": final_parsed.get("item"),
                    "change": final_parsed.get("change"),
                    "current_data": current_data or {}
                }

                simulation_id = save_simulation(
                    user_id=user_id,
                    query=query,
                    parameters=parameters,
                    result=final_result
                )
                if simulation_id:
                    final_result["simulation_id"] = simulation_id
                    logger.info(f"Simulation saved to database with ID: {simulation_id}")
                else:
                    logger.warning("Failed to save simulation to database; logging offline")
                    try:
                        # store minimal offline txn to indicate unsynced sim (reusing ledger)
                        save_offline_transaction({
                            "order_id": None,
                            "user_id": user_id,
                            "product_id": final_parsed.get("item"),
                            "quantity": 0,
                            "price_per_unit": 0,
                        })
                    except Exception:
                        pass
            except Exception as e:
                logger.error(f"Database save failed: {e}")
                final_result["db_save_error"] = str(e)

        logger.info("Simulation complete")
        return final_result
    
    def _store_results(self, query: str, gpt_parsed: Optional[Dict], 
                      gemini_parsed: Optional[Dict], final_result: Dict):
        """Store simulation results for analysis."""
        try:
            # Load existing results
            if self.results_file.exists():
                with open(self.results_file, 'r') as f:
                    all_results = json.load(f)
            else:
                all_results = []
            
            # Add new result
            result_entry = {
                "query": query,
                "timestamp": str(Path(".").stat().st_mtime),
                "gpt_parsing": gpt_parsed,
                "gemini_parsing": gemini_parsed,
                "final_result": final_result
            }
            
            all_results.append(result_entry)
            
            # Save updated results
            with open(self.results_file, 'w') as f:
                json.dump(all_results, f, indent=2)
                
            logger.info(f"Results stored in {self.results_file}")
            
        except Exception as e:
            logger.error(f"Failed to store results: {e}")
    
    def get_simulation_stats(self) -> Dict:
        """Get statistics about simulation results."""
        try:
            if not self.results_file.exists():
                return {"total_simulations": 0, "success_rate": 0}
            
            with open(self.results_file, 'r') as f:
                all_results = json.load(f)
            
            total = len(all_results)
            successful = sum(1 for r in all_results if not r.get("final_result", {}).get("error"))
            
            return {
                "total_simulations": total,
                "successful_simulations": successful,
                "success_rate": (successful / total * 100) if total > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}


# Convenience function for direct usage
def simulate(query: str, current_data: Optional[Dict] = None) -> Dict:
    """
    Convenience function to run a business simulation.
    
    Args:
        query: Natural language business query
        current_data: Optional current business data
        
    Returns:
        Simulation results
    """
    agent = SimulationAgent()
    return agent.simulate(query, current_data)


if __name__ == "__main__":
    # Test the agent
    print("🧪 Testing Simulation Agent")
    print("=" * 40)
    
    agent = SimulationAgent()
    print(f"✅ Agent initialized successfully")
    print(f"📊 Simulation stats: {agent.get_simulation_stats()}")
    
    # Test a simple simulation
    test_query = "What if I increase rice price by 5%?"
    print(f"\n🧪 Testing query: {test_query}")
    
    try:
        result = agent.simulate(test_query)
        print(f"✅ Simulation completed successfully")
        print(f"📋 Results: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
