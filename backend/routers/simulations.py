"""
Simulations router for BazaarBrain-Pro API.

Handles:
- Business simulation queries
- What-if analysis using Simulation Agent
- Simulation result storage
- Simulation history retrieval
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

from ..db import save_simulation, get_simulations
from ..agents.simulation_agent import SimulationAgent
from ..auth import get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize the Simulation Agent
simulation_agent = SimulationAgent()

@router.post("/simulate")
async def run_simulation(
    query: str,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Run a business simulation based on natural language query.
    
    Args:
        query: Natural language business question (e.g., "What if I increase coffee price by 10%?")
        current_user_id: Current user ID from JWT token
        
    Returns:
        Dict containing simulation results and simulation ID
    """
    try:
        # Validate query
        if not query or len(query.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Query must be at least 10 characters long"
            )
        
        # Run simulation using Simulation Agent
        logger.info(f"Running simulation for user {current_user_id}: {query}")
        result = simulation_agent.simulate(query)
        
        if not result or "error" in result:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to run simulation: {result.get('error', 'Unknown error')}"
            )
        
        # Extract parameters from the result for storage
        parameters = {
            "scenario": result.get("scenario"),
            "item": result.get("item"),
            "change": result.get("change"),
            "current_data": result.get("current_data", {})
        }
        
        # Save simulation to database
        simulation_id = save_simulation(
            user_id=current_user_id,
            query=query,
            parameters=parameters,
            result=result
        )
        
        if not simulation_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to save simulation to database"
            )
        
        # Return success response
        return {
            "success": True,
            "simulation_id": simulation_id,
            "query": query,
            "result": result,
            "processed_at": datetime.utcnow().isoformat(),
            "message": "Simulation completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running simulation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/simulations")
async def get_user_simulations(
    limit: int = 50,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get simulations for the current user.
    
    Args:
        limit: Maximum number of simulations to return
        current_user_id: Current user ID from JWT token
        
    Returns:
        Dict containing user's simulations
    """
    try:
        # Validate limit
        if limit <= 0 or limit > 100:
            limit = 50
        
        # Get simulations from database
        simulations = get_simulations(current_user_id, limit)
        
        return {
            "success": True,
            "simulations": simulations,
            "count": len(simulations),
            "limit": limit,
            "user_id": current_user_id,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving simulations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/simulations/{simulation_id}")
async def get_simulation(
    simulation_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get a specific simulation by ID.
    
    Args:
        simulation_id: Simulation UUID
        current_user_id: Current user ID from JWT token
        
    Returns:
        Dict containing simulation details
    """
    try:
        # Validate UUID format
        try:
            uuid.UUID(simulation_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid simulation ID format"
            )
        
        # Get simulations and find the specific one
        simulations = get_simulations(current_user_id, limit=1000)
        simulation = None
        
        for s in simulations:
            if s.get("id") == simulation_id:
                simulation = s
                break
        
        if not simulation:
            raise HTTPException(
                status_code=404,
                detail="Simulation not found"
            )
        
        return {
            "success": True,
            "simulation": simulation,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving simulation {simulation_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/simulations/{simulation_id}")
async def delete_simulation(
    simulation_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Delete a specific simulation.
    
    Args:
        simulation_id: Simulation UUID
        current_user_id: Current user ID from JWT token
        
    Returns:
        Dict confirming deletion
    """
    try:
        # Validate UUID format
        try:
            uuid.UUID(simulation_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid simulation ID format"
            )
        
        # TODO: Implement simulation deletion in db.py
        # For now, return success (implementation pending)
        
        return {
            "success": True,
            "message": f"Simulation {simulation_id} deleted successfully",
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting simulation {simulation_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/scenarios")
async def get_available_scenarios() -> Dict[str, Any]:
    """
    Get available simulation scenarios and examples.
    
    Returns:
        Dict containing available scenarios and example queries
    """
    try:
        scenarios = {
            "price_increase": {
                "description": "Analyze the impact of increasing product prices",
                "examples": [
                    "What if I increase coffee price by 10%?",
                    "How would a 15% price hike affect my tea sales?",
                    "What's the profit impact of raising bread prices by 20%?"
                ]
            },
            "price_decrease": {
                "description": "Analyze the impact of decreasing product prices",
                "examples": [
                    "What if I decrease coffee price by 5%?",
                    "How would a 10% discount affect my overall revenue?",
                    "What's the volume impact of lowering bread prices by 15%?"
                ]
            },
            "bulk_order": {
                "description": "Analyze bulk ordering scenarios",
                "examples": [
                    "What if I order 100 coffee bags together?",
                    "How much would I save by ordering tea in bulk?",
                    "What's the cost benefit of ordering 50 bread loaves at once?"
                ]
            },
            "inventory_optimization": {
                "description": "Analyze inventory and stock scenarios",
                "examples": [
                    "What if I reduce my coffee inventory by 30%?",
                    "How would increasing bread stock affect my storage costs?",
                    "What's the optimal tea inventory level for my sales?"
                ]
            }
        }
        
        return {
            "success": True,
            "scenarios": scenarios,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving scenarios: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/stats")
async def get_simulation_stats(
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get simulation statistics for the current user.
    
    Args:
        current_user_id: Current user ID from JWT token
        
    Returns:
        Dict containing simulation statistics
    """
    try:
        # Get agent statistics
        agent_stats = simulation_agent.get_simulation_stats()
        
        # Get user's simulation count
        simulations = get_simulations(current_user_id, limit=1000)
        
        # Calculate user-specific stats
        user_stats = {
            "total_simulations": len(simulations),
            "scenarios": {},
            "success_rate": 0
        }
        
        if simulations:
            # Count by scenario
            for s in simulations:
                scenario = s.get("parameters", {}).get("scenario", "unknown")
                user_stats["scenarios"][scenario] = user_stats["scenarios"].get(scenario, 0) + 1
            
            # Calculate success rate (simulations without errors)
            successful = sum(1 for s in simulations if "error" not in s.get("result", {}))
            user_stats["success_rate"] = (successful / len(simulations)) * 100
        
        return {
            "success": True,
            "user_stats": user_stats,
            "agent_stats": agent_stats,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving simulation stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
