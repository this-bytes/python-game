"""Budget system for managing company finances.

Handles monthly revenue/expense calculations, bankruptcy detection,
forced downsizing, and financial state tracking.
"""

import logging
from typing import Dict, Any, Tuple

from src.models.client import Client
from src.models.specialist import Specialist

logger = logging.getLogger(__name__)


def calculate_monthly_revenue(clients: list[Client]) -> float:
    """Calculate total monthly revenue from all active clients.
    
    Revenue = sum of (client.monthly_contract_value * satisfaction_multiplier)
    
    Where satisfaction_multiplier:
        1.0x at satisfaction = 1.0 (perfect)
        0.5x at satisfaction = 0.5 (poor)
        0.0x at satisfaction < 0.3 (client left)
    
    Args:
        clients: List of all clients
        
    Returns:
        Total monthly revenue in dollars
    """
    total_revenue = 0.0
    
    for client in clients:
        if not client.is_active:
            continue
        
        # Satisfaction directly multiplies contract value
        # satisfaction: 0.0-1.0
        # multiplier: 0.0-1.0
        revenue_from_client = client.monthly_contract_value * client.satisfaction
        total_revenue += revenue_from_client
        
        logger.debug(
            f"Client {client.company_name}: "
            f"${client.monthly_contract_value} * {client.satisfaction:.1%} = ${revenue_from_client:.0f}"
        )
    
    logger.info(f"Monthly revenue calculated: ${total_revenue:.0f}")
    return total_revenue


def calculate_monthly_expenses(
    specialists: list[Specialist],
    active_client_count: int,
    budget_config: Dict[str, float] | None = None
) -> float:
    """Calculate total monthly operating expenses.
    
    Expenses breakdown:
        - Specialist salaries: $3,000 per specialist
        - Infrastructure: $2,000 base + $500 per active client
        - Software licenses: $1,000 base + $200 per specialist
        - Fixed overhead: $1,500
    
    Args:
        specialists: List of all specialists
        active_client_count: Number of active clients
        budget_config: Optional config dict with custom rates
        
    Returns:
        Total monthly expenses in dollars
    """
    # Default rates
    specialist_salary = budget_config.get("specialist_salary_per_month", 3000.0) if budget_config else 3000.0
    infrastructure_base = budget_config.get("infrastructure_base", 2000.0) if budget_config else 2000.0
    infrastructure_per_client = budget_config.get("infrastructure_cost_per_client", 500.0) if budget_config else 500.0
    software_base = budget_config.get("software_license_base", 1000.0) if budget_config else 1000.0
    software_per_specialist = budget_config.get("software_license_per_specialist", 200.0) if budget_config else 200.0
    fixed_overhead = budget_config.get("fixed_overhead", 1500.0) if budget_config else 1500.0
    
    # Calculate by category
    specialist_salaries = len(specialists) * specialist_salary
    infrastructure = infrastructure_base + (active_client_count * infrastructure_per_client)
    software_licenses = software_base + (len(specialists) * software_per_specialist)
    
    total_expenses = specialist_salaries + infrastructure + software_licenses + fixed_overhead
    
    logger.debug(f"Specialist salaries: ${specialist_salaries:.0f} ({len(specialists)} × ${specialist_salary:.0f})")
    logger.debug(f"Infrastructure: ${infrastructure:.0f} (${infrastructure_base:.0f} + {active_client_count} × ${infrastructure_per_client:.0f})")
    logger.debug(f"Software licenses: ${software_licenses:.0f} (${software_base:.0f} + {len(specialists)} × ${software_per_specialist:.0f})")
    logger.debug(f"Fixed overhead: ${fixed_overhead:.0f}")
    logger.info(f"Monthly expenses calculated: ${total_expenses:.0f}")
    
    return total_expenses


def process_monthly_budget(
    game_state,
    specialists: list[Specialist],
    clients: list[Client],
    budget_config: Dict[str, float] | None = None
) -> Dict[str, Any]:
    """Execute end-of-month budget cycle.
    
    Process:
        1. Calculate revenue from active clients
        2. Calculate operating expenses
        3. Calculate profit (revenue - expenses)
        4. Apply profit to reserves
        5. Check for bankruptcy
        6. Check for critical condition
        7. Force downsizing if critical
        8. Update budget history
    
    Args:
        game_state: Current game state
        specialists: List of all specialists
        clients: List of all clients
        budget_config: Optional custom budget config
        
    Returns:
        Dict with budget results:
        {
            "revenue": float,
            "expenses": float,
            "profit": float,
            "reserves": float,
            "is_bankrupt": bool,
            "is_critical": bool,
            "downsizing_triggered": bool,
            "specialist_fired": str | None
        }
    """
    # Step 1: Calculate revenue
    active_clients = [c for c in clients if c.is_active]
    monthly_revenue = calculate_monthly_revenue(active_clients)
    
    # Step 2: Calculate expenses
    monthly_expenses = calculate_monthly_expenses(
        specialists,
        len(active_clients),
        budget_config
    )
    
    # Step 3: Calculate profit
    monthly_profit = monthly_revenue - monthly_expenses
    
    # Step 4: Update reserves
    game_state.budget.total_reserves += monthly_profit
    game_state.budget.monthly_revenue = monthly_revenue
    game_state.budget.monthly_expenses = monthly_expenses
    
    # Step 5: Track history
    game_state.budget.revenue_history.append(monthly_revenue)
    game_state.budget.expense_history.append(monthly_expenses)
    game_state.budget.profit_history.append(monthly_profit)
    
    # Step 6: Check bankruptcy
    is_bankrupt = game_state.budget.is_bankrupt()
    
    # Step 7: Check critical condition
    months_runway = game_state.budget.get_months_runway()
    is_critical = game_state.budget.is_in_critical_condition()
    
    # Step 8: Force downsizing if critical and unprofitable
    downsizing_triggered = False
    specialist_fired = None
    
    if is_critical and monthly_profit < 0:
        specialist_fired = _force_downsizing(game_state, specialists)
        if specialist_fired:
            downsizing_triggered = True
            logger.warning(f"Forced downsizing: Fired specialist {specialist_fired}")
    
    # Log summary
    logger.info(
        f"Monthly Budget: Revenue ${monthly_revenue:.0f} - "
        f"Expenses ${monthly_expenses:.0f} = "
        f"Profit ${monthly_profit:+.0f} | "
        f"Reserves: ${game_state.budget.total_reserves:+.0f} | "
        f"Runway: {months_runway:.1f} months"
    )
    
    return {
        "revenue": monthly_revenue,
        "expenses": monthly_expenses,
        "profit": monthly_profit,
        "reserves": game_state.budget.total_reserves,
        "is_bankrupt": is_bankrupt,
        "is_critical": is_critical,
        "months_runway": months_runway,
        "downsizing_triggered": downsizing_triggered,
        "specialist_fired": specialist_fired
    }


def _force_downsizing(game_state, specialists: list[Specialist]) -> str | None:
    """Fire the lowest-performing specialist to prevent bankruptcy.
    
    Performance metric: (level + total_incidents_resolved/10)
    
    Args:
        game_state: Current game state
        specialists: List of all specialists
        
    Returns:
        specialist_id of fired specialist, or None if none available to fire
    """
    if not specialists:
        logger.error("Cannot fire specialist: No specialists remaining!")
        return None
    
    # Calculate performance for each specialist
    # Better specialists have higher level and more incidents resolved
    specialist_performance = []
    
    for specialist in specialists:
        # Performance score: level + incidents/10
        # Higher score = better performer (keep them)
        performance = specialist.level + (specialist.total_incidents_resolved / 10.0)
        specialist_performance.append((specialist, performance))
    
    # Find lowest performer (lowest score = worst performer = fire them)
    lowest_performer, lowest_performance = min(specialist_performance, key=lambda x: x[1])
    
    logger.warning(
        f"Downsizing: Firing {lowest_performer.name} "
        f"(performance score: {lowest_performance:.1f})"
    )
    
    # Remove specialist from game state
    if lowest_performer in specialists:
        specialists.remove(lowest_performer)
    
    return lowest_performer.id


def check_game_over(game_state) -> Tuple[bool, str | None]:
    """Check if game is over (bankruptcy or no specialists).
    
    Args:
        game_state: Current game state
        
    Returns:
        (is_game_over, reason)
        reason: "bankruptcy", "no_specialists", or None
    """
    if game_state.budget.is_bankrupt():
        logger.error("GAME OVER: Bankruptcy!")
        return True, "bankruptcy"
    
    if not game_state.specialists or len(game_state.specialists) == 0:
        logger.error("GAME OVER: No specialists remaining!")
        return True, "no_specialists"
    
    return False, None
