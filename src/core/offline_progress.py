"""Offline Progress System for simulating game progress while player is away.

This module calculates what happened during the player's absence, including
incident generation, automation execution, passive income, and more.
"""

from typing import Dict, List, Any, Optional, TYPE_CHECKING
import time
import random

from src.utils.logger import GameLogger

if TYPE_CHECKING:
    from src.models.game_state import GameState


class OfflineProgressSystem:
    """Manages offline progress simulation when player returns to the game.
    
    This system simulates game events that occurred while the player was offline,
    including incident generation, automation, passive income, and specialist activity.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[GameLogger] = None):
        """Initialize the offline progress system.
        
        Args:
            config: Game configuration dictionary
            logger: Optional logger for offline progress events
        """
        self._logger = logger or GameLogger("offline_progress")
        self._config = config.get("game_settings", {})
        
        # Offline progress settings
        self._max_offline_hours = self._config.get("offline_progress_cap_hours", 24)
        self._offline_incident_rate_multiplier = 0.5  # 50% of normal rate
        self._offline_sla_penalty_multiplier = 0.5  # 50% of normal penalty
        
        # Statistics
        self._stats = {
            "last_offline_duration": 0.0,
            "total_offline_time": 0.0,
            "total_offline_sessions": 0
        }

    def calculate_offline_progress(self, game_state: 'GameState', time_elapsed: float) -> Dict[str, Any]:
        """Calculate all offline progress for the elapsed time.
        
        Args:
            game_state: Current game state
            time_elapsed: Time elapsed since last save (in seconds)
            
        Returns:
            Dictionary containing complete offline progress report
        """
        # Cap offline time
        capped_time = min(time_elapsed, self._max_offline_hours * 3600)
        
        if capped_time != time_elapsed:
            self._logger.info(
                f"[OFFLINE] Time capped: {time_elapsed/3600:.1f}h → {capped_time/3600:.1f}h"
            )
        
        self._logger.info(
            f"[OFFLINE] Calculating offline progress for {capped_time/3600:.1f} hours"
        )
        
        # Simulate different aspects
        incident_results = self.simulate_offline_incidents(game_state, capped_time)
        automation_results = self.simulate_offline_automation(game_state, capped_time)
        income_results = self.calculate_offline_income(game_state, capped_time)
        
        # Calculate totals
        total_income = income_results.get("total_income", 0.0)
        total_xp = automation_results.get("total_xp_gained", 0)
        incidents_handled = automation_results.get("incidents_handled", 0)
        incidents_failed = automation_results.get("incidents_failed", 0)
        
        # Apply results to game state
        game_state.current_money += total_income
        if total_income > 0:
            game_state.total_money_earned += total_income
        
        # Update statistics
        self._stats["last_offline_duration"] = time_elapsed
        self._stats["total_offline_time"] += time_elapsed
        self._stats["total_offline_sessions"] += 1
        
        self._logger.info(
            f"[OFFLINE] Progress complete: ${total_income:.2f}, {incidents_handled} incidents handled, "
            f"{incidents_failed} failed, {total_xp} total XP"
        )
        
        return {
            "time_elapsed": time_elapsed,
            "time_simulated": capped_time,
            "was_capped": capped_time != time_elapsed,
            "incidents": incident_results,
            "automation": automation_results,
            "income": income_results,
            "summary": {
                "total_income": total_income,
                "total_xp": total_xp,
                "incidents_handled": incidents_handled,
                "incidents_failed": incidents_failed
            }
        }

    def simulate_offline_incidents(self, game_state: 'GameState', time_elapsed: float) -> List[Dict]:
        """Simulate incident generation during offline period.
        
        Args:
            game_state: Current game state
            time_elapsed: Time elapsed in seconds
            
        Returns:
            List of simulated incident events
        """
        incident_events = []
        
        # Calculate how many incidents would have spawned
        for client in game_state.clients:
            if not client.is_active:
                continue
            
            # Base incident rate: convert from avg_monthly_incidents to per-second rate
            monthly_incidents = client.avg_monthly_incidents if hasattr(client, 'avg_monthly_incidents') else 10
            seconds_per_month = 30 * 24 * 3600  # Average month in seconds
            rate_per_second = monthly_incidents / seconds_per_month
            rate_per_minute = rate_per_second * 60 * self._offline_incident_rate_multiplier
            
            # Calculate expected incidents
            minutes_elapsed = time_elapsed / 60.0
            expected_incidents = rate_per_minute * minutes_elapsed
            
            # Generate incidents (Poisson-like distribution)
            num_incidents = int(expected_incidents)
            if random.random() < (expected_incidents - num_incidents):
                num_incidents += 1
            
            for _ in range(num_incidents):
                incident_events.append({
                    "client_id": client.client_id,
                    "client_name": client.company_name,
                    "specialty": self._select_random_specialty(),
                    "difficulty": self._select_random_difficulty()
                })
        
        self._logger.debug(
            f"[OFFLINE] Simulated {len(incident_events)} incidents"
        )
        
        return incident_events

    def simulate_offline_automation(self, game_state: 'GameState', time_elapsed: float) -> Dict[str, Any]:
        """Simulate automation execution during offline period.
        
        Args:
            game_state: Current game state
            time_elapsed: Time elapsed in seconds
            
        Returns:
            Dictionary containing automation simulation results
        """
        incidents_handled = 0
        incidents_failed = 0
        total_xp_gained = 0
        total_money_gained = 0.0
        total_money_lost = 0.0
        
        # Get simulated incidents
        incident_events = self.simulate_offline_incidents(game_state, time_elapsed)
        
        # Count specialists with automation scripts
        automated_specialists = [
            s for s in game_state.specialists 
            if s.automation_scripts and s.is_available()
        ]
        
        if not automated_specialists:
            # No automation - all incidents fail
            incidents_failed = len(incident_events)
            
            # Apply reduced SLA penalties
            for incident in incident_events:
                penalty = 100 * self._offline_sla_penalty_multiplier
                total_money_lost += penalty
            
            self._logger.warning(
                f"[OFFLINE] No automation available - {incidents_failed} incidents failed"
            )
        else:
            # Simulate automated incident handling
            automation_success_rate = self._calculate_automation_success_rate(automated_specialists)
            
            for incident in incident_events:
                if random.random() < automation_success_rate:
                    # Successfully handled
                    incidents_handled += 1
                    
                    # Award XP (distributed among automated specialists)
                    xp_per_incident = 50
                    xp_per_specialist = xp_per_incident // len(automated_specialists)
                    
                    for specialist in automated_specialists:
                        specialist.gain_xp(xp_per_specialist)
                        total_xp_gained += xp_per_specialist
                    
                    # Award money (reduced for offline)
                    reward = 200 * 0.75  # 75% of normal reward
                    total_money_gained += reward
                else:
                    # Failed to handle
                    incidents_failed += 1
                    
                    # Apply reduced penalty
                    penalty = 100 * self._offline_sla_penalty_multiplier
                    total_money_lost += penalty
        
        net_money = total_money_gained - total_money_lost
        
        self._logger.info(
            f"[OFFLINE] Automation: {incidents_handled} handled, {incidents_failed} failed, "
            f"${net_money:.2f} net, {total_xp_gained} XP"
        )
        
        return {
            "incidents_handled": incidents_handled,
            "incidents_failed": incidents_failed,
            "total_xp_gained": total_xp_gained,
            "money_gained": total_money_gained,
            "money_lost": total_money_lost,
            "net_money": net_money,
            "automation_success_rate": self._calculate_automation_success_rate(automated_specialists) if automated_specialists else 0.0
        }

    def calculate_offline_income(self, game_state: 'GameState', time_elapsed: float) -> Dict[str, Any]:
        """Calculate passive income during offline period.
        
        Args:
            game_state: Current game state
            time_elapsed: Time elapsed in seconds
            
        Returns:
            Dictionary containing income breakdown
        """
        # Use passive income system if available
        if hasattr(game_state, '_passive_income_system') and game_state._passive_income_system:
            passive_result = game_state._passive_income_system.apply_passive_income(
                game_state, time_elapsed
            )
            
            return {
                "retainer_income": passive_result.get("retainer_income", 0.0),
                "investment_return": passive_result.get("investment_return", 0.0),
                "reputation_bonus": passive_result.get("reputation_bonus", 0.0),
                "total_income": passive_result.get("total_income", 0.0)
            }
        else:
            # Fallback calculation
            total_income = 0.0
            
            # Simple retainer calculation
            for client in game_state.clients:
                if client.is_active:
                    hourly_rate = client.monthly_contract_value * 0.001
                    hours = time_elapsed / 3600.0
                    total_income += hourly_rate * hours
            
            return {
                "retainer_income": total_income,
                "investment_return": 0.0,
                "reputation_bonus": 0.0,
                "total_income": total_income
            }

    def _calculate_automation_success_rate(self, specialists: List[Any]) -> float:
        """Calculate overall automation success rate.
        
        Args:
            specialists: List of specialists with automation
            
        Returns:
            Success rate (0.0-1.0)
        """
        if not specialists:
            return 0.0
        
        # Base success rate from average accuracy
        avg_accuracy = sum(s.stats.accuracy for s in specialists) / len(specialists)
        base_rate = avg_accuracy / 100.0
        
        # Bonus for having multiple specialists
        multi_specialist_bonus = min(0.1 * (len(specialists) - 1), 0.3)
        
        return min(base_rate + multi_specialist_bonus, 0.95)

    def _select_random_specialty(self) -> str:
        """Select a random specialty for simulated incident.
        
        Returns:
            Specialty name
        """
        specialties = [
            "Network Security",
            "Malware Analysis",
            "Digital Forensics",
            "Application Security",
            "Cloud Security",
            "Incident Response"
        ]
        return random.choice(specialties)

    def _select_random_difficulty(self) -> int:
        """Select a random difficulty for simulated incident.
        
        Returns:
            Difficulty (1-5)
        """
        # Weighted towards easier incidents for offline
        weights = [0.4, 0.3, 0.2, 0.08, 0.02]
        return random.choices([1, 2, 3, 4, 5], weights=weights)[0]

    def get_statistics(self) -> Dict[str, Any]:
        """Get offline progress statistics.
        
        Returns:
            Dictionary containing statistics
        """
        return self._stats.copy()

    def reset_statistics(self) -> None:
        """Reset offline progress statistics."""
        self._stats = {
            "last_offline_duration": 0.0,
            "total_offline_time": 0.0,
            "total_offline_sessions": 0
        }
