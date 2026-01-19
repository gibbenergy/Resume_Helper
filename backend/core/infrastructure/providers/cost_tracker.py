"""
Cost Tracking Utilities for Resume Helper

This module handles all cost tracking functionality for LLM operations,
providing a clean separation between business logic and UI components.
"""

import os
import json
import datetime as dt
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Import LiteLLM cost tracking functions
try:
    from litellm.cost_calculator import completion_cost, cost_per_token
    from litellm import model_cost
    LITELLM_COST_AVAILABLE = True
except ImportError:
    LITELLM_COST_AVAILABLE = False
    completion_cost = None
    cost_per_token = None
    model_cost = None


class CostTracker:
    """
    Handles cost tracking for LLM operations with persistent storage.
    """
    
    def __init__(self, temp_dir: str):
        """Initialize the cost tracker with a temp directory for storage."""
        self.temp_dir = temp_dir
        self.cost_log_path = os.path.join(temp_dir, "cost_tracking.json")
    
    def load_cost_history(self) -> float:
        """Load total cost from file."""
        try:
            if os.path.exists(self.cost_log_path):
                with open(self.cost_log_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("total_cost", 0.0)
        except Exception as e:
            logger.error(f"Error loading cost history: {e}")
        return 0.0
    
    def save_cost_history(self, total_cost: float) -> bool:
        """Save total cost to file."""
        try:
            os.makedirs(os.path.dirname(self.cost_log_path), exist_ok=True)
            with open(self.cost_log_path, 'w', encoding='utf-8') as f:
                json.dump({"total_cost": total_cost}, f)
            return True
        except Exception as e:
            logger.error(f"Error saving cost history: {e}")
            return False
    
    def calculate_operation_cost(self, llm_response: Dict[str, Any], model_used: str, operation_type: str = "unknown") -> Optional[Dict[str, Any]]:
        """Calculate cost from LiteLLM response."""
        try:
            if not LITELLM_COST_AVAILABLE:
                logger.warning("⚠️ WARNING: LiteLLM cost calculator not available - cost tracking disabled. Install/update litellm package for accurate cost tracking.")
                print("⚠️ WARNING: LiteLLM cost calculator not available - cost tracking disabled. Install/update litellm package for accurate cost tracking.")
                return {"cost": 0.0}
            
            usage = llm_response.get("usage", {})
            if not usage:
                return {"cost": 0.0}
            
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            
            cost = 0.0
            if prompt_tokens > 0 or completion_tokens > 0:
                try:
                    if cost_per_token is not None:
                        prompt_cost, completion_cost_val = cost_per_token(
                            model=model_used,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens
                        )
                        cost = (prompt_cost or 0.0) + (completion_cost_val or 0.0)
                    else:
                        logger.warning(f"⚠️ WARNING: cost_per_token function not available for model '{model_used}' - cost tracking disabled.")
                        print(f"⚠️ WARNING: cost_per_token function not available for model '{model_used}' - cost tracking disabled.")
                        return {"cost": 0.0}
                except Exception as e:
                    logger.warning(f"⚠️ WARNING: Failed to calculate cost for model '{model_used}' (error: {e}) - cost tracking disabled.")
                    print(f"⚠️ WARNING: Failed to calculate cost for model '{model_used}' (error: {e}) - cost tracking disabled.")
                    return {"cost": 0.0}
            
            return {"cost": cost}
        except Exception as e:
            logger.error(f"Error calculating operation cost: {e}")
            return {"cost": 0.0}
    
    def log_operation_cost(self, cost_info: Dict[str, Any]) -> None:
        """Add operation cost to total."""
        if not cost_info:
            return
        try:
            total_cost = self.load_cost_history()
            total_cost += cost_info["cost"]
            self.save_cost_history(total_cost)
        except Exception as e:
            logger.error(f"Error logging operation cost: {e}")
    
    def format_cost_display(self) -> str:
        """Format cost for display in the UI."""
        try:
            total_cost = self.load_cost_history()
            return f"Total Cost: ${total_cost:.6f}"
        except Exception as e:
            logger.error(f"Error formatting cost display: {e}")
            return "Total Cost: Error"
    
def track_llm_operation(temp_dir: str, llm_response: Dict[str, Any], model_used: str, operation_type: str) -> None:
    """Convenience function to track an LLM operation cost."""
    tracker = CostTracker(temp_dir)
    cost_info = tracker.calculate_operation_cost(llm_response, model_used, operation_type)
    if cost_info:
        tracker.log_operation_cost(cost_info)


def get_cost_display(temp_dir: str) -> str:
    """Convenience function to get formatted cost display."""
    tracker = CostTracker(temp_dir)
    return tracker.format_cost_display() 