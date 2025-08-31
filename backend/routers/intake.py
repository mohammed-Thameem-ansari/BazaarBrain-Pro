"""
Intake router: Accepts natural language input and routes via IntakeAgent.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Dict
import logging

from ..auth import get_current_user_id
from agents.intake_agent import IntakeAgent

logger = logging.getLogger(__name__)
router = APIRouter()

agent = IntakeAgent()


class IntakeRequest(BaseModel):
    text: str


@router.post("/intake")
def intake(req: IntakeRequest, current_user_id: str = Depends(get_current_user_id)) -> Dict[str, Any]:
    try:
        if not req.text or len(req.text.strip()) < 2:
            raise HTTPException(status_code=400, detail="Text is required")

        result = agent.route_request(req.text)
        return {"success": True, "user_id": current_user_id, "routed": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Intake routing failed: {e}")
        raise HTTPException(status_code=500, detail="Routing failed")
