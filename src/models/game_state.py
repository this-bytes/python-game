"""GameState model representing the complete state of the cybersecurity firm game.

The GameState is now a facade that coordinates the layered architecture:
- StateManager: Pure data layer for entity storage and CRUD operations
- GameLogic: Business rules and game mechanics
- SystemCoordinator: Internal system management and time-based updates

This facade maintains the public API while delegating to the layered components.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
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

# Layered Architecture Imports
from src.core.state_manager import StateManager
from src.core.game_logic import GameLogic
from src.core.system_coordinator import SystemCoordinator

# Core System Imports (for backward compatibility)
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
    """Facade for the layered game state architecture.

    This class maintains the public API while delegating to the layered components:
    - StateManager: Pure data layer for entity storage and CRUD operations
    - GameLogic: Business rules and game mechanics
    - SystemCoordinator: Internal system management and time-based updates
    """

    # Layered Architecture Components
    _state_manager: StateManager = field(init=False)
    _game_logic: GameLogic = field(init=False)
    _system_coordinator: SystemCoordinator = field(init=False)

    # Observer pattern for UI state change notifications
    _observers: List[Callable[[str, Any], None]] = field(default_factory=list)

    # Legacy attributes for backward compatibility (delegated to layers via properties)
    # Note: These are now properties that delegate to the layered architecture

    # Internal systems (for backward compatibility)
    _json_loader: Optional[JSONLoader] = field(init=False)
    _logger: Optional[GameLogger] = field(init=False)
    _incident_generator: Optional[IncidentGenerator] = field(init=False)
    _automation_processor: Optional[AutomationProcessor] = field(init=False)
    _passive_income_system: Optional[PassiveIncomeSystem] = field(init=False)
    _relationships_system: Optional[RelationshipsSystem] = field(init=False)
    _dopamine_system: Optional[DopamineSystem] = field(init=False)
    _idle_core: Optional[Any] = field(init=False)
    _equipment_system: Optional[EquipmentSystem] = field(init=False)
    _last_incident_generation: float = field(init=False)
    _incident_generation_accumulator: float = field(init=False)
    _offline_progress_calculated: bool = field(init=False)
    _last_offline_report: Optional[Dict[str, Any]] = field(init=False)

    def __init__(
        self,
        specialists: int = 0,
        incidents: int = 0,
        clients: int = 0,
        money: float = 5000.0,
        time: float = 0.0,
        **kwargs
    ) -> None:
        """Construct a GameState with optional quick-test parameters.

        Tests often construct GameState(specialists=5, incidents=4, clients=6,...).
        This initializer supports that pattern, then delegates to the dataclass
        post-init to wire up the layered architecture.
        """
        # Minimal observer list until layered systems are initialized
        self._observers = []

        # Store requested bootstrap numbers or explicit lists for post-init population
        # Accept either an integer count OR a list of pre-built objects (for tests)
        if isinstance(specialists, list):
            self._bootstrap_specialists = len(specialists)
            self._bootstrap_specialists_list = list(specialists)
        else:
            self._bootstrap_specialists = int(specialists or 0)
            self._bootstrap_specialists_list = None

        if isinstance(incidents, list):
            self._bootstrap_incidents = len(incidents)
            self._bootstrap_incidents_list = list(incidents)
        else:
            self._bootstrap_incidents = int(incidents or 0)
            self._bootstrap_incidents_list = None

        if isinstance(clients, list):
            self._bootstrap_clients = len(clients)
            self._bootstrap_clients_list = list(clients)
        else:
            self._bootstrap_clients = int(clients or 0)
            self._bootstrap_clients_list = None
        self._bootstrap_money = float(money)
        self._bootstrap_time = float(time)

        # Now run full post-init to initialize layered architecture
        self.__post_init__()

        # After layered systems are ready, populate requested entities
        try:
            if hasattr(self, '_bootstrap_clients_list') and self._bootstrap_clients_list is not None:
                # Tests passed explicit client objects; use them directly
                self.clients = self._bootstrap_clients_list
            elif self._bootstrap_clients > 0:
                # Create simple placeholder clients if JSON not available
                from src.models.client import Client
                for i in range(self._bootstrap_clients):
                    cid = f"client_{i+1:03d}"
                    client = Client(
                        client_id=cid,
                        company_name=f"Client {i+1}",
                        industry="generic",
                        monthly_contract_value=1000.0,
                        sla_response_time_seconds=600,
                        sla_resolution_time_seconds=3600,
                        satisfaction=1.0,
                    )
                    self._state_manager.add_client(client)

            if hasattr(self, '_bootstrap_specialists_list') and self._bootstrap_specialists_list is not None:
                # Use provided specialists list directly
                self.specialists = self._bootstrap_specialists_list
            elif self._bootstrap_specialists > 0:
                # Create simple specialists
                for i in range(self._bootstrap_specialists):
                    spec_id = f"spec_{i+1:03d}"
                    spec = Specialist(
                        id=spec_id,
                        name=f"Spec {i+1}",
                        specialty="Network Security",
                        level=1,
                        xp=0,
                        stats=SpecialistStats(speed=100, accuracy=80, experience_bonus=1.0),
                    )
                    self._state_manager.specialists[spec.id] = spec

            if hasattr(self, '_bootstrap_incidents_list') and self._bootstrap_incidents_list is not None:
                # Use provided incident objects directly
                self.incidents = self._bootstrap_incidents_list
            elif self._bootstrap_incidents > 0:
                for i in range(self._bootstrap_incidents):
                    inc = Incident(
                        id=f"inc_{i+1:06d}",
                        incident_type="DDoS Attack",
                        difficulty=1,
                        status="pending",
                    )
                    self._state_manager.add_incident(inc)

            # Apply bootstrap money and time
            if hasattr(self._state_manager, 'budget') and self._state_manager.budget:
                self._state_manager.budget.total_reserves = self._bootstrap_money
            self._state_manager.game_time = self._bootstrap_time
        except Exception:
            # Best-effort population for test harness; do not fail init
            if self._logger:
                self._logger.debug("[GAME_STATE] Bootstrap population encountered an issue during __init__")

    def __post_init__(self):
        """Initialize game state facade with layered architecture."""
        # Initialize essential systems first
        self._initialize_essential_systems()

        # Initialize layered components
        self._initialize_layered_architecture()

        # Initialize legacy systems for backward compatibility
        self._initialize_legacy_systems()

        # Set up backward compatibility properties
        self._setup_backward_compatibility()

        # Load initial data and set up event subscriptions
        self._initialize_game_data()

        # Initialize simple in-memory flags for properties not yet in StateManager
        # These provide backward-compatible storage until full migration
        self._is_paused = False
        self._game_speed_multiplier = 1.0
        self._investments = {}

    def _initialize_essential_systems(self):
        """Initialize essential systems needed by layered architecture."""
        # Initialize JSON loader and logger first
        self._initialize_json_loader()
        self._initialize_logger()

    def _initialize_layered_architecture(self):
        """Initialize the layered architecture components."""
        # Load game config first
        game_config = {}
        if self._json_loader:
            try:
                game_config = self._json_loader.load_data("game_config.json")
            except Exception as e:
                if self._logger:
                    self._logger.warning(f"[GAME_STATE] Failed to load game config: {e}")

        # Initialize StateManager with starting budget
        self._state_manager = StateManager(budget=Budget(total_reserves=5000.0))

        # Initialize GameLogic with game config
        self._game_logic = GameLogic(game_config)

        # Initialize SystemCoordinator with all required parameters
        self._system_coordinator = SystemCoordinator(self._state_manager, self._game_logic, game_config)

    def _initialize_legacy_systems(self):
        """Initialize legacy systems for backward compatibility."""
        # Initialize essential systems
        self._json_loader = None
        self._logger = None
        self._incident_generator = None
        self._automation_processor = None
        self._passive_income_system = None
        self._relationships_system = None
        self._dopamine_system = None
        self._idle_core = None
        self._equipment_system = None
        # Backing storage for features not yet migrated into StateManager
        # Initialize automation scripts storage so _load_initial_data can populate it
        self._automation_scripts: List[AutomationScript] = []

        # Initialize timing accumulators
        self._last_incident_generation = time.time()
        self._incident_generation_accumulator = 0.0
        self._offline_progress_calculated = False
        self._last_offline_report = None

        # Initialize JSON loader and logger
        self._initialize_json_loader()
        self._initialize_logger()

        # Initialize core systems using layered approach
        self._initialize_core_systems()

    def _initialize_json_loader(self):
        """Initialize JSON loader."""
        import os
        current_dir = os.getcwd()
        if os.path.basename(current_dir) == 'src':
            project_root = os.path.dirname(current_dir)
        else:
            project_root = current_dir
        data_dir = os.path.join(project_root, "data")
        self._json_loader = JSONLoader(data_dir=data_dir)

    def _initialize_logger(self):
        """Initialize logger."""
        self._logger = GameLogger("game_state")

    def _setup_backward_compatibility(self):
        """Set up properties that delegate to layered components for backward compatibility."""
        # These will be properties that convert between dict/list formats
        pass

    # Backward compatibility properties that convert between StateManager dicts and GameState lists
    @property
    def specialists(self) -> List[Specialist]:
        """Get specialists as list for backward compatibility."""
        return list(self._state_manager.specialists.values())

    @specialists.setter
    def specialists(self, value: List[Specialist]):
        """Set specialists from list, converting to dict storage."""
        self._state_manager.specialists = {s.id: s for s in value}

    @property
    def incidents(self) -> List[Incident]:
        """Get incidents as list for backward compatibility."""
        return list(self._state_manager.incidents.values())

    @incidents.setter
    def incidents(self, value: List[Incident]):
        """Set incidents from list, converting to dict storage."""
        self._state_manager.incidents = {i.id: i for i in value}

    # Convenience API: add/remove incidents via the facade to ensure persistence
    def add_incident(self, incident: Incident) -> None:
        """Add an incident into the canonical StateManager store.

        This is the preferred API for creating/persisting incidents. It
        guarantees the incident is stored in the authoritative StateManager
        and not lost by mutating transient list views.

        Args:
            incident: Incident instance to add
        """
        try:
            self._state_manager.add_incident(incident)
            if self._logger:
                self._logger.info(f"[GAME_STATE] Incident added: id={incident.id} type={getattr(incident,'incident_type',None)}")
            self._notify_observers("incident_added", incident)
        except Exception as e:
            if self._logger:
                self._logger.error(f"[GAME_STATE] Failed to add incident {getattr(incident,'id',None)}: {e}")
            raise

    def remove_incident(self, incident_id: str) -> Optional[Incident]:
        """Remove an incident by id from the canonical StateManager store.

        Returns the removed Incident or None if not found.
        """
        try:
            removed = self._state_manager.remove_incident(incident_id)
            if removed and self._logger:
                self._logger.info(f"[GAME_STATE] Incident removed: id={incident_id}")
            if removed:
                self._notify_observers("incident_removed", removed)
            return removed
        except Exception as e:
            if self._logger:
                self._logger.error(f"[GAME_STATE] Failed to remove incident {incident_id}: {e}")
            raise

    def add_observer(self, callback: Callable[[str, Any], None]) -> None:
        """Register an observer callback for GameState events.

        Callback signature: fn(event_type: str, payload: Any)
        """
        if callback not in self._observers:
            self._observers.append(callback)

    def _notify_observers(self, event_type: str, payload: Any) -> None:
        """Internal: notify registered observers of an event."""
        for cb in list(self._observers):
            try:
                cb(event_type, payload)
            except Exception:
                # Observers must not break game flow; log and continue
                if self._logger:
                    self._logger.exception(f"[GAME_STATE] Observer callback failed for event {event_type}")

    @property
    def clients(self) -> List[Client]:
        """Get clients as list for backward compatibility."""
        return list(self._state_manager.clients.values())

    @clients.setter
    def clients(self, value: List[Client]):
        """Set clients from list, converting to dict storage."""
        self._state_manager.clients = {c.client_id: c for c in value}

    @property
    def contracts(self) -> List:
        """Get contracts as list for backward compatibility."""
        return list(self._state_manager.contracts.values())

    @contracts.setter
    def contracts(self, value: List):
        """Set contracts from list, converting to dict storage."""
        self._state_manager.contracts = {c.id: c for c in value}

    @property
    def sla_trackers(self) -> List[SLATracker]:
        """Get SLA trackers as list for backward compatibility."""
        return list(self._state_manager.sla_trackers.values())

    @sla_trackers.setter
    def sla_trackers(self, value: List[SLATracker]):
        """Set SLA trackers from list, converting to dict storage."""
        self._state_manager.sla_trackers = {t.tracker_id: t for t in value}

    @property
    def budget(self) -> Budget:
        """Get budget from StateManager."""
        return self._state_manager.budget or Budget(total_reserves=5000.0)

    @budget.setter
    def budget(self, value: Budget):
        """Set budget in StateManager."""
        self._state_manager.budget = value

    # Simple delegation properties for other attributes
    @property
    def game_start_time(self) -> float:
        return self._state_manager.game_time

    @game_start_time.setter
    def game_start_time(self, value: float):
        self._state_manager.game_time = value

    @property
    def current_time(self) -> float:
        return self._state_manager.game_time

    @current_time.setter
    def current_time(self, value: float):
        self._state_manager.game_time = value

    @property
    def current_money(self) -> float:
        return self._state_manager.budget.total_reserves if self._state_manager.budget else 5000.0

    @current_money.setter
    def current_money(self, value: float):
        if self._state_manager.budget:
            self._state_manager.budget.total_reserves = value

    @property
    def total_money_earned(self) -> float:
        return self._state_manager.total_money_earned

    @total_money_earned.setter
    def total_money_earned(self, value: float):
        self._state_manager.total_money_earned = value

    # Placeholder properties for attributes not yet in StateManager
    @property
    def automation_scripts(self) -> List[AutomationScript]:
        # Return the in-memory automation scripts list. In the future this
        # should be persisted via StateManager; for now keep a local list to
        # satisfy tests and legacy consumers.
        return getattr(self, '_automation_scripts', [])

    @automation_scripts.setter
    def automation_scripts(self, value: List[AutomationScript]):
        # Store automation scripts in backing list for legacy compatibility.
        # Expect a list of AutomationScript instances.
        self._automation_scripts = list(value) if value is not None else []

    @property
    def equipment_instances(self) -> Dict[str, Any]:
        return {}

    @equipment_instances.setter
    def equipment_instances(self, value: Dict[str, Any]):
        pass  # TODO: Add to StateManager

    @property
    def facilities(self) -> List:
        return []

    @facilities.setter
    def facilities(self, value: List):
        pass  # TODO: Add to StateManager

    @property
    def recruitment_pool(self) -> List[Dict]:
        return []

    @recruitment_pool.setter
    def recruitment_pool(self, value: List[Dict]):
        pass  # TODO: Add to StateManager

    @property
    def recruitment_refresh_time(self) -> float:
        return 0.0

    @recruitment_refresh_time.setter
    def recruitment_refresh_time(self, value: float):
        pass  # TODO: Add to StateManager

    @property
    def active_events(self) -> List[Dict]:
        return []

    @active_events.setter
    def active_events(self, value: List[Dict]):
        pass  # TODO: Add to StateManager

    @property
    def event_cooldowns(self) -> Dict[str, float]:
        return {}

    @event_cooldowns.setter
    def event_cooldowns(self, value: Dict[str, float]):
        pass  # TODO: Add to StateManager

    @property
    def game_speed_multiplier(self) -> float:
        return getattr(self, '_game_speed_multiplier', 1.0)

    @game_speed_multiplier.setter
    def game_speed_multiplier(self, value: float):
        self._game_speed_multiplier = float(value or 1.0)

    @property
    def is_paused(self) -> bool:
        return getattr(self, '_is_paused', False)

    @is_paused.setter
    def is_paused(self, value: bool):
        self._is_paused = bool(value)

    @property
    def investments(self) -> Dict[str, float]:
        return getattr(self, '_investments', {})

    @investments.setter
    def investments(self, value: Dict[str, float]):
        self._investments = dict(value or {})

    @property
    def company_founded_month(self) -> int:
        return 0

    @company_founded_month.setter
    def company_founded_month(self, value: int):
        pass  # TODO: Add to StateManager

    @property
    def current_month(self) -> int:
        return 1

    @current_month.setter
    def current_month(self, value: int):
        pass  # TODO: Add to StateManager

    @property
    def last_save_time(self) -> float:
        return time.time()

    @last_save_time.setter
    def last_save_time(self, value: float):
        pass  # TODO: Add to StateManager

    @property
    def prestige_points(self) -> int:
        return getattr(self._state_manager, 'prestige_points', 0)

    @prestige_points.setter
    def prestige_points(self, value: int):
        setattr(self._state_manager, 'prestige_points', int(value or 0))

    @property
    def prestige_upgrades(self) -> Dict[str, int]:
        return getattr(self._state_manager, 'prestige_upgrades', {})

    @prestige_upgrades.setter
    def prestige_upgrades(self, value: Dict[str, int]):
        setattr(self._state_manager, 'prestige_upgrades', dict(value or {}))

    @property
    def total_prestiges(self) -> int:
        return getattr(self._state_manager, 'total_prestiges', 0)

    @total_prestiges.setter
    def total_prestiges(self, value: int):
        setattr(self._state_manager, 'total_prestiges', int(value or 0))

    @property
    def unlocked_achievements(self) -> List[str]:
        return getattr(self._state_manager, 'unlocked_achievements', [])

    @unlocked_achievements.setter
    def unlocked_achievements(self, value: List[str]):
        setattr(self._state_manager, 'unlocked_achievements', list(value or []))

    @property
    def achievement_progress(self) -> Dict[str, float]:
        return getattr(self._state_manager, 'achievement_progress', {})

    @achievement_progress.setter
    def achievement_progress(self, value: Dict[str, float]):
        setattr(self._state_manager, 'achievement_progress', dict(value or {}))

    @property
    def dopamine_feedback_queue(self) -> List[Dict]:
        return []

    @dopamine_feedback_queue.setter
    def dopamine_feedback_queue(self, value: List[Dict]):
        pass  # TODO: Add to StateManager

    @property
    def active_risk_contracts(self) -> Dict[str, Any]:
        return {}

    @active_risk_contracts.setter
    def active_risk_contracts(self, value: Dict[str, Any]):
        pass  # TODO: Add to StateManager

    @property
    def max_active_incidents(self) -> int:
        return 50

    @max_active_incidents.setter
    def max_active_incidents(self, value: int):
        pass  # TODO: Add to StateManager

    @property
    def max_specialists(self) -> int:
        return 10

    @max_specialists.setter
    def max_specialists(self, value: int):
        pass  # TODO: Add to StateManager

    @property
    def incident_generation_enabled(self) -> bool:
        return True

    @incident_generation_enabled.setter
    def incident_generation_enabled(self, value: bool):
        pass  # TODO: Add to StateManager

    @property
    def metrics(self) -> GameMetrics:
        # Use in-memory backing field for metrics until StateManager integration
        return getattr(self, '_metrics', GameMetrics())

    @metrics.setter
    def metrics(self, value: GameMetrics):
        # Store metrics in a private backing field. Migration to StateManager
        # will later persist these into the canonical store.
        if isinstance(value, GameMetrics):
            self._metrics = value
        elif isinstance(value, dict):
            # Allow assignment from dict for deserialization convenience
            self._metrics = GameMetrics.from_dict(value)
        else:
            # Fallback: create empty metrics
            self._metrics = GameMetrics()

    def _initialize_game_data(self):
        """Initialize game data and set up subscriptions."""
        # Load initial data for new games
        if not self.specialists:
            self._load_initial_data()
            self._generate_initial_incidents()

        # Check for offline progress
        self._check_offline_progress()

        # Set up event bus subscriptions
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
                    # Persist incident into the StateManager (do not append to temporary list)
                    self._state_manager.add_incident(incident)
                    if self._logger:
                        # Log full incident id and initial status for lifecycle tracing
                        # Note: Incident uses 'incident_type' as the label field
                        self._logger.info(
                            f"[GAME_STATE] Generated initial incident: id={incident.id} incident_type={incident.incident_type} status={getattr(incident,'status',None)} difficulty={getattr(incident,'difficulty',None)} spawn_time={getattr(incident,'spawn_time',None)} ts={time.time()}"
                        )
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
        """Update game state by delegating to the layered architecture."""
        if self.is_paused:
            return

        effective_delta = delta_time * self.game_speed_multiplier
        self.current_time += effective_delta

        # Delegate to SystemCoordinator for time-based updates
        self._system_coordinator.update(effective_delta)

        # Notify observers of state changes
        self._notify_observers("game_updated", {"delta_time": effective_delta})

    def add_observer(self, observer: Callable[[str, Any], None]):
        """Add an observer for state change notifications."""
        self._observers.append(observer)

    def remove_observer(self, observer: Callable[[str, Any], None]):
        """Remove an observer."""
        self._observers.remove(observer)

    def _notify_observers(self, event_type: str, data: Any):
        """Notify all observers of a state change."""
        for observer in self._observers:
            try:
                observer(event_type, data)
            except Exception as e:
                if self._logger:
                    self._logger.warning(f"[GAME_STATE] Observer notification failed: {e}")

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

        # Remove resolved/failed incidents from the StateManager
        for incident in incidents_to_remove:
            try:
                self._state_manager.remove_incident(incident.id)
            except Exception:
                # Defensive: fall back to list removal if necessary
                try:
                    self.incidents.remove(incident)
                except Exception:
                    if self._logger:
                        self._logger.debug(f"[GAME_STATE] Could not remove incident {getattr(incident,'id',None)} from state manager")

    def _generate_incidents(self, delta_time: float):
        """Generate new incidents based on client rates."""
        if not self.incident_generation_enabled or not self._incident_generator or not self._dopamine_system:
            return

        for client in self.clients:
            if self._incident_generator.should_generate_incident(client, delta_time, len(self.incidents)):
                incident = self._incident_generator.generate_incident(client)
                if incident:
                    # Persist generated incident into StateManager
                    self._state_manager.add_incident(incident)
                    
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
        """Manually assign an incident to a specialist via GameLogic."""
        incident = self.get_incident_by_id(incident_id)
        specialist = self.get_specialist_by_id(specialist_id)

        if not incident or not specialist:
            return False

        result = self._game_logic.assign_specialist_to_incident(
            specialist=specialist,
            incident=incident,
            state_manager=self._state_manager
        )

        # Notify observers of assignment
        if result.success:
            # Log assignment for lifecycle tracing
            if self._logger:
                self._logger.info(
                    f"[GAME_STATE] Incident assigned: incident_id={incident_id} -> specialist_id={specialist_id} at time={self.current_time} ts={time.time()}"
                )

            self._notify_observers("incident_assigned", {
                "incident_id": incident_id,
                "specialist_id": specialist_id,
                "assignment_time": self.current_time
            })

            # Publish event on the global EventBus so systems like SLAPlugin can react
            try:
                event_bus = get_event_bus()
                client = None
                client_id_val = getattr(incident, 'client_id', None)
                if isinstance(client_id_val, str) and client_id_val:
                    client = self.get_client_by_id(client_id_val)
                event_bus.publish("incident_assigned", {
                    "incident_id": incident_id,
                    "specialist_id": specialist_id,
                    "incident": incident,
                    "specialist": specialist,
                    "client": client,
                    "assignment_time": self.current_time,
                })
            except Exception:
                # Best-effort publish; never break assignment on event failure
                pass

        return result.success

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

        # Initialize essential systems and layered architecture so property
        # setters (which delegate to StateManager) are safe to use.
        try:
            # essential systems set up JSON loader and logger
            instance._initialize_essential_systems()
        except Exception:
            # Fallback to best-effort minimal initialization
            instance._json_loader = JSONLoader()
            instance._logger = GameLogger("game_state")

        # Initialize layered architecture (creates StateManager, GameLogic, etc.)
        try:
            instance._initialize_layered_architecture()
        except Exception:
            # If layered init fails, leave instance in minimal usable state
            if not hasattr(instance, '_state_manager'):
                from src.core.state_manager import StateManager
                instance._state_manager = StateManager(budget=Budget(total_reserves=5000.0))

        # Initialize legacy systems which also prepares core systems that expect
        # attributes like _dopamine_system, _idle_core, etc.
        try:
            instance._initialize_legacy_systems()
        except Exception:
            # Best-effort: ensure attributes referenced by core init exist
            for attr in ('_dopamine_system', '_idle_core', '_equipment_system', '_relationships_system', '_automation_processor', '_incident_generator', '_passive_income_system'):
                if not hasattr(instance, attr):
                    setattr(instance, attr, None)

        # Load entities into the StateManager-backed properties
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