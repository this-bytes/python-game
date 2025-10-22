"""GameState model representing the complete state of the cybersecurity firm game.

The GameState is the central hub that manages all game entities, tracks game progression,
handles time-based mechanics, and provides the interface for all game operations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import time
import random

# Core Model Imports
from src.models.specialist import Specialist, SpecialistStats
from src.models.incident import Incident
from src.models.client import Client
from src.models.automation_script import AutomationScript
from src.models.budget import Budget
from src.models.sla_tracker import SLATracker
# Core System Imports (Types used as Optional or for instantiation)
from src.core.dopamine_system import DopamineSystem
from src.core.equipment_system import EquipmentSystem
from src.core.incident_generator import IncidentGenerator
from src.core.automation_processor import AutomationProcessor
from src.core.passive_income_system import PassiveIncomeSystem
from src.core.relationships_system import RelationshipsSystem
from src.utils.json_loader import JSONLoader
from src.utils.logger import GameLogger
from src.core.event_bus import get_event_bus

IdleCore = 'src.core.idle_core.IdleCore'


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
    facilities: List = field(default_factory=list)  # List[Facility]
    recruitment_pool: List[Dict] = field(default_factory=list)  # Candidate data
    recruitment_refresh_time: float = 0.0
    active_events: List[Dict] = field(default_factory=list)  # {event_id, remaining_time}
    event_cooldowns: Dict[str, float] = field(default_factory=dict)  # event_id -> next_allowed_time

    # Game progression
    game_start_time: float = field(default_factory=time.time)
    current_time: float = field(default_factory=time.time)
    game_speed_multiplier: float = 1.0
    is_paused: bool = False
    is_tutorial: bool = False

    # Financial state
    current_money: float = 5000.0  # Starting money
    total_money_earned: float = 0.0
    investments: Dict[str, float] = field(default_factory=dict)  # Investment type → amount
    budget: Budget = field(default_factory=lambda: Budget(total_reserves=10000.0))
    
    # SOC Startup tracking
    sla_trackers: List[SLATracker] = field(default_factory=list)
    company_founded_month: int = 0
    current_month: int = 1
    
    # Offline progress
    last_save_time: float = field(default_factory=time.time)  # Last time game was saved
    
    # Prestige/Rebirth system
    prestige_points: int = 0
    prestige_upgrades: Dict[str, int] = field(default_factory=dict)
    total_prestiges: int = 0
    
    # Achievement system
    unlocked_achievements: List[str] = field(default_factory=list)
    achievement_progress: Dict[str, float] = field(default_factory=dict)

    # Dopamine/addictive mechanics
    dopamine_feedback_queue: List[Dict] = field(default_factory=list)
    active_risk_contracts: Dict[str, Any] = field(default_factory=dict)

    # Game configuration
    max_active_incidents: int = 50
    max_specialists: int = 10
    incident_generation_enabled: bool = True

    # Metrics and statistics
    metrics: GameMetrics = field(default_factory=GameMetrics)

    # Internal state (systems) - Using string literals for type hints
    _json_loader: Optional[JSONLoader] = None
    _logger: Optional[GameLogger] = None
    _incident_generator: Optional[IncidentGenerator] = None
    _automation_processor: Optional[AutomationProcessor] = None
    _passive_income_system: Optional[PassiveIncomeSystem] = None
    # _offline_progress_system: Optional[OfflineProgressSystem] = None
    # _burnout_system: Optional['BurnoutSystem'] = None
    _relationships_system: Optional['RelationshipsSystem'] = None
    _dopamine_system: Optional[DopamineSystem] = None
    _idle_core: Optional[IdleCore] = None
    _equipment_system: Optional[EquipmentSystem] = None
    _last_incident_generation: float = field(default_factory=time.time)
    _incident_generation_accumulator: float = 0.0
    _offline_progress_calculated: bool = False
    _last_offline_report: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize game state after creation."""
        # 1. Initialize Essential Systems (Loader/Logger)
        if self._json_loader is None:
            import os
            current_dir = os.getcwd()
            if os.path.basename(current_dir) == 'src':
                project_root = os.path.dirname(current_dir)
            else:
                project_root = current_dir
            data_dir = os.path.join(project_root, "data")
            self._json_loader = JSONLoader(data_dir=data_dir)
            
        if self._logger is None:
            self._logger = GameLogger("game_state")

        # 2. Initialize Core Systems (using a helper)
        self._initialize_core_systems()

        # 3. Load Initial Data (Only for new games)
        if not self.specialists:
            self._load_initial_data()
            self._generate_initial_incidents()
        
        # 4. Check for offline progress on initialization
        self._check_offline_progress()

        # 5. Set up event bus subscriptions
        self._setup_event_subscriptions()

    def _initialize_core_systems(self):
        """Initializes all external system dependencies."""
        if self._json_loader is None:
             # This should only happen if __post_init__ was skipped entirely
             return
             
        game_config = {}
        try:
            game_config = self._json_loader.load_data("game_config.json")
            equipment_config = self._json_loader.load_data("equipment.json")
        except Exception as e:
            if self._logger:
                self._logger.warning(f"[GAME_STATE] Failed to load config files for system initialization: {e}")
        
        # Initialize core systems using lazy imports for systems
        from src.core.dopamine_system import DopamineSystem
        from src.core.idle_core import IdleCore
        from src.core.equipment_system import EquipmentSystem
        # from src.core.burnout_system import BurnoutSystem
        from src.core.relationships_system import RelationshipsSystem
        
        if self._dopamine_system is None:
            self._dopamine_system = DopamineSystem()
        # if self._burnout_system is None:
        #     self._burnout_system = BurnoutSystem()
        if self._relationships_system is None:
            self._relationships_system = RelationshipsSystem(game_config)
        if self._idle_core is None:
            self._idle_core = IdleCore()
        if self._equipment_system is None:
            self._equipment_system = EquipmentSystem(equipment_config)
        
        if self._incident_generator is None:
            self._incident_generator = IncidentGenerator(self._logger)
        if self._automation_processor is None:
            self._automation_processor = AutomationProcessor(self._logger)
        
        if self._passive_income_system is None:
            self._passive_income_system = PassiveIncomeSystem(game_config, self._logger)
        # if self._offline_progress_system is None:
        #     self._offline_progress_system = OfflineProgressSystem(game_config, self._logger)

        if self._logger:
            self._logger.info("[GAME_STATE] All core systems initialized.")


    def _setup_event_subscriptions(self):
        """Set up event bus subscriptions for game state integration."""
        event_bus = get_event_bus()
        
        event_bus.subscribe("combo_feedback", self._on_combo_feedback)
        event_bus.subscribe("completion_feedback", self._on_completion_feedback)
        event_bus.subscribe("risk_contract_offered", self._on_risk_contract_offered)
        
        if self._logger:
            self._logger.info("[GAME_STATE] Event bus subscriptions established")

    def _on_combo_feedback(self, event):
        """Handle combo feedback event from dopamine plugin."""
        self.dopamine_feedback_queue.append({
            "type": "assignment",
            "feedback": event.data
        })
        if self._logger:
            self._logger.debug(f"[GAME_STATE] Processed combo feedback: {event.data}")

    def _on_completion_feedback(self, event):
        """Handle completion feedback event from dopamine plugin."""
        self.dopamine_feedback_queue.append({
            "type": "completion",
            "feedback": event.data
        })
        if self._logger:
            self._logger.debug(f"[GAME_STATE] Processed completion feedback: {event.data}")

    def _on_risk_contract_offered(self, event):
        """Handle risk contract offered event from dopamine plugin."""
        self.dopamine_feedback_queue.append({
            "type": "risk_contract_offer",
            "contract": event.data
        })
        if self._logger:
            self._logger.debug(f"[GAME_STATE] Processed risk contract offer: {event.data}")

    def _generate_initial_incidents(self):
        """Generate starting incidents so player has something to interact with immediately."""
        if not self.clients or not self._incident_generator:
            return
        
        initial_incident_count = random.randint(3, 5)
        if self._logger:
            self._logger.info(f"[GAME_STATE] Generating {initial_incident_count} initial incidents for new game")
        
        for _ in range(initial_incident_count):
            client = random.choice(self.clients)
            try:
                incident = self._incident_generator.generate_incident(client)
                if incident:
                    self.incidents.append(incident)
                    if self._logger:
                        self._logger.info(f"[GAME_STATE] Generated initial incident: {incident.incident_type} (difficulty {incident.difficulty})")
            except Exception as e:
                if self._logger:
                    self._logger.warning(f"[GAME_STATE] Failed to generate initial incident: {e}")
    
    def _load_initial_data(self):
        """Load initial game data from JSON files."""
        if not self._json_loader:
            if self._logger:
                self._logger.error("[GAME_STATE] Cannot load initial data: JSONLoader is None.")
            return

        try:
            game_config = self._json_loader.load_data("game_config.json")
            starting_specialists = game_config.get("game_settings", {}).get("starting_specialists", 2)
            
            # Load specialists - for new games, create starting specialists
            specialists_data = self._json_loader.load_data("specialists.json")
            if "specialists" in specialists_data and specialists_data["specialists"]:
                self.specialists = [Specialist.from_dict(s) for s in specialists_data["specialists"]]
                if self._logger:
                    self._logger.info(f"[GAME_STATE] Loaded {len(self.specialists)} existing specialists")
            else:
                self._create_starting_specialists(starting_specialists)
            
            # Generate synergies for all specialists
            if self._idle_core and self._logger:
                self._logger.info(f"[GAME_STATE] Generating synergies for {len(self.specialists)} specialists")
                for specialist in self.specialists:
                    if not hasattr(specialist, 'synergies') or not specialist.synergies:
                        specialist.synergies = self._idle_core.generate_specialist_synergies(specialist)
                        self._logger.debug(f"[GAME_STATE] Generated {len(specialist.synergies)} synergies for {specialist.name}")

            # Load clients
            clients_data = self._json_loader.load_data("clients.json")
            if "clients" in clients_data:
                self.clients = [Client.from_dict(c) for c in clients_data["clients"]]

            # Load automation scripts
            automation_data = self._json_loader.load_data("automation_scripts.json")
            if "automation_scripts" in automation_data:
                self.automation_scripts = [AutomationScript.from_dict(a) for a in automation_data["automation_scripts"]]
            
            # Load facilities
            try:
                facilities_data = self._json_loader.load_data("facilities.json")
                if "facilities" in facilities_data:
                    from src.models.facility import Facility # Local import for Facility model
                    self.facilities = [Facility.from_dict(f) for f in facilities_data["facilities"]]
            except Exception as e:
                if self._logger:
                    self._logger.warning(f"[GAME_STATE] Could not load facilities: {e}")
                self.facilities = []

            if self._logger:
                self._logger.info(f"[GAME_STATE] Initial data loaded: specialists={len(self.specialists)}, clients={len(self.clients)}, automation_scripts={len(self.automation_scripts)}, facilities={len(self.facilities)}")

        except Exception as e:
            if self._logger:
                self._logger.error(f"[GAME_STATE] Failed to load initial data: {str(e)}")
            raise

    def _create_starting_specialists(self, count: int):
        """Create starting specialists for new games."""
        if not self._json_loader:
            return

        try:
            templates_data = self._json_loader.load_data("specialist_templates.json")
            templates = templates_data.get("specialist_archetypes", [])
            
            if not templates:
                if self._logger:
                    self._logger.warning("[GAME_STATE] No specialist templates found, creating basic specialists")
                # Fallback: create basic specialists
                for i in range(count):
                    specialist = Specialist(
                        id=f"spec_{i+1:03d}",
                        name=f"Specialist {i+1}",
                        specialty="Network Security",
                        level=1,
                        xp=0,
                        stats=SpecialistStats(speed=100, accuracy=80, experience_bonus=1.0)
                    )
                    self.specialists.append(specialist)
                return
            
            # Create specialists from templates
            created_count = 0
            while created_count < count:
                template = templates[created_count % len(templates)]
                
                specialist = Specialist(
                    id=f"spec_{created_count+1:03d}",
                    name=template["name"] if created_count < len(templates) else f"{template['name']} {created_count // len(templates) + 1}",
                    specialty=template["specialty"],
                    level=1,
                    xp=0,
                    stats=SpecialistStats(
                        speed=template["base_stats"]["speed"],
                        accuracy=template["base_stats"]["accuracy"],
                        experience_bonus=template["base_stats"]["experience_bonus"]
                    )
                )
                
                self.specialists.append(specialist)
                created_count += 1
            
            if self._logger:
                self._logger.info(f"[GAME_STATE] Created {len(self.specialists)} starting specialists")

        except Exception as e:
            if self._logger:
                self._logger.error(f"[GAME_STATE] Failed to create starting specialists: {e}")
            # Fallback: create minimal specialists
            for i in range(count):
                specialist = Specialist(
                    id=f"spec_{i+1:03d}",
                    name=f"Specialist {i+1}",
                    specialty="Network Security",
                    level=1,
                    xp=0,
                    stats=SpecialistStats(speed=100, accuracy=80, experience_bonus=1.0)
                )
                self.specialists.append(specialist)

    def _check_offline_progress(self):
        """Check if player was offline and calculate offline progress."""
        if self._offline_progress_calculated:
            return
        
        current_time = time.time()
        time_elapsed = current_time - self.last_save_time
        
        min_offline_time = 300  # 5 minutes
        
        if time_elapsed > min_offline_time:
            if self._logger:
                self._logger.info(
                    f"[GAME_STATE] Player was offline for {time_elapsed/3600:.1f} hours, calculating progress..."
                )
            
            if self._offline_progress_system:
                offline_report = self._offline_progress_system.calculate_offline_progress(
                    self, time_elapsed
                )
                
                self._last_offline_report = offline_report
                
                if self._logger:
                    self._logger.info(
                        f"[GAME_STATE] Offline progress complete: ${offline_report['summary']['total_income']:.2f} earned"
                    )
            
            self._offline_progress_calculated = True
        
        self.last_save_time = current_time

    def update(self, delta_time: float):
        """Update game state by the given time delta."""
        if self.is_paused:
            return

        effective_delta = delta_time * self.game_speed_multiplier
        self.current_time += effective_delta

        # Update core game mechanics
        self._update_incidents(effective_delta)
        self._generate_incidents(effective_delta)
        self._auto_assign_incidents()
        
        # Process automation
        if self._automation_processor:
            automation_results = self._automation_processor.process_automation(self, effective_delta)
            try:
                executed_count = len(automation_results)
            except Exception:
                executed_count = 0
            self.metrics.automation_scripts_triggered += executed_count
        
        # Update dopamine system (combo timers, etc.)
        if self._dopamine_system:
            self._dopamine_system.update(effective_delta)

        self._update_metrics()

    def _auto_assign_incidents(self):
        """Handles auto-assignment of incidents using the IdleCore."""
        if self._idle_core and self._idle_core.config.enabled:
            auto_assignments = self._idle_core.auto_assign_incidents(self)
            if self._logger:
                for assignment in auto_assignments:
                    self._logger.debug(
                        f"[IDLE] Auto-assigned {assignment['incident_id']} to {assignment['specialist_id']}"
                        f" (synergy: {assignment['synergy_active']}, quality: {assignment['match_quality']})"
                    )

    def _update_incidents(self, delta_time: float):
        """Update all active incidents."""
        incidents_to_remove = []

        for incident in self.incidents:
            if incident.status == "assigned":
                specialist = self.get_specialist_by_id(incident.assigned_specialist_id)
                if specialist and specialist.is_available():
                    # Specialist completed the incident
                    self._resolve_incident(incident, specialist)
                    incidents_to_remove.append(incident)
                elif not specialist:
                    # Specialist no longer exists - unassign incident
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
        """Generate new incidents based on client rates."""
        if not self.incident_generation_enabled or not self._incident_generator or not self._dopamine_system:
            return

        for client in self.clients:
            if self._incident_generator.should_generate_incident(client, delta_time, len(self.incidents)):
                incident = self._incident_generator.generate_incident(client)
                if incident:
                    self.incidents.append(incident)
                    
                    if hasattr(incident, 'difficulty') and isinstance(incident.difficulty, int):
                        risk_contract = self._dopamine_system.offer_risk_contract(incident, incident.difficulty)
                        if risk_contract:
                            self.active_risk_contracts[incident.id] = risk_contract
                            self.dopamine_feedback_queue.append({
                                "type": "risk_contract_offer",
                                "timestamp": time.time(),
                                "incident_id": incident.id,
                                "contract": risk_contract
                            })
                    
                    if self._logger:
                        self._logger.info(f"[GAME_STATE] Incident {incident.id} generated for client {client.client_id}")

    def _resolve_incident(self, incident: Incident, specialist: Specialist):
        """Resolve a successfully completed incident."""
        incident.status = "resolved"
        incident.completion_time = self.current_time

        # Calculate success probability
        # Rely on initialized _equipment_system
        success_prob = specialist.calculate_success_probability(incident.difficulty, self._equipment_system)
        success = random.random() < success_prob

        if success and self._dopamine_system and self._idle_core:
            base_reward = incident.base_reward
            base_xp = incident.xp_reward
            sla_met = self.current_time <= incident.sla_deadline
            
            synergy_bonuses = self._idle_core.apply_synergy_bonuses(specialist, incident, self)
            
            if synergy_bonuses:
                base_xp = int(base_xp * synergy_bonuses["xp_multiplier"])
                base_reward = int(base_reward * synergy_bonuses["reward_multiplier"])
                if self._logger:
                    self._logger.info(
                        f"[IDLE] Synergy bonus applied! {synergy_bonuses['synergy_name']}: "
                        f"{synergy_bonuses['xp_multiplier']}x XP, {synergy_bonuses['reward_multiplier']}x Reward"
                    )
            
            # DOPAMINE INJECTION: Get feedback and apply combo multipliers
            dopamine_feedback = self._dopamine_system.register_incident_completion(
                incident, specialist, success=True, is_sla_met=sla_met
            )
            
            reward = dopamine_feedback["final_reward"]
            xp_gain = dopamine_feedback["final_xp"]
            
            # Apply SLA bonus/penalty
            if sla_met:
                reward = int(reward * 1.2)
            else:
                reward = int(reward * 0.5)
                
            # Check for risk contract completion
            if incident.id in self.active_risk_contracts:
                risk_reward = self._dopamine_system.calculate_risk_reward(incident, success, sla_met)
                reward = risk_reward
                dopamine_feedback["risk_contract_completed"] = True
                dopamine_feedback["risk_reward"] = risk_reward
                del self.active_risk_contracts[incident.id]

            # Award rewards
            self.current_money += reward
            self.total_money_earned += reward
            
            # Award XP and check for level up
            leveled_up = specialist.gain_xp(xp_gain, self._equipment_system)
            if leveled_up:
                self._process_specialist_level_up(specialist)
                dopamine_feedback["level_up"] = True

            # Update client reputation (or satisfaction)
            client = self.get_client_by_id(incident.client_id)
            if client:
                # Assuming Client model has adjust_reputation or adjust_satisfaction
                adjustment = 2 if sla_met else -5
                if hasattr(client, 'adjust_reputation'):
                     client.adjust_reputation(adjustment)
                elif hasattr(client, 'adjust_satisfaction'):
                     client.adjust_satisfaction(adjustment) 

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

            # Publish event for external systems
            event_bus = get_event_bus()
            event_bus.publish("incident_completed", {
                "incident": incident,
                "specialist": specialist,
                "success": success,
                "is_sla_met": sla_met,
                "final_reward": reward,
                "final_xp": xp_gain,
                "combo_count": dopamine_feedback.get("combo_count", 0),
                "multiplier": dopamine_feedback.get("multiplier", 1.0),
                "is_perfect": dopamine_feedback.get("is_perfect", False),
                "reward_tier": dopamine_feedback.get("reward_tier"),
                "message": dopamine_feedback.get("message", ""),
                "combo_broken": dopamine_feedback.get("combo_broken", False)
            })

            if self._logger:
                self._logger.info(f"[GAME_STATE] Incident {incident.id} resolved by {specialist.id}: reward=${reward}, XP={xp_gain}, SLA={'met' if sla_met else 'missed'}, combo={dopamine_feedback.get('combo_count', 0)}")
            
            self._generate_equipment_drop_internal(incident, specialist)

        else:
            # Failed resolution (or lack of required systems)
            if self._dopamine_system:
                self._dopamine_system.combo_state.break_combo()
                self.dopamine_feedback_queue.append({
                    "type": "combo_broken",
                    "timestamp": time.time(),
                    "incident_id": incident.id
                })
            self._fail_incident(incident)

    def _fail_incident(self, incident: Incident):
        """Handle incident failure."""
        incident.status = "failed"

        penalty = incident.base_reward * 0.3
        self.current_money = max(0, self.current_money - penalty)

        client = self.get_client_by_id(incident.client_id)
        if client:
            if hasattr(client, 'adjust_reputation'):
                client.adjust_reputation(-10)
            elif hasattr(client, 'adjust_satisfaction'):
                client.adjust_satisfaction(-10) 

        self.metrics.total_incidents_failed += 1

        if self._logger:
            self._logger.warning(f"[GAME_STATE] Incident {incident.id} failed: penalty=${penalty}")

    def _generate_equipment_drop_internal(self, incident: Incident, specialist: Specialist):
        """Internal handler for equipment drop after successful incident resolution."""
        if not self._equipment_system:
            return

        try:
            equipment = self._equipment_system.generate_equipment_drop(
                incident.difficulty,
                rarity_boost=0.0
            )

            if equipment:
                success = self._equipment_system.add_to_inventory(specialist, equipment)
                if success:
                    self.equipment_instances[equipment.id] = equipment
                    self.dopamine_feedback_queue.append({
                        "type": "equipment_drop",
                        "timestamp": time.time(),
                        "equipment": equipment,
                        "specialist_id": specialist.id,
                        "rarity": equipment.rarity
                    })

                    if self._logger:
                        self._logger.info(
                            f"[GAME_STATE] Equipment drop: {equipment.name} ({equipment.rarity}) "
                            f"awarded to {specialist.name}"
                        )
        except Exception as e:
            if self._logger:
                self._logger.warning(f"[GAME_STATE] Failed to generate equipment drop: {e}")

    def _update_metrics(self):
        """Update real-time game metrics."""
        total_specialists = len(self.specialists)
        busy_specialists = sum(1 for s in self.specialists if not s.is_available())

        if total_specialists > 0:
            self.metrics.specialist_utilization_rate = (busy_specialists / total_specialists) * 100.0

        total_incidents = self.metrics.total_incidents_handled + self.metrics.total_incidents_failed
        if total_incidents > 0:
            self.metrics.sla_compliance_rate = (self.metrics.total_incidents_handled / total_incidents) * 100.0
        
    def _process_specialist_level_up(self, specialist):
        """Process level-up rewards for a specialist."""
        if not self._json_loader or not self._logger:
            return

        try:
            # Lazy import core systems only needed for this flow
            from src.core.progression_system import ProgressionSystem
            from src.core.ability_system import AbilitySystem
            
            # Use self._json_loader which is guaranteed to be initialized here
            game_config = self._json_loader.load_data("game_config.json")
            progression_system = ProgressionSystem(game_config)
            
            rewards = progression_system.process_level_up(specialist)
            
            abilities_config = self._json_loader.load_data("abilities.json")
            ability_system = AbilitySystem(abilities_config)
            unlocked_abilities = ability_system.unlock_abilities_for_level(specialist, specialist.level)
            
            if unlocked_abilities:
                rewards["unlocked_abilities"] = unlocked_abilities
            
            if self._logger:
                self._logger.info(
                    f"[GAME_STATE] Specialist {specialist.id} leveled up to {specialist.level}: "
                    f"stats={rewards['stat_increases']}, abilities={unlocked_abilities}"
                )
        except Exception as e:
            if self._logger:
                self._logger.warning(f"[GAME_STATE] Failed to process level up: {e}")

    # Public interface methods

    def assign_incident_to_specialist(self, incident_id: str, specialist_id: str) -> bool:
        """Manually assign an incident to a specialist."""
        incident = self.get_incident_by_id(incident_id)
        specialist = self.get_specialist_by_id(specialist_id)

        if not incident or not specialist:
            return False

        if incident.status != "pending" or not specialist.is_available():
            return False

        # --- REFACTOR FIX: Track assignment metrics immediately ---
        specialty_match = specialist.matches_specialty(incident.specialty_required)

        self.metrics.total_assignments_attempted += 1
        if specialty_match:
            self.metrics.specialty_match_assignments += 1
        else:
            self.metrics.specialty_mismatch_assignments += 1
            # Assignment fails if specialty doesn't match
            # if self._logger:
            #     self._logger.warning(f"[GAME_STATE] Assignment failed: {specialist_id} specialty mismatch for {incident_id}")
            return False

        # Perform assignment (Only proceeds if specialty_match is True)
        success = specialist.assign_to_incident(incident_id)
        if success:
            self.metrics.total_assignments_successful += 1
            if self.metrics.total_assignments_attempted > 0:
                self.metrics.assignment_success_rate = (
                    self.metrics.total_assignments_successful / self.metrics.total_assignments_attempted * 100
                )

            incident.status = "assigned"
            incident.assigned_specialist_id = specialist_id
            incident.assignment_time = self.current_time

            # Publish event for dopamine plugin
            event_bus = get_event_bus()
            event_bus.publish("incident_assigned", {
                "incident": incident,
                "specialist": specialist,
                "assignment_time": self.current_time
            })
            if self._logger:
                self._logger.debug(f"[GAME_STATE] Published incident_assigned event for {incident_id}")
                self._logger.info(f"[GAME_STATE] Manual assignment: incident {incident_id} to specialist {specialist_id}")

        return success

    def hire_specialist(self, specialist_data: Dict) -> bool:
        """Hire a new specialist."""
        hire_cost = 2000

        if self.current_money < hire_cost:
            return False

        try:
            specialist = Specialist.from_dict(specialist_data)
            self.specialists.append(specialist)
            self.current_money -= hire_cost

            if self._logger:
                self._logger.info(f"[GAME_STATE] Specialist {specialist.id} hired for ${hire_cost}")

            return True
        except Exception as e:
            if self._logger:
                self._logger.warning(f"[GAME_STATE] Specialist hire failed: {str(e)}")
            return False

    def upgrade_specialist(self, specialist_id: str, upgrade_type: str) -> bool:
        """Upgrade a specialist's abilities."""
        specialist = self.get_specialist_by_id(specialist_id)
        if not specialist:
            return False

        upgrade_cost = 1000 * (specialist.level // 5 + 1)

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

        if self._logger:
            self._logger.info(f"[GAME_STATE] Specialist {specialist_id} upgraded ({upgrade_type}) for ${upgrade_cost}")

        return True

    # Getter methods (omitted for brevity, as they were correct)
    def get_specialist_by_id(self, specialist_id: str) -> Optional[Specialist]:
        return next((s for s in self.specialists if s.id == specialist_id), None)

    def get_incident_by_id(self, incident_id: str) -> Optional[Incident]:
        return next((i for i in self.incidents if i.id == incident_id), None)

    def get_client_by_id(self, client_id: str) -> Optional[Client]:
        return next((c for c in self.clients if c.client_id == client_id), None)

    def get_automation_script_by_id(self, script_id: str) -> Optional[AutomationScript]:
        return next((a for a in self.automation_scripts if a.id == script_id), None)

    def get_available_specialists(self) -> List[Specialist]:
        return [s for s in self.specialists if s.is_available()]

    def get_pending_incidents(self) -> List[Incident]:
        return [i for i in self.incidents if i.status == "pending"]

    def get_game_time_elapsed(self) -> float:
        return self.current_time - self.game_start_time

    def get_game_summary(self) -> Dict[str, Any]:
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
        
        if hasattr(self, '_last_offline_report'):
            summary["offline_progress"] = self._last_offline_report
        
        return summary

    def get_offline_progress_report(self) -> Optional[Dict[str, Any]]:
        return getattr(self, '_last_offline_report', None)

    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for serialization."""
        return {
            "specialists": [s.to_dict() for s in self.specialists],
            "incidents": [i.to_dict() for i in self.incidents],
            "clients": [c.to_dict() for c in self.clients],
            "contracts": [c.to_dict() for c in self.contracts] if hasattr(self, 'contracts') else [],
            "facilities": [f.to_dict() for f in self.facilities] if hasattr(self, 'facilities') else [],
            "recruitment_pool": self.recruitment_pool if hasattr(self, 'recruitment_pool') else [],
            "recruitment_refresh_time": self.recruitment_refresh_time if hasattr(self, 'recruitment_refresh_time') else 0.0,
            "active_events": self.active_events if hasattr(self, 'active_events') else [],
            "event_cooldowns": self.event_cooldowns.copy() if hasattr(self, 'event_cooldowns') else {},
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
        """Create GameState from dictionary (for loaded games)."""
        instance = cls.__new__(cls)

        # Initialize minimal essentials first
        instance._json_loader = JSONLoader()
        instance._logger = GameLogger("game_state")

        # Load entities
        instance.specialists = [Specialist.from_dict(s) for s in data.get("specialists", [])]
        instance.incidents = [Incident.from_dict(i) for i in data.get("incidents", [])]
        instance.clients = [Client.from_dict(c) for c in data.get("clients", [])]
        
        # Load tycoon system entities
        instance.contracts = []
        if "contracts" in data:
            try:
                from src.models.contract import Contract
                instance.contracts = [Contract.from_dict(c) for c in data["contracts"]]
            except ImportError:
                pass
        
        instance.facilities = []
        if "facilities" in data:
            try:
                from src.models.facility import Facility
                instance.facilities = [Facility.from_dict(f) for f in data["facilities"]]
            except ImportError:
                pass
        
        # Load simple state data
        instance.recruitment_pool = data.get("recruitment_pool", []).copy()
        instance.recruitment_refresh_time = data.get("recruitment_refresh_time", 0.0)
        instance.active_events = data.get("active_events", []).copy()
        instance.event_cooldowns = data.get("event_cooldowns", {}).copy()
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

        # Initialize internal state (defaults)
        instance._incident_generator = IncidentGenerator(instance._logger)
        instance._automation_processor = AutomationProcessor(instance._logger)
        instance._last_incident_generation = time.time()
        instance._incident_generation_accumulator = 0.0
        instance._offline_progress_calculated = False
        
        # Initialize ALL CORE SYSTEMS using the consolidated helper
        instance._initialize_core_systems()
        
        # Load automation scripts (done again after system init to use the loader)
        try:
            automation_data = instance._json_loader.load_data("automation_scripts.json")
            if "automation_scripts" in automation_data:
                instance.automation_scripts = [AutomationScript.from_dict(a) for a in automation_data["automation_scripts"]]
        except Exception:
            instance.automation_scripts = []

        return instance

    @property
    def incident_generator(self) -> Optional[IncidentGenerator]:
        """Get the incident generator instance."""
        return self._incident_generator

    @property
    def config(self) -> Dict[str, Any]:
        """Get game configuration (lazy-loaded)."""
        if not hasattr(self, '_cached_config'):
            if self._json_loader:
                self._cached_config = self._json_loader.load_data("game_config.json")
            else:
                self._cached_config = {}
        return self._cached_config

    # === PHASE 1: SOC STARTUP CORE METHODS ===
    
    def get_active_clients(self) -> List[Client]:
        """Get all currently active clients."""
        return [c for c in self.clients if c.is_active]
    
    def get_sla_tracker_for_client_this_month(self, client_id: str) -> Optional[SLATracker]:
        """Get SLA tracker for client in current month."""
        for tracker in self.sla_trackers:
            if tracker.client_id == client_id and tracker.month == self.current_month:
                return tracker
        return None
    
    def create_sla_tracker_for_client(self, client_id: str) -> SLATracker:
        """Create new SLA tracker for client in current month."""
        tracker_id = f"sla_{client_id}_{self.current_month}"
        tracker = SLATracker(
            tracker_id=tracker_id,
            client_id=client_id,
            month=self.current_month,
        )
        self.sla_trackers.append(tracker)
        return tracker

    def __repr__(self) -> str:
        """String representation of game state."""
        return (f"GameState(specialists={len(self.specialists)}, "
                        f"incidents={len(self.incidents)}, clients={len(self.clients)}, "
                        f"money=${self.current_money:.0f}, time={self.get_game_time_elapsed():.0f}s)")