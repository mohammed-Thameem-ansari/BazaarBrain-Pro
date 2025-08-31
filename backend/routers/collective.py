"""
Collective Bargaining router.

Endpoints:
- POST /collective_order: place or join a collective order for a product
- GET /collective_order: list user's collective orders (demo only returns aggregates)

For demo purposes, data is kept in-memory. Replace with DB tables later.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
import logging

from ..auth import get_current_user_payload
from ..db import save_collective_order, get_collective_orders, save_offline_transaction, sync_to_supabase

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store: product_id -> { total_qty, participants, base_ppu }
aggregates: Dict[str, Dict[str, Any]] = {}


class CollectiveOrderInput(BaseModel):
    product_id: str
    quantity: int


def _estimate_price_and_savings(product_id: str, total_qty: int) -> Dict[str, Any]:
    # Simple pricing curve for demo: base price $10; discounts at quantity tiers
    base_price = 10.0
    discount = 0.0
    if total_qty >= 1000:
        discount = 0.20
    elif total_qty >= 500:
        discount = 0.12
    elif total_qty >= 200:
        discount = 0.08
    elif total_qty >= 100:
        discount = 0.05

    price_per_unit = round(base_price * (1 - discount), 2)
    estimated_savings = round(discount * 100, 1)
    return {"price_per_unit": price_per_unit, "estimated_savings": estimated_savings}


@router.post("/collective_order")
def place_collective_order(payload: CollectiveOrderInput, user=Depends(get_current_user_payload)) -> Dict[str, Any]:
    try:
        if payload.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")

        pid = payload.product_id
        # Try saving to Supabase
        order_id = save_collective_order({
            "user_id": user.get("sub"),
            "product_id": pid,
            "quantity": payload.quantity,
            "price_per_unit": 0,
        })
        if order_id:
            # Attempt to compute aggregates via DB
            db_aggs = get_collective_orders()
            entry = next((a for a in db_aggs if a.get("product_id") == pid), None)
            total_qty = entry.get("aggregated_quantity", 0) if entry else payload.quantity
            pricing = _estimate_price_and_savings(pid, total_qty)
            return {
                "product_id": pid,
                "total_quantity": total_qty,
                "participants": None,
                **pricing,
            }

        # If DB unavailable, fallback to offline ledger + memory aggregate
        save_offline_transaction({
            "order_id": None,
            "user_id": user.get("sub"),
            "product_id": pid,
            "quantity": payload.quantity,
            "price_per_unit": 0,
        })
        entry = aggregates.get(pid, {"total_quantity": 0, "participants": set(), "base_ppu": 10.0})
        entry["total_quantity"] += payload.quantity
        entry["participants"].add(user.get("sub"))
        aggregates[pid] = entry
        pricing = _estimate_price_and_savings(pid, entry["total_quantity"])
        return {"product_id": pid, "total_quantity": entry["total_quantity"], "participants": len(entry["participants"]), **pricing}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to place collective order: {e}")
        raise HTTPException(status_code=500, detail="Failed to place collective order")


@router.get("/collective_order")
def get_collective_orders_route(user=Depends(get_current_user_payload)) -> Dict[str, Any]:
    try:
        # Try syncing any offline entries first
        try:
            sync_to_supabase()
        except Exception:
            pass

        # Try DB aggregates
        data: List[Dict[str, Any]] = get_collective_orders() or []
        if not data:
            # Fallback to memory
            for pid, entry in aggregates.items():
                pricing = _estimate_price_and_savings(pid, entry["total_quantity"])
                data.append({
                    "product_id": pid,
                    "total_quantity": entry["total_quantity"],
                    "participants": len(entry["participants"]),
                    **pricing,
                })
        return {"success": True, "orders": data}
    except Exception as e:
        logger.error(f"Failed to fetch collective orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch collective orders")
