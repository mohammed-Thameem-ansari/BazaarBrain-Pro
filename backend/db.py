"""
Database module for BazaarBrain-Pro using Supabase.

This module handles all database operations including:
- User management
- Transaction storage (OCR results)
- Simulation storage (what-if analysis results)
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid
import sqlite3

try:
    from supabase import create_client, Client
    from supabase.lib.client_options import ClientOptions
except ImportError:
    print("Warning: supabase-py not installed. Run: pip install supabase")
    Client = None

from .config import config


class DatabaseManager:
    """Manages database operations for BazaarBrain-Pro."""
    
    def __init__(self):
        """Initialize database connection."""
        self.client: Optional[Client] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Supabase."""
        try:
            if not Client:
                raise ImportError("supabase-py not available")
            
            # Validate configuration
            config.validate()
            
            # Create Supabase client
            self.client = create_client(
                config.SUPABASE_URL,
                config.SUPABASE_ANON_KEY,
                options=ClientOptions(
                    schema="public",
                    headers={
                        "X-Client-Info": "bazaarbrain-pro/1.0.0"
                    }
                )
            )
            
            # Test connection
            self._test_connection()
            print("✅ Database connection established successfully")
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.client = None
    
    def _test_connection(self):
        """Test database connection with a simple query."""
        try:
            # Try to fetch a single row from users table
            result = self.client.table("users").select("id").limit(1).execute()
            return True
        except Exception as e:
            print(f"⚠️  Connection test failed: {e}")
            return False
    
    def _ensure_tables(self):
        """Ensure required tables exist (for development/testing)."""
        # This would typically be handled by migrations in production
        # For now, we'll just log if tables don't exist
        try:
            # Check if tables exist by trying to select from them
            self.client.table("users").select("id").limit(1).execute()
            self.client.table("transactions").select("id").limit(1).execute()
            self.client.table("simulations").select("id").limit(1).execute()
            return True
        except Exception as e:
            print(f"⚠️  Some tables may not exist: {e}")
            print("💡 Run the SQL schema creation script in Supabase dashboard")
            return False
    
    def save_transaction(
        self, 
        user_id: str, 
        raw_input: str, 
        parsed_json: Dict[str, Any], 
        source: str = "image"
    ) -> Optional[str]:
        """
        Save a transaction (OCR result) to the database.
        
        Args:
            user_id: UUID of the user
            raw_input: Original input (image path, text, etc.)
            parsed_json: Structured JSON result from OCR
            source: Source type (e.g., "image", "text", "receipt")
            
        Returns:
            Transaction ID if successful, None otherwise
        """
        try:
            if not self.client:
                print("❌ Database not connected")
                return None
            
            transaction_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "raw_input": raw_input,
                "parsed_json": parsed_json,
                "source": source,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("transactions").insert(transaction_data).execute()
            
            if result.data:
                print(f"✅ Transaction saved with ID: {transaction_data['id']}")
                return transaction_data['id']
            else:
                print("❌ Failed to save transaction")
                return None
                
        except Exception as e:
            print(f"❌ Error saving transaction: {e}")
            return None
    
    def save_simulation(
        self, 
        user_id: str, 
        query: str, 
        parameters: Dict[str, Any], 
        result: Dict[str, Any]
    ) -> Optional[str]:
        """
        Save a simulation result to the database.
        
        Args:
            user_id: UUID of the user
            query: Original query text
            parameters: Parsed parameters used for simulation
            result: Simulation results
            
        Returns:
            Simulation ID if successful, None otherwise
        """
        try:
            if not self.client:
                print("❌ Database not connected")
                return None
            
            simulation_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "query": query,
                "parameters": parameters,
                "result": result,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result_data = self.client.table("simulations").insert(simulation_data).execute()
            
            if result_data.data:
                print(f"✅ Simulation saved with ID: {simulation_data['id']}")
                return simulation_data['id']
            else:
                print("❌ Failed to save simulation")
                return None
                
        except Exception as e:
            print(f"❌ Error saving simulation: {e}")
            return None
    
    def get_transactions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve transactions for a specific user.
        
        Args:
            user_id: UUID of the user
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction dictionaries
        """
        try:
            if not self.client:
                print("❌ Database not connected")
                return []
            
            result = (
                self.client.table("transactions")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            return result.data or []
            
        except Exception as e:
            print(f"❌ Error retrieving transactions: {e}")
            return []
    
    def get_simulations(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve simulations for a specific user.
        
        Args:
            user_id: UUID of the user
            limit: Maximum number of simulations to return
            
        Returns:
            List of simulation dictionaries
        """
        try:
            if not self.client:
                print("❌ Database not connected")
                return []
            
            result = (
                self.client.table("simulations")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            return result.data or []
            
        except Exception as e:
            print(f"❌ Error retrieving simulations: {e}")
            return []

    # Day 6: Collective Orders CRUD
    def save_collective_order(self, order: Dict[str, Any]) -> Optional[str]:
        """Save a collective order to Supabase."""
        try:
            if not self.client:
                print("❌ Database not connected")
                return None

            payload = {
                "order_id": str(uuid.uuid4()),
                "user_id": order["user_id"],
                "product_id": order["product_id"],
                "quantity": int(order["quantity"]),
                "price_per_unit": float(order.get("price_per_unit", 0)),
                "created_at": datetime.utcnow().isoformat(),
            }
            res = self.client.table("collective_orders").insert(payload).execute()
            if res.data:
                return payload["order_id"]
            return None
        except Exception as e:
            print(f"❌ Error saving collective order: {e}")
            return None

    def get_collective_orders(self) -> List[Dict[str, Any]]:
        """Fetch aggregated collective orders by product_id."""
        try:
            if not self.client:
                print("❌ Database not connected")
                return []
            # Return most recent aggregates per product
            res = (
                self.client.rpc(
                    "",  # fallback: select with group by when rpc not available
                )
            )
        except Exception:
            # Fallback to manual aggregation through select
            try:
                result = (
                    self.client.table("collective_orders")
                    .select("product_id, aggregated_quantity, price_per_unit")
                    .order("updated_at", desc=True)
                    .execute()
                )
                # Reduce to latest per product
                latest: Dict[str, Dict[str, Any]] = {}
                for row in (result.data or []):
                    pid = row["product_id"]
                    if pid not in latest:
                        latest[pid] = row
                return list(latest.values())
            except Exception as e:
                print(f"❌ Error retrieving collective orders: {e}")
                return []

    # Day 6: Offline ledger (SQLite)
    def _sqlite_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect("offline_ledger.db")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT,
                user_id TEXT,
                product_id TEXT,
                quantity INTEGER,
                price_per_unit REAL,
                synced INTEGER DEFAULT 0
            )
            """
        )
        return conn

    def save_offline_transaction(self, txn: Dict[str, Any]) -> int:
        try:
            conn = self._sqlite_conn()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO transactions(order_id, user_id, product_id, quantity, price_per_unit, synced) VALUES(?,?,?,?,?,0)",
                (
                    txn.get("order_id"),
                    txn.get("user_id"),
                    txn.get("product_id"),
                    int(txn.get("quantity", 0)),
                    float(txn.get("price_per_unit", 0)),
                ),
            )
            conn.commit()
            rowid = cur.lastrowid
            conn.close()
            return rowid
        except Exception as e:
            print(f"❌ Offline save failed: {e}")
            return -1

    def _unsynced_transactions(self) -> List[Tuple]:
        conn = self._sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, order_id, user_id, product_id, quantity, price_per_unit FROM transactions WHERE synced = 0")
        rows = cur.fetchall()
        conn.close()
        return rows

    def sync_to_supabase(self) -> int:
        """Try to push unsynced offline transactions to Supabase. Returns number synced."""
        if not self.client:
            return 0
        rows = self._unsynced_transactions()
        if not rows:
            return 0
        synced = 0
        conn = self._sqlite_conn()
        try:
            for row in rows:
                _id, order_id, user_id, product_id, quantity, price_per_unit = row
                payload = {
                    "order_id": order_id or str(uuid.uuid4()),
                    "user_id": user_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "price_per_unit": price_per_unit,
                    "created_at": datetime.utcnow().isoformat(),
                }
                try:
                    res = self.client.table("collective_orders").insert(payload).execute()
                    if res.data:
                        conn.execute("UPDATE transactions SET synced = 1 WHERE id = ?", (_id,))
                        synced += 1
                except Exception:
                    pass
            conn.commit()
        finally:
            conn.close()
        return synced
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User dictionary or None if not found
        """
        try:
            if not self.client:
                print("❌ Database not connected")
                return None
            
            result = (
                self.client.table("users")
                .select("*")
                .eq("email", email)
                .limit(1)
                .execute()
            )
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"❌ Error retrieving user: {e}")
            return None
    
    def create_user(self, email: str, password: Optional[str] = None) -> Optional[str]:
        """
        Create a new user.
        
        Args:
            email: User's email address
            password: Optional password (if not using Supabase auth)
            
        Returns:
            User ID if successful, None otherwise
        """
        try:
            if not self.client:
                print("❌ Database not connected")
                return None
            
            user_data = {
                "id": str(uuid.uuid4()),
                "email": email,
                "created_at": datetime.utcnow().isoformat()
            }
            
            if password:
                user_data["password"] = password
            
            result = self.client.table("users").insert(user_data).execute()
            
            if result.data:
                print(f"✅ User created with ID: {user_data['id']}")
                return user_data['id']
            else:
                print("❌ Failed to create user")
                return None
                
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None
    
    def health_check(self) -> bool:
        """Check database health status."""
        try:
            if not self.client:
                return False
            
            # Try a simple query
            self.client.table("users").select("id").limit(1).execute()
            return True
            
        except Exception:
            return False


# Global database instance
db = DatabaseManager()


# Convenience functions for easy access
def save_transaction(user_id: str, raw_input: str, parsed_json: Dict[str, Any], source: str = "image") -> Optional[str]:
    """Save a transaction to the database."""
    return db.save_transaction(user_id, raw_input, parsed_json, source)


def save_simulation(user_id: str, query: str, parameters: Dict[str, Any], result: Dict[str, Any]) -> Optional[str]:
    """Save a simulation to the database."""
    return db.save_simulation(user_id, query, parameters, result)


def get_transactions(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get transactions for a user."""
    return db.get_transactions(user_id, limit)


def get_simulations(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get simulations for a user."""
    return db.get_simulations(user_id, limit)


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email."""
    return db.get_user_by_email(email)


def create_user(email: str, password: Optional[str] = None) -> Optional[str]:
    """Create a new user."""
    return db.create_user(email, password)


def health_check() -> bool:
    """Check database health."""
    return db.health_check()

# Day 6 convenience exports
def save_collective_order(order: Dict[str, Any]) -> Optional[str]:
    return db.save_collective_order(order)


def get_collective_orders() -> List[Dict[str, Any]]:
    return db.get_collective_orders()


def save_offline_transaction(txn: Dict[str, Any]) -> int:
    return db.save_offline_transaction(txn)


def sync_to_supabase() -> int:
    return db.sync_to_supabase()
