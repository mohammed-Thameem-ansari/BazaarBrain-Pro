"""
Database module for BazaarBrain-Pro using Supabase.

This module handles all database operations including:
- User management
- Transaction storage (OCR results)
- Simulation storage (what-if analysis results)
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

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
