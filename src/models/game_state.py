"""GameState model representing the complete state of the cybersecurity firm game.

The GameState is the central hub that manages all game entities, tracks game progression,
handles time-based mechanics, and provides the inte                    self._logger.logger.info(f"[GAME_STATE] Incident {incident.id} generated for client {incident.client_id}")for all game operations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import time
import random

from src.models.specialist import Specialist
from src.models.incident import Incident
from src.models.client import Client
from src.models.automation_script import AutomationScript
from src.core.incident_generator import IncidentGenerator
from src.core.automation_processor import AutomationProcessor
from src.core.passive_income_system import PassiveIncomeSystem
from src.core.burnout_system import BurnoutSystem
from src.core.relationships_system import RelationshipsSystem
from src.utils.json_loader import JSONLoader
from src.utils.logger import GameLogger


@dataclass
class GameMetrics:
    """Real-time game performance metrics."""
    total_incidents_handled: int = 0
    total_incidents_failed: int = 0
    total_profit: float = 0.0
    total_xp_awarded: int = 0
    average_resolution_time: float = 0.0
    sla_compliance_rate: float = 100.0
    automation_scripts_triggered: int = 0
    specialist_utilization_rate: float = 0.0
    
    # Assignment analytics
    total_assignments_attempted: int = 0
    total_assignments_successful: int = 0
    specialty_match_assignments: int = 0
    specialty_mismatch_assignments: int = 0
    assignment_success_rate: float = 0.0

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary."""
        return {
            "total_incidents_handled": self.total_incidents_handled,
            "total_incidents_failed": self.total_incidents_failed,
            "total_profit": self.total_profit,
            "total_xp_awarded": self.total_xp_awarded,
            "average_resolution_time": self.average_resolution_time,
            "sla_compliance_rate": self.sla_compliance_rate,
            "automation_scripts_triggered": self.automation_scripts_triggered,
            "specialist_utilization_rate": self.specialist_utilization_rate,
            "total_assignments_attempted": self.total_assignments_attempted,
            "total_assignments_successful": self.total_assignments_successful,
            "specialty_match_assignments": self.specialty_match_assignments,
            "specialty_mismatch_assignments": self.specialty_mismatch_assignments,
            "assignment_success_rate": self.assignment_success_rate
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'GameMetrics':
        """Create GameMetrics from dictionary."""
        return cls(
            total_incidents_handled=data.get("total_incidents_handled", 0),
            total_incidents_failed=data.get("total_incidents_failed", 0),
            total_profit=data.get("total_profit", 0.0),
            total_xp_awarded=data.get("total_xp_awarded", 0),
            average_resolution_time=data.get("average_resolution_time", 0.0),
            sla_compliance_rate=data.get("sla_compliance_rate", 100.0),
            automation_scripts_triggered=data.get("automation_scripts_triggered", 0),
            specialist_utilization_rate=data.get("specialist_utilization_rate", 0.0),
            total_assignments_attempted=data.get("total_assignments_attempted", 0),
            total_assignments_successful=data.get("total_assignments_successful", 0),
            specialty_match_assignments=data.get("specialty_match_assignments", 0),
            specialty_mismatch_assignments=data.get("specialty_mismatch_assignments", 0),
            assignment_success_rate=data.get("assignment_success_rate", 0.0)
        )


@dataclass
class GameState:
    """Central game state manager for the cybersecurity firm simulation."""

    # Core game entities
    specialists: List[Specialist] = field(default_factory=list)
    incidents: List[Incident] = field(default_factory=list)
    clients: List[Client] = field(default_factory=list)
    automation_scripts: List[AutomationScript] = field(default_factory=list)
    equipment_instances: Dict[str, Any] = field(default_factory=dict)  # equipment_id -> Equipment instance
    
    # Tycoon system entities
    contracts: List = field(default_factory=list)  # List[Contract]
    recruitment_pool: List[Dict] = field(default_factory=list)  # Candidate data
    recruitment_refresh_time: float = 0.0

    # Game progression
    game_start_time: float = field(default_factory=time.time)
    current_time: float = field(default_factory=time.time)
    game_speed_multiplier: float = 1.0
    is_paused: bool = False

    # Financial state
    current_money: float = 5000.0  # Starting money
    total_money_earned: float = 0.0
    investments: Dict[str, float] = field(default_factory=dict)  # Investment type → amount
    
    # Offline progress
    last_save_time: float = field(default_factory=time.time)  # Last time game was saved
    
    # Prestige/Rebirth system
    prestige_points: int = 0  # Prestige points available to spend
    prestige_upgrades: Dict[str, int] = field(default_factory=dict)  # Upgrade ID → level
    total_prestiges: int = 0  # Total number of prestiges performed
    
    # Achievement system
    unlocked_achievements: List[str] = field(default_factory=list)  # Achievement IDs
    achievement_progress: Dict[str, float] = field(default_factory=dict)  # Achievement ID → progress value

    # Dopamine/addictive mechanics
    dopamine_feedback_queue: List[Dict] = field(default_factory=list)  # Visual feedback queue
    active_risk_contracts: Dict[str, Any] = field(default_factory=dict)  # incident_id -> contract

    # Game configuration
    max_active_incidents: int = 50
    max_specialists: int = 10  # Affected by office space facility
    incident_generation_enabled: bool = True

    # Metrics and statistics
    metrics: GameMetrics = field(default_factory=GameMetrics)

    # Internal state
    _json_loader: Optional[JSONLoader] = None
    _logger: Optional[GameLogger] = None
    _incident_generator: Optional[IncidentGenerator] = None
    _automation_processor: Optional[AutomationProcessor] = None
    _passive_income_system: Optional[PassiveIncomeSystem] = None
    _burnout_system: Optional[BurnoutSystem] = None  # Specialist burnout tracking
    _relationships_system: Optional[RelationshipsSystem] = None  # Specialist relationships
    _dopamine_system: Optional[Any] = None  # DopamineSystem - lazy imported
    _idle_core: Optional[Any] = None  # IdleCore - TRUE idle game mechanics
    _equipment_system: Optional[Any] = None  # EquipmentSystem - equipment management
    _last_incident_generation: float = field(default_factory=time.time)
    _incident_generation_accumulator: float = 0.0

    def __post_init__(self):
        """Initialize game state after creation."""
        if self._json_loader is None:
            # Find project root by looking for data directory
            import os
            current_dir = os.getcwd()
            # If we're in src/, go up one level
            if os.path.basename(current_dir) == 'src':
                project_root = os.path.dirname(current_dir)
            else:
                project_root = current_dir
            data_dir = os.path.join(project_root, "data")
            self._json_loader = JSONLoader(data_dir=data_dir)
        if self._logger is None:
            self._logger = GameLogger("game_state")
        
        # Initialize dopamine system for addictive gameplay
        if self._dopamine_system is None:
            from src.core.dopamine_system import DopamineSystem
            self._dopamine_system = DopamineSystem()
        
        # Initialize burnout system for specialist management
        if self._burnout_system is None:
            self._burnout_system = BurnoutSystem()
        
        # Initialize relationships system for team synergy
        if self._relationships_system is None:
            config = self._json_loader.load_data("game_config.json") if self._json_loader else {}
            self._relationships_system = RelationshipsSystem(config)
        
        # Initialize idle core for TRUE idle game mechanics
        if self._idle_core is None:
            from src.core.idle_core import IdleCore
            self._idle_core = IdleCore()
        
        # Initialize equipment system for specialist gear
        if self._equipment_system is None:
            from src.core.equipment_system import EquipmentSystem
            equipment_config = self._json_loader.load_data("equipment.json") if self._json_loader else {}
            self._equipment_system = EquipmentSystem(equipment_config)
        
        if self._incident_generator is None:
            self._incident_generator = IncidentGenerator(self._logger)
        if self._automation_processor is None:
            self._automation_processor = AutomationProcessor(self._logger)
        if self._passive_income_system is None:
            # Load game config for passive income settings
            try:
                game_config = self._json_loader.load_data("game_config.json")
                self._passive_income_system = PassiveIncomeSystem(game_config, self._logger)
            except Exception as e:
                self._logger.logger.warning(f"[GAME_STATE] Could not load game config, using default passive income: {e}")
                self._passive_income_system = PassiveIncomeSystem({}, self._logger)

        # Load initial data if not provided
        if not self.specialists:
            self._load_initial_data()
            # Generate initial incidents so player has something to do immediately
            self._generate_initial_incidents()

    def _generate_initial_incidents(self):
        """Generate starting incidents so player has something to interact with immediately.
        
        This creates 3-5 initial incidents of varying difficulty to give the player
        an immediate gameplay experience instead of waiting for random generation.
        """
        if not self.clients or not self._incident_generator:
            return
        
        initial_incident_count = random.randint(3, 5)
        self._logger.logger.info(f"[GAME_STATE] Generating {initial_incident_count} initial incidents for new game")
        
        for _ in range(initial_incident_count):
            # Pick a random client
            client = random.choice(self.clients)
            try:
                incident = self._incident_generator.generate_incident(client)
                if incident:
                    self.incidents.append(incident)
                    self._logger.logger.info(f"[GAME_STATE] Generated initial incident: {incident.incident_type} (difficulty {incident.difficulty})")
            except Exception as e:
                self._logger.logger.warning(f"[GAME_STATE] Failed to generate initial incident: {e}")
    
    def _load_initial_data(self):
        """Load initial game data from JSON files."""
        try:
            # Load specialists
            specialists_data = self._json_loader.load_data("specialists.json")
            if "specialists" in specialists_data:
                self.specialists = [Specialist.from_dict(s) for s in specialists_data["specialists"]]
                
                # IDLE GAME: Generate synergies for all specialists (strategic depth)
                if self._idle_core:
                    self._logger.logger.info(f"[GAME_STATE] Generating synergies for {len(self.specialists)} specialists")
                    for specialist in self.specialists:
                        if not hasattr(specialist, 'synergies') or not specialist.synergies:
                            specialist.synergies = self._idle_core.generate_specialist_synergies(specialist)
                            self._logger.logger.info(f"[GAME_STATE] Generated {len(specialist.synergies)} synergies for {specialist.name}")

            # Load clients
            clients_data = self._json_loader.load_data("clients.json")
            if "clients" in clients_data:
                self.clients = [Client.from_dict(c) for c in clients_data["clients"]]

            # Load automation scripts
            automation_data = self._json_loader.load_data("automation_scripts.json")
            if "automation_scripts" in automation_data:
                self.automation_scripts = [AutomationScript.from_dict(a) for a in automation_data["automation_scripts"]]

            self._logger.logger.info(f"[GAME_STATE] Initial data loaded: specialists={len(self.specialists)}, clients={len(self.clients)}, automation_scripts={len(self.automation_scripts)}")

        except Exception as e:
            self._logger.logger.error(f"[GAME_STATE] Failed to load initial data: {str(e)}")
            raise



    def update(self, delta_time: float):
        """Update game state by the given time delta.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if self.is_paused:
            return

        # Apply game speed multiplier
        effective_delta = delta_time * self.game_speed_multiplier
        self.current_time += effective_delta

        # Update all incidents
        self._update_incidents(effective_delta)

        # Generate new incidents
        self._generate_incidents(effective_delta)
        
        # AUTO-ASSIGN INCIDENTS (TRUE IDLE GAME MECHANIC)
        # This makes the game play itself - the core of idle games
        if self._idle_core and self._idle_core.config.enabled:
            auto_assignments = self._idle_core.auto_assign_incidents(self)
            for assignment in auto_assignments:
                self._logger.logger.debug(
                    f"[IDLE] Auto-assigned {assignment['incident_id']} to {assignment['specialist_id']}"
                    f" (synergy: {assignment['synergy_active']}, quality: {assignment['match_quality']})"
                )

        # Process automation scripts (pass full GameState)
        automation_results = self._automation_processor.process_automation(self, effective_delta)

        # Update metrics with automation results (number of executed results)
        try:
            executed_count = len(automation_results)
        except Exception:
            executed_count = 0

        self.metrics.automation_scripts_triggered += executed_count
        
        # Apply passive income
        if self._passive_income_system:
            passive_income_result = self._passive_income_system.apply_passive_income(self, effective_delta)

        # Update specialist ability cooldowns
        self._update_ability_cooldowns(effective_delta)
        
        # Update dopamine system (combo timers, etc.)
        self._dopamine_system.update(effective_delta)
        
        # Check for achievements periodically (every 10 seconds)
        if not hasattr(self, '_last_achievement_check'):
            self._last_achievement_check = 0.0
        self._last_achievement_check += effective_delta
        if self._last_achievement_check >= 10.0:
            self._check_achievements()
            self._last_achievement_check = 0.0

        # Update metrics
        self._update_metrics()

    def _update_incidents(self, delta_time: float):
        """Update all active incidents.

        Args:
            delta_time: Time elapsed in seconds
        """
        incidents_to_remove = []

        for incident in self.incidents:
            # Update incident status
            if incident.status == "assigned":
                # Check if assigned specialist is still working on it
                specialist = self.get_specialist_by_id(incident.assigned_specialist_id)
                if specialist and specialist.is_available():
                    # Specialist completed the incident
                    self._resolve_incident(incident, specialist)
                    incidents_to_remove.append(incident)
                elif specialist and not specialist.is_available():
                    # Specialist is still busy
                    pass  # Continue waiting
                else:
                    # Specialist no longer exists or available
                    incident.status = "pending"
                    incident.assigned_specialist_id = None
                    incident.assignment_time = None

            elif incident.status == "pending":
                # Check SLA deadline
                if self.current_time > incident.sla_deadline:
                    self._fail_incident(incident)
                    incidents_to_remove.append(incident)

        # Remove resolved/failed incidents
        for incident in incidents_to_remove:
            self.incidents.remove(incident)

    def _generate_incidents(self, delta_time: float):
        """Generate new incidents based on client rates.

        Args:
            delta_time: Time elapsed in seconds
        """
        if not self.incident_generation_enabled:
            return

        # Generate incidents for each client
        for client in self.clients:
            if self._incident_generator.should_generate_incident(client, delta_time, len(self.incidents)):
                incident = self._incident_generator.generate_incident(client)
                if incident:
                    self.incidents.append(incident)
                    
                    # DOPAMINE INJECTION: Offer risk/reward contracts randomly
                    # Check if incident has difficulty attribute and is a proper Incident object
                    if hasattr(incident, 'difficulty') and isinstance(incident.difficulty, int):
                        risk_contract = self._dopamine_system.offer_risk_contract(incident, incident.difficulty)
                        if risk_contract:
                            self.active_risk_contracts[incident.id] = risk_contract
                            # Visual marker will be added by UI
                            self.dopamine_feedback_queue.append({
                                "type": "risk_contract_offer",
                                "timestamp": time.time(),
                                "incident_id": incident.id,
                                "contract": risk_contract
                            })
                    
                    self._logger.logger.info(f"[GAME_STATE] Incident {incident.id} generated for client {client.id}")

    def _resolve_incident(self, incident: Incident, specialist: Specialist):
        """Resolve a successfully completed incident.

        Args:
            incident: The resolved incident
            specialist: The specialist who resolved it
        """
        # Mark incident as resolved
        incident.status = "resolved"
        incident.completion_time = self.current_time

        # Calculate resolution time
        resolution_time = self.current_time - (incident.assignment_time or incident.spawn_time)

        # Calculate success probability
        success_prob = specialist.calculate_success_probability(incident.difficulty, self._equipment_system)
        success = random.random() < success_prob

        if success:
            # Successful resolution
            base_reward = incident.base_reward
            base_xp = incident.xp_reward

            # Apply SLA bonus/penalty
            sla_met = self.current_time <= incident.sla_deadline
            
            # IDLE CORE: Check for synergy bonuses (strategic depth)
            synergy_bonuses = None
            if self._idle_core:
                synergy_bonuses = self._idle_core.apply_synergy_bonuses(specialist, incident, self)
            
            # Apply synergy multipliers if present
            if synergy_bonuses:
                base_xp = int(base_xp * synergy_bonuses["xp_multiplier"])
                base_reward = int(base_reward * synergy_bonuses["reward_multiplier"])
                # Speed multiplier affects completion time (already handled in simulation)
                self._logger.logger.info(
                    f"[IDLE] Synergy bonus applied! {synergy_bonuses['synergy_name']}: "
                    f"{synergy_bonuses['xp_multiplier']}x XP, {synergy_bonuses['reward_multiplier']}x Reward"
                )
            
            # DOPAMINE INJECTION: Get feedback and apply combo multipliers
            dopamine_feedback = self._dopamine_system.register_incident_completion(
                incident, specialist, success=True, is_sla_met=sla_met
            )
            
            # Use dopamine system rewards (includes combo multipliers)
            reward = dopamine_feedback["final_reward"]
            xp_gain = dopamine_feedback["final_xp"]
            
            # Apply SLA bonus/penalty to base
            if sla_met:
                reward = int(reward * 1.2)  # 20% bonus for SLA compliance
            else:
                reward = int(reward * 0.5)  # 50% penalty for SLA violation
                
            # Check for risk contract completion
            if hasattr(incident, 'risk_contract'):
                risk_reward = self._dopamine_system.calculate_risk_reward(incident, success, sla_met)
                reward = risk_reward  # Override with risk reward
                dopamine_feedback["risk_contract_completed"] = True
                dopamine_feedback["risk_reward"] = risk_reward

            # Award rewards
            self.current_money += reward
            self.total_money_earned += reward
            
            # Award XP and check for level up
            leveled_up = specialist.gain_xp(xp_gain, self._equipment_system)
            if leveled_up:
                self._process_specialist_level_up(specialist)
                dopamine_feedback["level_up"] = True

            # Update client reputation
            client = self.get_client_by_id(incident.client_id)
            if client:
                if sla_met:
                    client.adjust_reputation(2)  # Small reputation boost
                else:
                    client.adjust_reputation(-5)  # Reputation penalty

            self.metrics.total_incidents_handled += 1
            self.metrics.total_xp_awarded += xp_gain
            
            # Add dopamine feedback to queue for visual display
            self.dopamine_feedback_queue.append({
                "type": "completion",
                "timestamp": time.time(),
                "feedback": dopamine_feedback,
                "incident_id": incident.id,
                "specialist_id": specialist.id
            })

            self._logger.logger.info(f"[GAME_STATE] Incident {incident.id} resolved by {specialist.id}: reward=${reward}, XP={xp_gain}, SLA={'met' if sla_met else 'missed'}, combo={dopamine_feedback.get('combo_count', 0)}")
            
            # Generate equipment drop
            self._generate_equipment_drop(incident, specialist)

        else:
            # Failed resolution - break combo
            self._dopamine_system.combo_state.break_combo()
            self.dopamine_feedback_queue.append({
                "type": "combo_broken",
                "timestamp": time.time(),
                "incident_id": incident.id
            })
            self._fail_incident(incident)

    def _fail_incident(self, incident: Incident):
        """Handle incident failure.

        Args:
            incident: The failed incident
        """
        incident.status = "failed"

        # Apply penalties
        penalty = incident.base_reward * 0.3  # 30% of base reward as penalty
        self.current_money = max(0, self.current_money - penalty)

        # Update client reputation
        client = self.get_client_by_id(incident.client_id)
        if client:
            client.adjust_reputation(-10)  # Significant reputation penalty

        self.metrics.total_incidents_failed += 1

        self._logger.logger.warning(f"[GAME_STATE] Incident {incident.id} failed: penalty=${penalty}")

    def _generate_equipment_drop(self, incident: Incident, specialist: Specialist):
        """Generate equipment drop after successful incident resolution.

        Args:
            incident: The resolved incident
            specialist: The specialist who resolved it
        """
        try:
            if not self._equipment_system:
                return

            # Generate equipment drop based on incident difficulty
            equipment = self._equipment_system.generate_equipment_drop(
                incident.difficulty,
                rarity_boost=0.0  # Could add prestige/specialist level bonuses here
            )

            if equipment:
                # Add to specialist's inventory
                success = self._equipment_system.add_to_inventory(specialist, equipment)
                if success:
                    # Add to game state equipment instances
                    self.equipment_instances[equipment.id] = equipment

                    # Add visual feedback for equipment drop
                    self.dopamine_feedback_queue.append({
                        "type": "equipment_drop",
                        "timestamp": time.time(),
                        "equipment": equipment,
                        "specialist_id": specialist.id,
                        "rarity": equipment.rarity
                    })

                    self._logger.logger.info(
                        f"[GAME_STATE] Equipment drop: {equipment.name} ({equipment.rarity}) "
                        f"awarded to {specialist.name}"
                    )
        except Exception as e:
            self._logger.logger.warning(f"[GAME_STATE] Failed to generate equipment drop: {e}")

    def _update_metrics(self):
        """Update real-time game metrics."""
        # Calculate specialist utilization
        total_specialists = len(self.specialists)
        busy_specialists = sum(1 for s in self.specialists if not s.is_available())

        if total_specialists > 0:
            self.metrics.specialist_utilization_rate = (busy_specialists / total_specialists) * 100.0

        # Calculate SLA compliance rate
        total_incidents = self.metrics.total_incidents_handled + self.metrics.total_incidents_failed
        if total_incidents > 0:
            self.metrics.sla_compliance_rate = (self.metrics.total_incidents_handled / total_incidents) * 100.0
    
    def _update_ability_cooldowns(self, delta_time: float):
        """Update ability cooldowns for all specialists.
        
        Args:
            delta_time: Time elapsed in seconds
        """
        try:
            from src.core.ability_system import AbilitySystem
            from src.utils.json_loader import JSONLoader
            
            # Load abilities config
            json_loader = JSONLoader()
            abilities_config = json_loader.load_data("abilities.json")
            ability_system = AbilitySystem(abilities_config)
            
            # Update cooldowns for all specialists
            for specialist in self.specialists:
                ability_system.update_cooldowns(specialist, delta_time)
                ability_system.update_active_effects(specialist, delta_time)
        except Exception as e:
            self._logger.logger.warning(f"[GAME_STATE] Failed to update ability cooldowns: {e}")
    
    def _check_achievements(self):
        """Check for newly unlocked achievements."""
        try:
            from src.core.achievement_system import AchievementSystem
            from src.utils.json_loader import JSONLoader
            
            # Load achievements config
            json_loader = JSONLoader()
            achievements_config = json_loader.load_data("achievements.json")
            achievement_system = AchievementSystem(achievements_config)
            
            # Check for newly unlocked achievements
            newly_unlocked = achievement_system.check_achievements(self)
            
            if newly_unlocked:
                for achievement in newly_unlocked:
                    self._logger.logger.info(
                        f"[GAME_STATE] Achievement unlocked: {achievement.name}"
                    )
        except Exception as e:
            self._logger.logger.warning(f"[GAME_STATE] Failed to check achievements: {e}")
    
    def _process_specialist_level_up(self, specialist):
        """Process level-up rewards for a specialist.
        
        Args:
            specialist: The specialist who leveled up
        """
        try:
            from src.core.progression_system import ProgressionSystem
            from src.core.ability_system import AbilitySystem
            from src.utils.json_loader import JSONLoader
            
            # Load game config
            json_loader = JSONLoader()
            game_config = json_loader.load_data("game_config.json")
            progression_system = ProgressionSystem(game_config)
            
            # Process level up
            rewards = progression_system.process_level_up(specialist)
            
            # Load abilities config and unlock new abilities
            abilities_config = json_loader.load_data("abilities.json")
            ability_system = AbilitySystem(abilities_config)
            unlocked_abilities = ability_system.unlock_abilities_for_level(specialist, specialist.level)
            
            if unlocked_abilities:
                rewards["unlocked_abilities"] = unlocked_abilities
            
            self._logger.logger.info(
                f"[GAME_STATE] Specialist {specialist.id} leveled up to {specialist.level}: "
                f"stats={rewards['stat_increases']}, abilities={unlocked_abilities}"
            )
        except Exception as e:
            self._logger.logger.warning(f"[GAME_STATE] Failed to process level up: {e}")
    
    def _generate_equipment_drop(self, incident, specialist):
        """Generate equipment drop from incident resolution.
        
        Args:
            incident: The resolved incident
            specialist: The specialist who resolved it
        """
        try:
            from src.core.equipment_system import EquipmentSystem
            from src.utils.json_loader import JSONLoader
            
            # Load equipment config
            json_loader = JSONLoader()
            equipment_config = json_loader.load_data("equipment.json")
            equipment_system = EquipmentSystem(equipment_config)
            
            # Generate drop
            dropped_equipment = equipment_system.generate_equipment_drop(incident.difficulty)
            
            if dropped_equipment:
                # Add to specialist's inventory
                equipment_system.add_to_inventory(specialist, dropped_equipment)
                self._logger.logger.info(
                    f"[GAME_STATE] Equipment drop: {dropped_equipment.name} "
                    f"({dropped_equipment.rarity}) for {specialist.id}"
                )
        except Exception as e:
            self._logger.logger.warning(f"[GAME_STATE] Failed to generate equipment drop: {e}")

    # Public interface methods

    def assign_incident_to_specialist(self, incident_id: str, specialist_id: str) -> bool:
        """Manually assign an incident to a specialist.

        Args:
            incident_id: ID of the incident to assign
            specialist_id: ID of the specialist to assign to

        Returns:
            True if assignment successful, False otherwise
        """
        incident = self.get_incident_by_id(incident_id)
        specialist = self.get_specialist_by_id(specialist_id)

        if not incident or not specialist:
            return False

        if incident.status != "pending" or not specialist.is_available():
            return False

        # Check specialty compatibility
        specialty_match = specialist.matches_specialty(incident.specialty_required)
        if not specialty_match:
            return False

        # Track assignment analytics
        self.metrics.total_assignments_attempted += 1
        if specialty_match:
            self.metrics.specialty_match_assignments += 1
        else:
            self.metrics.specialty_mismatch_assignments += 1

        # Perform assignment
        success = specialist.assign_to_incident(incident_id)
        if success:
            self.metrics.total_assignments_successful += 1
            # Update success rate
            if self.metrics.total_assignments_attempted > 0:
                self.metrics.assignment_success_rate = (
                    self.metrics.total_assignments_successful / self.metrics.total_assignments_attempted * 100
                )

            incident.status = "assigned"
            incident.assigned_specialist_id = specialist_id
            incident.assignment_time = self.current_time

            # DOPAMINE INJECTION: Register assignment for combo system
            feedback = self._dopamine_system.register_incident_assignment(incident, specialist)
            self.dopamine_feedback_queue.append({
                "type": "assignment",
                "timestamp": time.time(),
                "feedback": feedback,
                "incident_id": incident_id,
                "specialist_id": specialist_id
            })

            self._logger.logger.info(f"[GAME_STATE] Manual assignment: incident {incident_id} to specialist {specialist_id}")

        return success

    def hire_specialist(self, specialist_data: Dict) -> bool:
        """Hire a new specialist.

        Args:
            specialist_data: Specialist configuration data

        Returns:
            True if hiring successful, False otherwise
        """
        hire_cost = 2000  # Base hiring cost

        if self.current_money < hire_cost:
            return False

        try:
            specialist = Specialist.from_dict(specialist_data)
            self.specialists.append(specialist)
            self.current_money -= hire_cost

            self._logger.logger.info(f"[GAME_STATE] Specialist {specialist.id} hired for ${hire_cost}")

            return True
        except Exception as e:
            self._logger.logger.warning(f"[GAME_STATE] Specialist hire failed: {str(e)}")
            return False

    def upgrade_specialist(self, specialist_id: str, upgrade_type: str) -> bool:
        """Upgrade a specialist's abilities.

        Args:
            specialist_id: ID of the specialist to upgrade
            upgrade_type: Type of upgrade (speed, accuracy, experience_bonus)

        Returns:
            True if upgrade successful, False otherwise
        """
        specialist = self.get_specialist_by_id(specialist_id)
        if not specialist:
            return False

        upgrade_cost = 1000 * (specialist.level // 5 + 1)  # Scaling cost

        if self.current_money < upgrade_cost:
            return False

        # Apply upgrade
        if upgrade_type == "speed":
            specialist.stats.speed = min(200.0, specialist.stats.speed + 5.0)
        elif upgrade_type == "accuracy":
            specialist.stats.accuracy = min(100.0, specialist.stats.accuracy + 2.0)
        elif upgrade_type == "experience_bonus":
            specialist.stats.experience_bonus = min(3.0, specialist.stats.experience_bonus + 0.1)
        else:
            return False

        self.current_money -= upgrade_cost

        self._logger.logger.info(f"[GAME_STATE] Specialist {specialist_id} upgraded ({upgrade_type}) for ${upgrade_cost}")

        return True

    # Getter methods

    def get_specialist_by_id(self, specialist_id: str) -> Optional[Specialist]:
        """Get specialist by ID.

        Args:
            specialist_id: The specialist ID to find

        Returns:
            Specialist instance or None if not found
        """
        return next((s for s in self.specialists if s.id == specialist_id), None)

    def get_incident_by_id(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID.

        Args:
            incident_id: The incident ID to find

        Returns:
            Incident instance or None if not found
        """
        return next((i for i in self.incidents if i.id == incident_id), None)

    def get_client_by_id(self, client_id: str) -> Optional[Client]:
        """Get client by ID.

        Args:
            client_id: The client ID to find

        Returns:
            Client instance or None if not found
        """
        return next((c for c in self.clients if c.id == client_id), None)

    def get_automation_script_by_id(self, script_id: str) -> Optional[AutomationScript]:
        """Get automation script by ID.

        Args:
            script_id: The automation script ID to find

        Returns:
            AutomationScript instance or None if not found
        """
        return next((a for a in self.automation_scripts if a.id == script_id), None)

    def get_available_specialists(self) -> List[Specialist]:
        """Get all available specialists.

        Returns:
            List of available specialists
        """
        return [s for s in self.specialists if s.is_available()]

    def get_pending_incidents(self) -> List[Incident]:
        """Get all pending incidents.

        Returns:
            List of pending incidents
        """
        return [i for i in self.incidents if i.status == "pending"]

    def get_game_time_elapsed(self) -> float:
        """Get total game time elapsed in seconds.

        Returns:
            Time elapsed since game start
        """
        return self.current_time - self.game_start_time

    def get_game_summary(self) -> Dict[str, Any]:
        """Get comprehensive game state summary.

        Returns:
            Dictionary containing game summary data
        """
        summary = {
            "game_time": self.get_game_time_elapsed(),
            "current_money": self.current_money,
            "total_money_earned": self.total_money_earned,
            "specialists_count": len(self.specialists),
            "active_incidents_count": len(self.incidents),
            "pending_incidents_count": len(self.get_pending_incidents()),
            "available_specialists_count": len(self.get_available_specialists()),
            "metrics": self.metrics.to_dict(),
            "is_paused": self.is_paused,
            "game_speed": self.game_speed_multiplier
        }
        
        return summary

    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for serialization.

        Returns:
            Dictionary representation of the game state
        """
        return {
            "specialists": [s.to_dict() for s in self.specialists],
            "incidents": [i.to_dict() for i in self.incidents],
            "clients": [c.to_dict() for c in self.clients],
            "contracts": [c.to_dict() for c in self.contracts] if hasattr(self, 'contracts') else [],
            "recruitment_pool": self.recruitment_pool if hasattr(self, 'recruitment_pool') else [],
            "recruitment_refresh_time": self.recruitment_refresh_time if hasattr(self, 'recruitment_refresh_time') else 0.0,
            "game_start_time": self.game_start_time,
            "current_time": self.current_time,
            "game_speed_multiplier": self.game_speed_multiplier,
            "is_paused": self.is_paused,
            "current_money": self.current_money,
            "total_money_earned": self.total_money_earned,
            "investments": self.investments.copy(),
            "last_save_time": self.last_save_time,
            "prestige_points": self.prestige_points,
            "prestige_upgrades": self.prestige_upgrades.copy(),
            "total_prestiges": self.total_prestiges,
            "unlocked_achievements": self.unlocked_achievements.copy(),
            "achievement_progress": self.achievement_progress.copy(),
            "max_active_incidents": self.max_active_incidents,
            "max_specialists": self.max_specialists if hasattr(self, 'max_specialists') else 10,
            "incident_generation_enabled": self.incident_generation_enabled,
            "metrics": self.metrics.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Create GameState from dictionary.

        Args:
            data: Dictionary containing game state data

        Returns:
            New GameState instance
        """
        # Create instance without calling __post_init__
        instance = cls.__new__(cls)

        # Load entities
        instance.specialists = [Specialist.from_dict(s) for s in data.get("specialists", [])]
        instance.incidents = [Incident.from_dict(i) for i in data.get("incidents", [])]
        instance.clients = [Client.from_dict(c) for c in data.get("clients", [])]
        
        # Load tycoon system entities (imported inline to avoid circular dependencies)
        instance.contracts = []
        if "contracts" in data:
            try:
                from src.models.contract import Contract
                instance.contracts = [Contract.from_dict(c) for c in data["contracts"]]
            except ImportError:
                pass
        
        instance.recruitment_pool = data.get("recruitment_pool", []).copy()
        instance.recruitment_refresh_time = data.get("recruitment_refresh_time", 0.0)

        # Load game state
        instance.game_start_time = data.get("game_start_time", time.time())
        instance.current_time = data.get("current_time", time.time())
        instance.game_speed_multiplier = data.get("game_speed_multiplier", 1.0)
        instance.is_paused = data.get("is_paused", False)
        instance.current_money = data.get("current_money", 5000.0)
        instance.total_money_earned = data.get("total_money_earned", 0.0)
        instance.investments = data.get("investments", {}).copy()
        instance.last_save_time = data.get("last_save_time", time.time())
        instance.prestige_points = data.get("prestige_points", 0)
        instance.prestige_upgrades = data.get("prestige_upgrades", {}).copy()
        instance.total_prestiges = data.get("total_prestiges", 0)
        instance.unlocked_achievements = data.get("unlocked_achievements", []).copy()
        instance.achievement_progress = data.get("achievement_progress", {}).copy()
        instance.dopamine_feedback_queue = data.get("dopamine_feedback_queue", []).copy()
        instance.active_risk_contracts = data.get("active_risk_contracts", {}).copy()
        instance.max_active_incidents = data.get("max_active_incidents", 50)
        instance.max_specialists = data.get("max_specialists", 10)
        instance.incident_generation_enabled = data.get("incident_generation_enabled", True)
        instance.metrics = GameMetrics.from_dict(data.get("metrics", {}))

        # Initialize internal state
        instance._json_loader = JSONLoader()
        instance._logger = GameLogger("game_state")
        instance._incident_generator = IncidentGenerator(instance._logger)
        instance._automation_processor = AutomationProcessor(instance._logger)
        instance._last_incident_generation = time.time()
        instance._incident_generation_accumulator = 0.0
        
        # Initialize passive income system
        try:
            game_config = instance._json_loader.load_data("game_config.json")
            instance._passive_income_system = PassiveIncomeSystem(game_config, instance._logger)
        except Exception:
            instance._passive_income_system = PassiveIncomeSystem({}, instance._logger)

        # Load automation scripts
        try:
            automation_data = instance._json_loader.load_data("automation_scripts.json")
            if "automation_scripts" in automation_data:
                instance.automation_scripts = [AutomationScript.from_dict(a) for a in automation_data["automation_scripts"]]
        except Exception:
            instance.automation_scripts = []
        
        # Initialize systems that are normally created in __post_init__
        # These MUST be initialized for loaded games to work properly
        from src.core.dopamine_system import DopamineSystem
        from src.core.idle_core import IdleCore
        from src.core.equipment_system import EquipmentSystem
        
        instance._dopamine_system = DopamineSystem()
        instance._burnout_system = BurnoutSystem()
        
        try:
            game_config = instance._json_loader.load_data("game_config.json")
            instance._relationships_system = RelationshipsSystem(game_config)
        except Exception:
            instance._relationships_system = RelationshipsSystem({})
        
        instance._idle_core = IdleCore()
        
        try:
            equipment_config = instance._json_loader.load_data("equipment.json")
            instance._equipment_system = EquipmentSystem(equipment_config)
        except Exception:
            instance._equipment_system = EquipmentSystem({})

        return instance
    
    @property
    def incident_generator(self) -> IncidentGenerator:
        """Get the incident generator instance."""
        return self._incident_generator

    def __repr__(self) -> str:
        """String representation of game state."""
        return (f"GameState(specialists={len(self.specialists)}, "
                f"incidents={len(self.incidents)}, clients={len(self.clients)}, "
                f"money=${self.current_money:.0f}, time={self.get_game_time_elapsed():.0f}s)")