"""
GameLogic - Business rules and game mechanics layer.

This module contains all business logic, validation, and game mechanics
that operate on the state managed by StateManager.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

from src.core.state_manager import StateManager
from src.models.specialist import Specialist
from src.models.incident import Incident
from src.models.client import Client
from src.models.contract import Contract
from src.models.budget import Budget
from src.models.sla_tracker import SLATracker
from src.core.event_bus import get_event_bus

logger = logging.getLogger(__name__)


@dataclass
class AssignmentResult:
    """Result of an incident assignment operation."""
    success: bool
    message: str
    specialist: Optional[Specialist] = None
    incident: Optional[Incident] = None


@dataclass
class ResolutionResult:
    """Result of an incident resolution operation."""
    success: bool
    message: str
    xp_gained: int = 0
    money_earned: float = 0.0
    sla_met: bool = False
    time_taken: float = 0.0


class GameLogic:
    """
    Business rules and game mechanics layer.

    GameLogic contains all validation, business rules, and game mechanics
    that operate on state data. It enforces game rules without managing
    the actual storage of entities.
    """

    def __init__(self, game_config: Dict[str, Any]):
        """
        Initialize GameLogic with game configuration.

        Args:
            game_config: Game configuration dictionary
        """
        self.game_config = game_config
        self.event_bus = get_event_bus()

    # ===== SPECIALIST BUSINESS LOGIC =====

    def can_assign_specialist_to_incident(
        self,
        specialist: Specialist,
        incident: Incident,
        state_manager: StateManager
    ) -> Tuple[bool, str]:
        """
        Validate if a specialist can be assigned to an incident.

        Args:
            specialist: The specialist to assign
            incident: The incident to assign to
            state_manager: Current state manager

        Returns:
            Tuple of (can_assign, reason_if_not)
        """
        # Check if specialist exists and is available
        if not specialist.is_available():
            return False, f"Specialist {specialist.name} is not available"

        # Check specialty compatibility
        if specialist.specialty != incident.specialty_required:
            return False, f"Specialist specialty '{specialist.specialty}' doesn't match required '{incident.specialty_required}'"

        # Check if incident is already assigned
        if incident.assigned_specialist_id:
            return False, f"Incident is already assigned to specialist {incident.assigned_specialist_id}"

        # Check if incident is resolved
        if incident.is_resolved():
            return False, "Incident is already resolved"

        return True, ""

    def assign_specialist_to_incident(
        self,
        specialist: Specialist,
        incident: Incident,
        state_manager: StateManager
    ) -> AssignmentResult:
        """
        Assign a specialist to an incident with validation.

        Args:
            specialist: The specialist to assign
            incident: The incident to assign to
            state_manager: Current state manager

        Returns:
            AssignmentResult with success status and details
        """
        # Validate assignment
        can_assign, reason = self.can_assign_specialist_to_incident(
            specialist, incident, state_manager
        )

        if not can_assign:
            return AssignmentResult(
                success=False,
                message=reason,
                specialist=specialist,
                incident=incident
            )

        # Perform assignment
        specialist.assigned_incident_id = incident.id
        specialist.status = "assigned"
        incident.assigned_specialist_id = specialist.id
        incident.status = "assigned"
        incident.sla_deadline = state_manager.game_time + incident.sla_seconds

        # Emit event
        self.event_bus.publish("incident_assigned", {
            "specialist_id": specialist.id,
            "incident_id": incident.id,
            "timestamp": state_manager.game_time
        })

        logger.info(f"Assigned specialist {specialist.name} to incident {incident.incident_type}")

        return AssignmentResult(
            success=True,
            message=f"Successfully assigned {specialist.name} to {incident.incident_type}",
            specialist=specialist,
            incident=incident
        )

    def calculate_specialist_salary(self, specialist: Specialist) -> float:
        """
        Calculate monthly salary for a specialist.

        Args:
            specialist: The specialist

        Returns:
            Monthly salary amount
        """
        base_salary = self.game_config.get("specialist_hiring_cost_base", 2000)
        level_multiplier = 1.0 + (specialist.level - 1) * 0.2  # 20% increase per level

        return base_salary * level_multiplier

    # ===== INCIDENT BUSINESS LOGIC =====

    def resolve_incident(
        self,
        incident: Incident,
        specialist: Specialist,
        state_manager: StateManager
    ) -> ResolutionResult:
        """
        Resolve an incident with game mechanics.

        Args:
            incident: The incident to resolve
            specialist: The specialist resolving it
            state_manager: Current state manager

        Returns:
            ResolutionResult with outcome details
        """
        if incident.is_resolved():
            return ResolutionResult(
                success=False,
                message="Incident is already resolved"
            )

        if incident.assigned_specialist_id != specialist.id:
            return ResolutionResult(
                success=False,
                message=f"Incident is not assigned to specialist {specialist.name}"
            )

        # Calculate resolution time based on specialist skills
        resolution_time = self._calculate_resolution_time(incident, specialist)

        # Determine success based on specialist accuracy and incident difficulty
        success_chance = self._calculate_success_chance(specialist, incident)
        success = self._roll_success(success_chance)

        # Calculate rewards
        xp_gained, money_earned = self._calculate_rewards(incident, specialist, success)

        # Check SLA compliance
        sla_met = self._check_sla_compliance(incident, state_manager.game_time + resolution_time)

        # Update incident
        incident.status = "resolved"
        incident.completion_time = state_manager.game_time + resolution_time

        # Clear specialist assignment
        specialist.assigned_incident_id = None
        specialist.status = "available"
        specialist.total_incidents_resolved += 1

        # Update metrics
        state_manager.update_metrics(
            incidents_resolved=1,
            money_earned=money_earned,
            xp_gained=xp_gained
        )

        # Award XP to specialist
        specialist.xp += xp_gained

        # Emit event
        self.event_bus.publish("incident_resolved", {
            "incident_id": incident.id,
            "specialist_id": specialist.id,
            "success": success,
            "xp_gained": xp_gained,
            "money_earned": money_earned,
            "sla_met": sla_met,
            "resolution_time": resolution_time
        })

        message = f"Incident {incident.incident_type} resolved by {specialist.name}"
        if success:
            message += f" successfully (+{xp_gained} XP, +${money_earned})"
        else:
            message += " with failure"

        return ResolutionResult(
            success=success,
            message=message,
            xp_gained=xp_gained,
            money_earned=money_earned,
            sla_met=sla_met,
            time_taken=resolution_time
        )

    def _calculate_resolution_time(self, incident: Incident, specialist: Specialist) -> float:
        """Calculate time to resolve incident."""
        base_time = incident.sla_seconds

        # Specialist speed affects resolution time
        speed_modifier = specialist.stats.speed / 100.0  # Speed is 0-100, convert to multiplier

        # Difficulty affects resolution time
        difficulty_modifier = 1.0 + (incident.difficulty - 1) * 0.25  # +25% per difficulty level

        return base_time / speed_modifier * difficulty_modifier

    def _calculate_success_chance(self, specialist: Specialist, incident: Incident) -> float:
        """Calculate probability of successful resolution."""
        base_chance = specialist.stats.accuracy / 100.0  # Accuracy is 0-100, convert to 0-1

        # Difficulty penalty
        difficulty_penalty = (incident.difficulty - 1) * 0.1  # -10% per difficulty level

        # Specialty bonus
        specialty_bonus = 0.2 if specialist.specialty == incident.specialty_required else 0.0

        final_chance = base_chance - difficulty_penalty + specialty_bonus
        return max(0.1, min(0.95, final_chance))  # Clamp between 10% and 95%

    def _roll_success(self, success_chance: float) -> bool:
        """Roll for success based on chance."""
        import random
        return random.random() < success_chance

    def _calculate_rewards(
        self,
        incident: Incident,
        specialist: Specialist,
        success: bool
    ) -> Tuple[int, float]:
        """Calculate XP and money rewards."""
        if not success:
            return 0, 0.0

        # Base XP from incident
        base_xp = incident.xp_reward

        # Specialist XP bonus
        xp_bonus = specialist.stats.experience_bonus
        xp_gained = int(base_xp * xp_bonus)

        # Money reward (smaller than XP)
        money_earned = incident.base_reward * 0.1  # 10% of incident reward

        return xp_gained, money_earned

    def _check_sla_compliance(self, incident: Incident, resolution_time: float) -> bool:
        """Check if resolution meets SLA requirements."""
        return resolution_time <= incident.sla_seconds

    # ===== CLIENT BUSINESS LOGIC =====

    def calculate_client_satisfaction(
        self,
        client: Client,
        sla_trackers: List[SLATracker],
        current_month: int
    ) -> float:
        """
        Calculate client satisfaction based on SLA performance.

        Args:
            client: The client
            sla_trackers: SLA trackers for this client
            current_month: Current game month

        Returns:
            Satisfaction score (0.0 to 1.0)
        """
        # Get current month's SLA trackers
        current_trackers = [
            t for t in sla_trackers
            if t.month == current_month and t.client_id == client.client_id
        ]

        if not current_trackers:
            return client.satisfaction  # No incidents this month, maintain satisfaction

        total_incidents = sum(t.total_incidents for t in current_trackers)
        if total_incidents == 0:
            return client.satisfaction

        # Calculate SLA compliance rate
        sla_met = sum(t.response_sla_met + t.resolution_sla_met for t in current_trackers)
        sla_total = sum(t.total_incidents * 2 for t in current_trackers)  # Response + resolution per incident

        compliance_rate = sla_met / sla_total if sla_total > 0 else 1.0

        # Update satisfaction (gradual change)
        satisfaction_change = (compliance_rate - 0.5) * 0.2  # ±20% max change per month
        new_satisfaction = client.satisfaction + satisfaction_change

        return max(0.0, min(1.0, new_satisfaction))

    def should_renew_contract(self, client: Client) -> bool:
        """
        Determine if a client should renew their contract.

        Args:
            client: The client

        Returns:
            True if contract should be renewed
        """
        # Simple rule: renew if satisfaction > 0.6
        return client.satisfaction > 0.6

    # ===== BUDGET BUSINESS LOGIC =====

    def calculate_monthly_budget(
        self,
        state_manager: StateManager
    ) -> Tuple[float, float, float]:
        """
        Calculate monthly revenue, expenses, and profit.

        Args:
            state_manager: Current state manager

        Returns:
            Tuple of (revenue, expenses, profit)
        """
        # Calculate revenue from active clients
        revenue = 0.0
        for client in state_manager.get_active_clients():
            # Revenue = contract value * satisfaction
            client_revenue = client.monthly_contract_value * client.satisfaction
            revenue += client_revenue

        # Calculate expenses (specialist salaries)
        expenses = 0.0
        for specialist in state_manager.get_all_specialists():
            salary = self.calculate_specialist_salary(specialist)
            expenses += salary

        # Add operational costs
        operational_costs = self.game_config.get("operational_costs", 1000)
        expenses += operational_costs

        profit = revenue - expenses

        return revenue, expenses, profit

    def can_afford_specialist_hiring(
        self,
        specialist: Specialist,
        state_manager: StateManager
    ) -> Tuple[bool, str]:
        """
        Check if company can afford to hire a specialist.

        Args:
            specialist: The specialist to hire
            state_manager: Current state manager

        Returns:
            Tuple of (can_afford, reason_if_not)
        """
        salary = self.calculate_specialist_salary(specialist)
        current_budget = state_manager.get_budget()

        # Check if we have enough reserves for 3 months salary (hiring cost)
        hiring_cost = salary * 3
        if current_budget.total_reserves < hiring_cost:
            return False, f"Insufficient reserves (${current_budget.total_reserves}) for hiring cost (${hiring_cost})"

        # Check if monthly expenses would exceed revenue
        budget_result = self.calculate_monthly_budget(state_manager, current_month=1)
        current_expenses = budget_result.monthly_expenses
        new_monthly_expenses = current_expenses + salary

        revenue = budget_result.monthly_revenue
        if new_monthly_expenses > revenue * 1.2:  # Allow 20% deficit
            return False, f"Hiring would cause excessive deficit (expenses: ${new_monthly_expenses}, revenue: ${revenue})"

        return True, ""

    # ===== LEVELING BUSINESS LOGIC =====

    def check_specialist_level_up(self, specialist: Specialist) -> bool:
        """
        Check if specialist should level up.

        Args:
            specialist: The specialist

        Returns:
            True if specialist leveled up
        """
        xp_required = self._calculate_xp_for_level(specialist.level + 1)

        if specialist.xp >= xp_required:
            specialist.level += 1
            specialist.xp -= xp_required

            # Emit level up event
            self.event_bus.publish("specialist_leveled_up", {
                "specialist_id": specialist.id,
                "new_level": specialist.level
            })

            logger.info(f"Specialist {specialist.name} leveled up to {specialist.level}")
            return True

        return False

    def _calculate_xp_for_level(self, level: int) -> int:
        """Calculate XP required for a given level."""
        base_xp = self.game_config.get("xp_curve", {}).get("base_xp", 100)
        exponent = self.game_config.get("xp_curve", {}).get("exponent", 1.5)

        return int(base_xp * (level ** exponent))

    # ===== VALIDATION METHODS =====

    def validate_game_state(self, state_manager: StateManager) -> List[str]:
        """
        Validate the entire game state for consistency.

        Args:
            state_manager: State manager to validate

        Returns:
            List of validation error messages
        """
        errors = []

        # Check referential integrity
        integrity_errors = state_manager.validate_referential_integrity()
        errors.extend(integrity_errors)

        # Check business rule violations
        business_errors = self._validate_business_rules(state_manager)
        errors.extend(business_errors)

        return errors

    # ===== BUDGET BUSINESS LOGIC =====

    def calculate_monthly_budget(
        self,
        state_manager: StateManager,
        current_month: int
    ) -> Budget:
        """
        Calculate monthly budget including revenue, expenses, and profit.

        Args:
            state_manager: Current state manager
            current_month: Current game month

        Returns:
            Updated budget with calculated values
        """
        budget = state_manager.get_budget()

        # Calculate revenue from active clients
        total_revenue = 0.0
        for client in state_manager.get_all_clients():
            if client.is_active:
                # Apply satisfaction multiplier to contract value
                satisfaction_multiplier = client.satisfaction
                client_revenue = client.monthly_contract_value * satisfaction_multiplier
                total_revenue += client_revenue

        # Calculate expenses from specialists
        total_expenses = 0.0
        specialist_count = len(state_manager.get_all_specialists())
        specialist_salary = budget.specialist_salary_per_month
        total_expenses += specialist_count * specialist_salary

        # Calculate profit
        monthly_profit = total_revenue - total_expenses

        # Update budget
        budget.monthly_revenue = total_revenue
        budget.monthly_expenses = total_expenses
        # monthly_profit is calculated via get_monthly_profit() method
        budget.total_reserves += monthly_profit

        # Store in history
        budget.revenue_history.append(total_revenue)
        budget.expense_history.append(total_expenses)
        budget.profit_history.append(monthly_profit)

        logger.info(f"Monthly budget calculated: revenue=${total_revenue:.2f}, "
                   f"expenses=${total_expenses:.2f}, profit=${monthly_profit:.2f}")

        return budget

    def _validate_business_rules(self, state_manager: StateManager) -> List[str]:
        """Validate business rules across the game state."""
        errors = []

        # Check specialist levels are valid
        for specialist in state_manager.get_all_specialists():
            if specialist.level < 1:
                errors.append(f"Specialist {specialist.name} has invalid level {specialist.level}")

            max_level = self.game_config.get("xp_curve", {}).get("level_cap", 20)
            if specialist.level > max_level:
                errors.append(f"Specialist {specialist.name} exceeds level cap {max_level}")

        # Check client satisfaction is valid
        for client in state_manager.get_all_clients():
            if not (0.0 <= client.satisfaction <= 1.0):
                errors.append(f"Client {client.company_name} has invalid satisfaction {client.satisfaction}")

        # Check budget is valid
        budget = state_manager.get_budget()
        if budget.total_reserves < 0:
            errors.append(f"Budget has negative reserves: ${budget.total_reserves}")

        return errors