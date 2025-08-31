#!/usr/bin/env python3
"""
Intake Agent - Intelligent Request Router

This agent acts as the central dispatcher for all user interactions,
classifying inputs and routing them to the appropriate specialized agents.

Features:
- Intent classification using dual LLMs
- Image vs text input detection
- Routing to specialized agents
- Request logging and tracking
- Extensible routing framework
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Union
from PIL import Image

# AI imports
from openai import OpenAI
import google.generativeai as genai

# Local imports
import sys
sys.path.append('..')
from backend.config import config

# Agent imports
from .reality_capture_agent import RealityCaptureAgent
from .simulation_agent import SimulationAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntakeAgent:
    """
    Central routing agent that classifies and dispatches user requests.
    """
    
    def __init__(self):
        """Initialize the Intake Agent with routing capabilities."""
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.gemini_model = None
        self._setup_gemini()
        
        # Initialize specialized agents
        self.reality_capture_agent = RealityCaptureAgent()
        self.simulation_agent = SimulationAgent()
        
        # Intent classification prompt
        self.classification_prompt = self._load_classification_prompt()
        
        # Supported categories
        self.categories = [
            "image_processing",      # Receipts, bills, handwritten notes
            "simulation_query",      # What-if scenarios
            "sales_log",            # Sales data entry
            "financial_query",      # Financial analysis
            "inventory_query",      # Stock questions
            "general"               # General business questions
        ]
        
        # Results storage
        self.results_file = Path("tests/intake_results.json")
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
    
    def _load_classification_prompt(self) -> str:
        """Load the intent classification prompt."""
        return """
You are BazaarBrain's intelligent intake classifier. Your job is to categorize user inputs into the most appropriate business category.

Available categories:
1. image_processing - Receipts, bills, handwritten notes, any image that needs data extraction
2. simulation_query - "What if" scenarios, price changes, bulk orders, business simulations
3. sales_log - Sales data entry, transaction logging, daily sales records
4. financial_query - Profit analysis, expense tracking, financial reports
5. inventory_query - Stock levels, inventory management, product availability
6. general - Greetings, general business advice, unspecific queries

IMPORTANT: Respond with ONLY valid JSON. No explanations.

Required JSON structure:
{
  "intent": "category_name",
  "confidence": "high|medium|low",
  "reasoning": "Brief explanation of classification",
  "requires_agent": "agent_name_if_needed"
}

Classification rules:
- If input mentions images, photos, receipts, bills → image_processing
- If input starts with "what if", "simulate", "if" → simulation_query
- If input mentions sales, transactions, daily records → sales_log
- If input mentions profit, expenses, money, financial → financial_query
- If input mentions stock, inventory, products → inventory_query
- Otherwise → general

Examples:
Input: "Process this receipt image" → {"intent": "image_processing", "confidence": "high", "reasoning": "Explicitly mentions image processing", "requires_agent": "reality_capture"}
Input: "What if I increase rice price by 5%?" → {"intent": "simulation_query", "confidence": "high", "reasoning": "What-if scenario", "requires_agent": "simulation"}
Input: "Add today's milk sales ₹500" → {"intent": "sales_log", "confidence": "high", "reasoning": "Sales data entry", "requires_agent": "sales"}
Input: "How much profit did I make?" → {"intent": "financial_query", "confidence": "high", "reasoning": "Profit analysis", "requires_agent": "financial"}
Input: "Good morning!" → {"intent": "general", "confidence": "high", "reasoning": "General greeting", "requires_agent": "none"}

Remember: Output ONLY the JSON, no other text.
"""
    
    def classify_intent_with_gpt(self, user_input: str) -> Optional[Dict]:
        """
        Classify user intent using OpenAI GPT.
        
        Args:
            user_input: User's input text
            
        Returns:
            Classification result as dictionary or None if failed
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.classification_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"GPT classification: {content[:100]}...")
            
            return self._parse_json_response(content)
            
        except Exception as e:
            logger.error(f"GPT intent classification failed: {e}")
            return None
    
    def classify_intent_with_gemini(self, user_input: str) -> Optional[Dict]:
        """
        Classify user intent using Google Gemini.
        
        Args:
            user_input: User's input text
            
        Returns:
            Classification result as dictionary or None if failed
        """
        try:
            if not self.gemini_model:
                logger.warning("Gemini model not available")
                return None
            
            response = self.gemini_model.generate_content([
                self.classification_prompt,
                user_input
            ])
            
            content = response.text.strip()
            logger.info(f"Gemini classification: {content[:100]}...")
            
            return self._parse_json_response(content)
            
        except Exception as e:
            logger.error(f"Gemini intent classification failed: {e}")
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
    
    def arbitrate_classification(self, gpt_output: Optional[Dict], gemini_output: Optional[Dict]) -> Dict:
        """
        Arbitration logic for intent classification results.
        
        Args:
            gpt_output: Output from GPT classification
            gemini_output: Output from Gemini classification
            
        Returns:
            Final arbitrated classification
        """
        # 1. If both are identical
        if gpt_output == gemini_output and gpt_output is not None:
            return {**gpt_output, "classification_source": "gpt+gemini_agree"}
        
        # 2. If one is missing or empty, prefer the other
        if not gpt_output and gemini_output:
            return {**gemini_output, "classification_source": "gemini_only"}
        if not gemini_output and gpt_output:
            return {**gpt_output, "classification_source": "gpt_only"}
        
        # 3. If both failed, use fallback classification
        if not gpt_output and not gemini_output:
            return self._fallback_classification("")
        
        # 4. Prefer the more confident classification
        gpt_confidence = gpt_output.get("confidence", "low") if gpt_output else "low"
        gemini_confidence = gemini_output.get("confidence", "low") if gemini_output else "low"
        
        confidence_order = {"high": 3, "medium": 2, "low": 1}
        gpt_score = confidence_order.get(gpt_confidence, 1)
        gemini_score = confidence_order.get(gemini_confidence, 1)
        
        if gpt_score >= gemini_score:
            return {**gpt_output, "classification_source": "gpt_preferred"}
        else:
            return {**gemini_output, "classification_source": "gemini_preferred"}
    
    def _fallback_classification(self, user_input: str) -> Dict:
        """
        Fallback classification when LLMs fail.
        
        Args:
            user_input: Original user input
            
        Returns:
            Basic classification result
        """
        input_lower = user_input.lower()
        
        # Basic keyword detection
        if any(word in input_lower for word in ["image", "photo", "receipt", "bill"]):
            intent = "image_processing"
            requires_agent = "reality_capture"
        elif any(word in input_lower for word in ["what if", "simulate", "if"]):
            intent = "simulation_query"
            requires_agent = "simulation"
        elif any(word in input_lower for word in ["sales", "transaction", "log"]):
            intent = "sales_log"
            requires_agent = "sales"
        elif any(word in input_lower for word in ["profit", "expense", "money", "financial"]):
            intent = "financial_query"
            requires_agent = "financial"
        elif any(word in input_lower for word in ["stock", "inventory", "product"]):
            intent = "inventory_query"
            requires_agent = "inventory"
        else:
            intent = "general"
            requires_agent = "none"
        
        return {
            "intent": intent,
            "confidence": "low",
            "reasoning": "Fallback classification used",
            "requires_agent": requires_agent,
            "classification_source": "fallback"
        }
    
    def detect_input_type(self, user_input: Union[str, Path]) -> str:
        """
        Detect if input is text or image.
        
        Args:
            user_input: User input (text string or image path)
            
        Returns:
            Input type: "text" or "image"
        """
        if isinstance(user_input, Path) or (isinstance(user_input, str) and Path(user_input).exists()):
            try:
                # Try to open as image
                with Image.open(user_input) as img:
                    img.verify()
                return "image"
            except Exception:
                # Not a valid image, treat as text
                return "text"
        return "text"
    
    def route_request(self, user_input: Union[str, Path]) -> Dict:
        """
        Main routing function that classifies and routes user requests.
        
        Args:
            user_input: User input (text or image path)
            
        Returns:
            Routing result with agent response
        """
        logger.info(f"Processing input: {user_input}")
        
        # Detect input type
        input_type = self.detect_input_type(user_input)
        
        if input_type == "image":
            # Route to Reality Capture Agent
            logger.info("Routing image to Reality Capture Agent")
            try:
                result = self.reality_capture_agent.process_receipt(str(user_input))
                return {
                    "input_type": "image",
                    "intent": "image_processing",
                    "routed_to": "reality_capture_agent",
                    "result": result,
                    "status": "success"
                }
            except Exception as e:
                logger.error(f"Image processing failed: {e}")
                return {
                    "input_type": "image",
                    "intent": "image_processing",
                    "routed_to": "reality_capture_agent",
                    "error": str(e),
                    "status": "failed"
                }
        
        else:
            # Text input - classify intent
            user_input_str = str(user_input)
            
            # Classify with both LLMs
            logger.info("Classifying text intent with GPT...")
            gpt_classification = self.classify_intent_with_gpt(user_input_str)
            
            logger.info("Classifying text intent with Gemini...")
            gemini_classification = self.classify_intent_with_gemini(user_input_str)
            
            # Arbitrate classification
            final_classification = self.arbitrate_classification(gpt_classification, gemini_classification)
            
            # Route based on classification
            intent = final_classification.get("intent", "general")
            routed_to = final_classification.get("requires_agent", "none")
            
            logger.info(f"Intent: {intent}, Routing to: {routed_to}")
            
            # Execute routing
            if routed_to == "simulation":
                try:
                    result = self.simulation_agent.simulate(user_input_str)
                    return {
                        "input_type": "text",
                        "intent": intent,
                        "routed_to": "simulation_agent",
                        "classification": final_classification,
                        "result": result,
                        "status": "success"
                    }
                except Exception as e:
                    logger.error(f"Simulation failed: {e}")
                    return {
                        "input_type": "text",
                        "intent": intent,
                        "routed_to": "simulation_agent",
                        "classification": final_classification,
                        "error": str(e),
                        "status": "failed"
                    }
            
            elif routed_to == "reality_capture":
                return {
                    "input_type": "text",
                    "intent": intent,
                    "routed_to": "reality_capture_agent",
                    "classification": final_classification,
                    "message": "Please provide an image for processing",
                    "status": "requires_image"
                }
            
            elif routed_to in ["sales", "financial", "inventory"]:
                return {
                    "input_type": "text",
                    "intent": intent,
                    "routed_to": routed_to,
                    "classification": final_classification,
                    "message": f"{routed_to.title()} agent not yet implemented",
                    "status": "not_implemented"
                }
            
            else:
                # General query
                return {
                    "input_type": "text",
                    "intent": intent,
                    "routed_to": "general",
                    "classification": final_classification,
                    "message": "General business query received",
                    "status": "success"
                }
    
    def process_batch(self, inputs: List[Union[str, Path]]) -> List[Dict]:
        """
        Process multiple inputs in batch.
        
        Args:
            inputs: List of user inputs
            
        Returns:
            List of routing results
        """
        results = []
        for user_input in inputs:
            try:
                result = self.route_request(user_input)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process input {user_input}: {e}")
                results.append({
                    "input": user_input,
                    "error": str(e),
                    "status": "failed"
                })
        return results
    
    def get_routing_stats(self) -> Dict:
        """Get statistics about routing results."""
        try:
            if not self.results_file.exists():
                return {"total_routed": 0, "success_rate": 0}
            
            with open(self.results_file, 'r') as f:
                all_results = json.load(f)
            
            total = len(all_results)
            successful = sum(1 for r in all_results if r.get("status") == "success")
            
            return {
                "total_routed": total,
                "successful_routes": successful,
                "success_rate": (successful / total * 100) if total > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}


# Convenience function for direct usage
def route_request(user_input: Union[str, Path]) -> Dict:
    """
    Convenience function to route a user request.
    
    Args:
        user_input: User input (text or image path)
        
    Returns:
        Routing result
    """
    agent = IntakeAgent()
    return agent.route_request(user_input)


if __name__ == "__main__":
    # Test the agent
    print("🧪 Testing Intake Agent")
    print("=" * 40)
    
    agent = IntakeAgent()
    print(f"✅ Agent initialized successfully")
    print(f"📊 Routing stats: {agent.get_routing_stats()}")
    
    # Test text classification
    test_queries = [
        "What if I increase rice price by 5%?",
        "Process this receipt image",
        "Add today's milk sales ₹500",
        "How much profit did I make last month?",
        "Good morning!"
    ]
    
    print(f"\n🧪 Testing text classification:")
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = agent.route_request(query)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
