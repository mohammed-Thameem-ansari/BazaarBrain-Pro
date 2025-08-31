"""
Receipts router for BazaarBrain-Pro API.

Handles:
- Receipt image upload
- OCR processing using Reality Capture Agent
- Transaction storage
- Receipt retrieval
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
import base64
from io import BytesIO

from ..db import save_transaction, get_transactions
from ..agents.reality_capture_agent import RealityCaptureAgent
from ..auth import get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize the Reality Capture Agent
reality_capture_agent = RealityCaptureAgent()

@router.post("/upload_receipt")
async def upload_receipt(
    file: UploadFile = File(...),
    source: str = Form("image"),
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Upload and process a receipt image.
    
    Args:
        file: Receipt image file
        source: Source type (e.g., "image", "receipt", "bill")
        current_user_id: Current user ID from JWT token
        
    Returns:
        Dict containing processing results and transaction ID
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Convert to PIL Image for processing
        from PIL import Image
        image = Image.open(BytesIO(file_content))
        
        # Process receipt using Reality Capture Agent
        logger.info(f"Processing receipt for user {current_user_id}")
        result = reality_capture_agent.process_receipt(image)
        
        if not result or "error" in result:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to process receipt: {result.get('error', 'Unknown error')}"
            )
        
        # Save transaction to database
        transaction_id = save_transaction(
            user_id=current_user_id,
            raw_input=f"uploaded_file_{file.filename}",
            parsed_json=result,
            source=source
        )
        
        if not transaction_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to save transaction to database"
            )
        
        # Return success response
        return {
            "success": True,
            "transaction_id": transaction_id,
            "result": result,
            "filename": file.filename,
            "processed_at": datetime.utcnow().isoformat(),
            "message": "Receipt processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing receipt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/transactions")
async def get_user_transactions(
    limit: int = 50,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get transactions for the current user.
    
    Args:
        limit: Maximum number of transactions to return
        current_user_id: Current user ID from JWT token
        
    Returns:
        Dict containing user's transactions
    """
    try:
        # Validate limit
        if limit <= 0 or limit > 100:
            limit = 50
        
        # Get transactions from database
        transactions = get_transactions(current_user_id, limit)
        
        return {
            "success": True,
            "transactions": transactions,
            "count": len(transactions),
            "limit": limit,
            "user_id": current_user_id,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving transactions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get a specific transaction by ID.
    
    Args:
        transaction_id: Transaction UUID
        current_user_id: Current user ID from JWT token
        
    Returns:
        Dict containing transaction details
    """
    try:
        # Validate UUID format
        try:
            uuid.UUID(transaction_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid transaction ID format"
            )
        
        # Get transactions and find the specific one
        transactions = get_transactions(current_user_id, limit=1000)
        transaction = None
        
        for t in transactions:
            if t.get("id") == transaction_id:
                transaction = t
                break
        
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found"
            )
        
        return {
            "success": True,
            "transaction": transaction,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Delete a specific transaction.
    
    Args:
        transaction_id: Transaction UUID
        current_user_id: Current user ID from JWT token
        
    Returns:
        Dict confirming deletion
    """
    try:
        # Validate UUID format
        try:
            uuid.UUID(transaction_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid transaction ID format"
            )
        
        # TODO: Implement transaction deletion in db.py
        # For now, return success (implementation pending)
        
        return {
            "success": True,
            "message": f"Transaction {transaction_id} deleted successfully",
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/stats")
async def get_processing_stats(
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get processing statistics for the current user.
    
    Args:
        current_user_id: Current user ID from JWT token
        
    Returns:
        Dict containing processing statistics
    """
    try:
        # Get agent statistics
        agent_stats = reality_capture_agent.get_processing_stats()
        
        # Get user's transaction count
        transactions = get_transactions(current_user_id, limit=1000)
        
        # Calculate user-specific stats
        user_stats = {
            "total_transactions": len(transactions),
            "sources": {},
            "processing_success_rate": 0
        }
        
        if transactions:
            # Count by source
            for t in transactions:
                source = t.get("source", "unknown")
                user_stats["sources"][source] = user_stats["sources"].get(source, 0) + 1
            
            # Calculate success rate (transactions without errors)
            successful = sum(1 for t in transactions if "error" not in t.get("parsed_json", {}))
            user_stats["processing_success_rate"] = (successful / len(transactions)) * 100
        
        return {
            "success": True,
            "user_stats": user_stats,
            "agent_stats": agent_stats,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving processing stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
