#!/usr/bin/env python3
"""
Reality Capture Agent v2 - Dual LLM OCR with Arbitration

This agent processes images (receipts, bills, handwritten notes) using both
GPT-4o Vision and Gemini Pro Vision, then applies arbitration logic to
determine the best result or merge conflicting outputs.

Features:
- Dual LLM processing for accuracy
- Image preprocessing (resize, grayscale)
- Arbitration logic for conflicting results
- Structured JSON output
- Result logging and storage
"""

import json
import base64
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image
import io

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

class RealityCaptureAgent:
    """
    Enhanced OCR agent using dual LLM approach with arbitration logic.
    """
    
    def __init__(self):
        """Initialize the Reality Capture Agent with both LLM clients."""
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.gemini_model = None
        self._setup_gemini()
        
        # Load prompts
        self.ocr_prompt = self._load_prompt("prompts/ocr_prompt.txt")
        
        # Results storage
        self.results_file = Path("tests/ocr_results.json")
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
            return "Extract business data from this image in JSON format."
    
    def preprocess_image(self, image_path: str) -> bytes:
        """
        Preprocess image for better OCR results.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Processed image as bytes
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large (max 1024x1024)
                max_size = 1024
                if max(img.size) > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Convert to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=85)
                return img_byte_arr.getvalue()
                
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            # Fallback: read original image
            with open(image_path, 'rb') as f:
                return f.read()
    
    def process_with_gpt_vision(self, image_bytes: bytes) -> Optional[Dict]:
        """
        Process image using OpenAI GPT-4o Vision.
        
        Args:
            image_bytes: Image as bytes
            
        Returns:
            Extracted data as dictionary or None if failed
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.ocr_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Please analyze this image and extract the business data."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"GPT Vision response: {content[:100]}...")
            
            # Try to parse JSON response
            return self._parse_json_response(content)
            
        except Exception as e:
            logger.error(f"GPT Vision processing failed: {e}")
            return None
    
    def process_with_gemini_vision(self, image_bytes: bytes) -> Optional[Dict]:
        """
        Process image using Google Gemini Pro Vision.
        
        Args:
            image_bytes: Image as bytes
            
        Returns:
            Extracted data as dictionary or None if failed
        """
        try:
            if not self.gemini_model:
                logger.warning("Gemini model not available")
                return None
            
            # Convert bytes to PIL Image for Gemini
            image = Image.open(io.BytesIO(image_bytes))
            
            response = self.gemini_model.generate_content([
                self.ocr_prompt,
                image
            ])
            
            content = response.text.strip()
            logger.info(f"Gemini Vision response: {content[:100]}...")
            
            # Try to parse JSON response
            return self._parse_json_response(content)
            
        except Exception as e:
            logger.error(f"Gemini Vision processing failed: {e}")
            return None
    
    def _parse_json_response(self, content: str) -> Optional[Dict]:
        """
        Parse JSON response from LLM, handling common formatting issues.
        
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
    
    def arbitrate_ocr(self, gpt_output: Optional[Dict], gemini_output: Optional[Dict]) -> Dict:
        """
        Arbitration logic for dual LLM OCR results.
        
        Args:
            gpt_output: Output from GPT Vision
            gemini_output: Output from Gemini Vision
            
        Returns:
            Final arbitrated result
        """
        # 1. If both are identical
        if gpt_output == gemini_output and gpt_output is not None:
            return {**gpt_output, "source": "gpt+gemini_agree"}
        
        # 2. If one is missing or empty, prefer the other
        if not gpt_output and gemini_output:
            return {**gemini_output, "source": "gemini_only"}
        if not gemini_output and gpt_output:
            return {**gpt_output, "source": "gpt_only"}
        
        # 3. If both failed
        if not gpt_output and not gemini_output:
            return {
                "items": [],
                "total": 0,
                "source": "both_failed",
                "error": "Both LLMs failed to process the image"
            }
        
        # 4. Compare length of items (prefer more structured JSON)
        gpt_items = gpt_output.get("items", []) if gpt_output else []
        gemini_items = gemini_output.get("items", []) if gemini_output else []
        
        if len(gpt_items) > len(gemini_items):
            return {**gpt_output, "source": "gpt_preferred"}
        elif len(gemini_items) > len(gpt_items):
            return {**gemini_output, "source": "gemini_preferred"}
        
        # 5. Merge items if both contain useful but different data
        merged_items = gpt_items.copy()
        for item in gemini_items:
            if item not in merged_items:
                merged_items.append(item)
        
        merged = {
            "items": merged_items,
            "total": max(
                gpt_output.get("total", 0) if gpt_output else 0,
                gemini_output.get("total", 0) if gemini_output else 0
            ),
            "source": "merged"
        }
        
        # Copy other fields from the more complete output
        if gpt_output and len(gpt_output) > len(gemini_output or {}):
            merged.update({k: v for k, v in gpt_output.items() if k not in merged})
        elif gemini_output:
            merged.update({k: v for k, v in gemini_output.items() if k not in merged})
        
        return merged
    
    def process_receipt(self, image_path: str, user_id: Optional[str] = None, save_to_db: bool = True) -> Dict:
        """
        Main function to process a receipt/bill image.
        
        Args:
            image_path: Path to the image file
            user_id: Optional user ID for database storage
            save_to_db: Whether to save results to database
            
        Returns:
            Structured data extracted from the image
        """
        logger.info(f"Processing image: {image_path}")
        
        # Preprocess image
        image_bytes = self.preprocess_image(image_path)
        
        # Process with both LLMs
        logger.info("Processing with GPT Vision...")
        gpt_result = self.process_with_gpt_vision(image_bytes)
        
        logger.info("Processing with Gemini Vision...")
        gemini_result = self.process_with_gemini_vision(image_bytes)
        
        # Arbitrate results
        final_result = self.arbitrate_ocr(gpt_result, gemini_result)
        
        # Add metadata
        final_result.update({
            "image_path": image_path,
            "processing_timestamp": str(Path(image_path).stat().st_mtime),
            "gpt_success": gpt_result is not None,
            "gemini_success": gemini_result is not None
        })
        
        # Store results locally
        self._store_results(image_path, gpt_result, gemini_result, final_result)
        
        # Save to database if requested and user_id provided
        if save_to_db and user_id:
            try:
                from backend.db import save_transaction
                transaction_id = save_transaction(
                    user_id=user_id,
                    raw_input=image_path,
                    parsed_json=final_result,
                    source="image"
                )
                if transaction_id:
                    final_result["transaction_id"] = transaction_id
                    logger.info(f"Transaction saved to database with ID: {transaction_id}")
                else:
                    logger.warning("Failed to save transaction to database")
            except Exception as e:
                logger.error(f"Database save failed: {e}")
                final_result["db_save_error"] = str(e)
        
        logger.info(f"Processing complete. Source: {final_result.get('source', 'unknown')}")
        return final_result
    
    def _store_results(self, image_path: str, gpt_result: Optional[Dict], 
                      gemini_result: Optional[Dict], final_result: Dict):
        """
        Store processing results for analysis and debugging.
        
        Args:
            image_path: Path to the processed image
            gpt_result: Raw GPT output
            gemini_result: Raw Gemini output
            final_result: Final arbitrated result
        """
        try:
            # Load existing results
            if self.results_file.exists():
                with open(self.results_file, 'r') as f:
                    all_results = json.load(f)
            else:
                all_results = []
            
            # Add new result
            result_entry = {
                "image_path": image_path,
                "timestamp": str(Path(image_path).stat().st_mtime),
                "gpt_output": gpt_result,
                "gemini_output": gemini_result,
                "final_result": final_result
            }
            
            all_results.append(result_entry)
            
            # Save updated results
            with open(self.results_file, 'w') as f:
                json.dump(all_results, f, indent=2)
                
            logger.info(f"Results stored in {self.results_file}")
            
        except Exception as e:
            logger.error(f"Failed to store results: {e}")
    
    def get_processing_stats(self) -> Dict:
        """
        Get statistics about processing results.
        
        Returns:
            Dictionary with processing statistics
        """
        try:
            if not self.results_file.exists():
                return {"total_processed": 0, "success_rate": 0}
            
            with open(self.results_file, 'r') as f:
                all_results = json.load(f)
            
            total = len(all_results)
            successful = sum(1 for r in all_results if r.get("final_result", {}).get("items"))
            
            return {
                "total_processed": total,
                "successful_extractions": successful,
                "success_rate": (successful / total * 100) if total > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}


# Convenience function for direct usage
def process_receipt(image_path: str) -> Dict:
    """
    Convenience function to process a receipt image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Structured data extracted from the image
    """
    agent = RealityCaptureAgent()
    return agent.process_receipt(image_path)


if __name__ == "__main__":
    # Test the agent
    print("🧪 Testing Reality Capture Agent v2")
    print("=" * 50)
    
    # This would normally process a real image
    # For now, just show the agent is working
    agent = RealityCaptureAgent()
    print(f"✅ Agent initialized successfully")
    print(f"📊 Processing stats: {agent.get_processing_stats()}")
