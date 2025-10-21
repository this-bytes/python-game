"""Passive Income System for generating income from retainers, investments, and reputation.

This module manages passive income sources that generate money over time without
active incident resolution, including contract retainers, investments, and reputation bonuses.
"""

from typing import Dict, List, Any, Optional
import random

from src.models.client import Client
from src.utils.logger import GameLogger


class PassiveIncomeSystem:
    """Manages passive income generation from various sources.
    
    This system calculates and applies passive income from:
    - Contract retainers (continuous payments from clients)
    - Investments (low/medium/high risk with returns)
    - Reputation bonuses (passive multiplier based on client satisfaction)
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[GameLogger] = None):
        """Initialize the passive income system.
        
        Args:
            config: Game configuration dictionary containing passive income settings
            logger: Optional logger for passive income events
        """
    # Class-level annotations for static analysis
    self._logger: GameLogger = logger or GameLogger("passive_income")
    self._config: Dict[str, Any] = config.get("passive_income", {})
        
        # Investment configuration
        self._investment_types: Dict[str, Dict[str, float]] = self._config.get("investment_types", {
            "low_risk": {"return_rate": 0.02, "risk": 0.0},
            "medium_risk": {"return_rate": 0.05, "risk": 0.1},
            "high_risk": {"return_rate": 0.10, "risk": 0.25}
        })
        
        # Retainer income multiplier
    self._retainer_multiplier: float = self._config.get("retainer_income_multiplier", 1.0)
        
        # Statistics tracking
        self._stats: Dict[str, float] = {
            "total_retainer_income": 0.0,
            "total_investment_income": 0.0,
            "total_investment_losses": 0.0,
            "total_reputation_bonus": 0.0
        }

    def calculate_retainer_income(self, clients: List[Client], delta_time: float) -> float:
        """Calculate retainer income from active client contracts.
        
        Args:
            clients: List of active clients
            delta_time: Time elapsed since last calculation (in seconds)
            
        Returns:
            Total retainer income for the time period
        """
        if not clients:
            return 0.0
        
        total_income = 0.0
        
        for client in clients:
            # Only active clients with good reputation provide retainers
            if hasattr(client, 'is_active') and client.is_active():
                # Base retainer is a small percentage of contract value per hour
                retainer_rate = 0.001  # 0.1% per hour
                hourly_retainer = client.contract_value * retainer_rate
                
                # Convert delta_time from seconds to hours
                hours_elapsed = delta_time / 3600.0
                
                # Calculate income for this period
                income = hourly_retainer * hours_elapsed * self._retainer_multiplier
                total_income += income
        
        self._stats["total_retainer_income"] += total_income
        
        if total_income > 0:
            # Use GameLogger wrapper API directly
            self._logger.debug(
                f"[PASSIVE_INCOME] Retainer income: ${total_income:.2f} from {len(clients)} clients"
            )
        
        return total_income

    def calculate_investment_returns(self, investments: Dict[str, float], 
                                   delta_time: float) -> float:
        """Calculate returns (or losses) from investments.
        
        Args:
            investments: Dictionary mapping investment type to amount invested
            delta_time: Time elapsed since last calculation (in seconds)
            
        Returns:
            Net return (positive for gains, negative for losses)
        """
        if not investments:
            return 0.0
        
        total_return = 0.0
        
        for investment_type, amount in investments.items():
            if amount <= 0:
                continue
            
            investment_config = self._investment_types.get(investment_type)
            if not investment_config:
                # Unknown investment types are a harmless warning
                self._logger.warning(
                    f"[PASSIVE_INCOME] Unknown investment type: {investment_type}"
                )
                continue
            
            return_rate = investment_config["return_rate"]  # Annual return rate
            risk = investment_config["risk"]  # Probability of loss
            
            # Convert annual rate to rate per second
            seconds_per_year = 365 * 24 * 3600
            rate_per_second = return_rate / seconds_per_year
            
            # Calculate base return
            base_return = amount * rate_per_second * delta_time
            
            # Apply risk (random chance of loss)
            if risk > 0:
                # Roll for loss every ~24 hours of game time
                loss_check_interval = 24 * 3600  # 24 hours
                checks_needed = int(delta_time / loss_check_interval)
                
                for _ in range(checks_needed):
                    if random.random() < risk:
                        # Loss event: lose a percentage of the investment
                        loss_percentage = random.uniform(0.05, 0.15)  # 5-15% loss
                        loss = amount * loss_percentage
                        base_return -= loss
                        self._stats["total_investment_losses"] += loss
                        
                        # Log investment loss via GameLogger
                        self._logger.info(
                            f"[PASSIVE_INCOME] Investment loss: ${loss:.2f} on {investment_type}"
                        )
            
            total_return += base_return
        
        if total_return > 0:
            self._stats["total_investment_income"] += total_return
            self._logger.debug(
                f"[PASSIVE_INCOME] Investment returns: ${total_return:.2f}"
            )
        
        return total_return

    def calculate_reputation_bonus(self, clients: List[Client]) -> float:
        """Calculate passive income multiplier based on client reputation.
        
        Args:
            clients: List of clients
            
        Returns:
            Reputation bonus multiplier (e.g., 1.1 for 10% bonus)
        """
        if not clients:
            return 1.0
        
        # Calculate average reputation across all clients
        total_reputation = sum(client.reputation for client in clients)
        avg_reputation = total_reputation / len(clients)
        
        # Reputation ranges from 0-100
        # Bonus ranges from 0% at rep 0 to 50% at rep 100
        reputation_bonus = (avg_reputation / 100.0) * 0.5
        multiplier = 1.0 + reputation_bonus
        
        self._stats["total_reputation_bonus"] = reputation_bonus
        
        return multiplier

    def apply_passive_income(self, game_state: Any, delta_time: float) -> Dict[str, Any]:
        """Apply all passive income sources to game state.
        
        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update (in seconds)
            
        Returns:
            Dictionary containing breakdown of passive income
        """
        # Calculate retainer income
        retainer_income = self.calculate_retainer_income(game_state.clients, delta_time)
        
        # Calculate investment returns
        investments = getattr(game_state, 'investments', {})
        investment_return = self.calculate_investment_returns(investments, delta_time)
        
        # Calculate reputation bonus multiplier
        reputation_multiplier = self.calculate_reputation_bonus(game_state.clients)
        
        # Apply reputation multiplier to retainer income
        retainer_income_with_bonus = retainer_income * reputation_multiplier
        bonus_amount = retainer_income_with_bonus - retainer_income
        
        # Total passive income
        total_income = retainer_income_with_bonus + investment_return
        
        # Apply to game state
        if total_income != 0:
            game_state.current_money += total_income
            if total_income > 0:
                game_state.total_money_earned += total_income
        
        # Log significant passive income
        if abs(total_income) > 1.0:
            self._logger.info(
                f"[PASSIVE_INCOME] Total passive income: ${total_income:.2f} "
                f"(retainer: ${retainer_income:.2f}, reputation bonus: ${bonus_amount:.2f}, "
                f"investments: ${investment_return:.2f})"
            )
        
        return {
            "retainer_income": retainer_income,
            "reputation_multiplier": reputation_multiplier,
            "reputation_bonus": bonus_amount,
            "investment_return": investment_return,
            "total_income": total_income
        }

    def invest(self, game_state: Any, investment_type: str, amount: float) -> Dict[str, Any]:
        """Make an investment.
        
        Args:
            game_state: Current game state
            investment_type: Type of investment (low_risk, medium_risk, high_risk)
            amount: Amount to invest
            
        Returns:
            Dictionary containing investment result
        """
        if investment_type not in self._investment_types:
            return {
                "success": False,
                "error": f"Invalid investment type: {investment_type}"
            }
        
        if amount <= 0:
            return {
                "success": False,
                "error": "Investment amount must be positive"
            }
        
        if game_state.current_money < amount:
            return {
                "success": False,
                "error": "Insufficient funds",
                "available": game_state.current_money
            }
        
        # Deduct money
        game_state.current_money -= amount
        
        # Add to investments
        if not hasattr(game_state, 'investments'):
            game_state.investments = {}
        
        if investment_type not in game_state.investments:
            game_state.investments[investment_type] = 0.0
        
        game_state.investments[investment_type] += amount
        
        investment_config = self._investment_types[investment_type]
        
        self._logger.info(
            f"[PASSIVE_INCOME] Invested ${amount:.2f} in {investment_type} "
            f"(return: {investment_config['return_rate']*100:.1f}%, "
            f"risk: {investment_config['risk']*100:.1f}%)"
        )
        
        return {
            "success": True,
            "investment_type": investment_type,
            "amount": amount,
            "total_invested": game_state.investments[investment_type],
            "return_rate": investment_config["return_rate"],
            "risk": investment_config["risk"]
        }

    def withdraw(self, game_state: Any, investment_type: str, amount: float) -> Dict[str, Any]:
        """Withdraw from an investment.
        
        Args:
            game_state: Current game state
            investment_type: Type of investment
            amount: Amount to withdraw
            
        Returns:
            Dictionary containing withdrawal result
        """
        if not hasattr(game_state, 'investments'):
            return {
                "success": False,
                "error": "No investments found"
            }
        
        if investment_type not in game_state.investments:
            return {
                "success": False,
                "error": f"No {investment_type} investments found"
            }
        
        available = game_state.investments[investment_type]
        
        if amount <= 0:
            return {
                "success": False,
                "error": "Withdrawal amount must be positive"
            }
        
        if amount > available:
            return {
                "success": False,
                "error": "Insufficient investment balance",
                "available": available
            }
        
        # Withdraw
        game_state.investments[investment_type] -= amount
        game_state.current_money += amount
        
        self._logger.info(
            f"[PASSIVE_INCOME] Withdrew ${amount:.2f} from {investment_type}"
        )
        
        return {
            "success": True,
            "investment_type": investment_type,
            "amount": amount,
            "remaining": game_state.investments[investment_type]
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get passive income statistics.
        
        Returns:
            Dictionary containing statistics
        """
        return self._stats.copy()

    def reset_statistics(self) -> None:
        """Reset passive income statistics."""
        self._stats = {
            "total_retainer_income": 0.0,
            "total_investment_income": 0.0,
            "total_investment_losses": 0.0,
            "total_reputation_bonus": 0.0
        }
