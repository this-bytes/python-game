Copilot said: # 🎮 CYBERSECURITY FIRM TYCOON - COMPREHENSIVE
🎮 CYBERSECURITY FIRM TYCOON - COMPREHENSIVE EXECUTION PLAN
"From Vision to Reality: The Complete Roadmap"

📋 EXECUTIVE SUMMARY
Current State: Solid foundation with core mechanics, plugin architecture, and professional UI framework.

Target State: Active strategy tycoon where players progress from manual incident triage (responder) → automated systems (manager) → empire orchestration (CEO).

Critical Path: 12 weeks to playable v1.0, 6 months to feature-complete.

Success Metric: Player can play for 2+ hours without getting bored, then prestige and want to play again.

🚨 BEFORE YOU START - READ THIS
For AI Agents Executing This Plan:
Read ALL instruction files first - Especially core-standards.instructions.md
Update docs as you go - Document in docs/ for features, update instruction files for patterns
No shortcuts - 15-point gate applies to EVERY commit
Test everything - 80%+ coverage, no exceptions
JSON-first - All game parameters in config files
Ask before deviating - If plan unclear, ask human for clarification
Documentation Standards:
New features → Create docs/FEATURE_NAME.md
New patterns → Update relevant instruction file
Architecture changes → Update ARCHITECTURE.md
Breaking changes → Update PROGRESS.md with migration notes
🎯 PHASE 1: CORE LOOP REFINEMENT (Weeks 1-2)
Goal: Make the 30-second loop PERFECT before adding depth.

TASK 1.1: Incident Resolution Depth ⭐ HIGH PRIORITY
Owner: AI Agent
Duration: 3 days
Deliverable: Decision-based incident resolution system

Requirements:
Python
# Create: src/core/resolution_system.py

class ResolutionSystem:
    """Decision-based incident resolution with player agency."""
    
    def start_resolution(
        self, 
        incident: Incident, 
        specialist: Specialist
    ) -> ResolutionSession:
        """
        Start incident resolution.
        
        Returns ResolutionSession with:
        - Available actions (containment options)
        - Decision tree state
        - Time pressure mechanics
        """
        pass
    
    def make_decision(
        self, 
        session: ResolutionSession, 
        decision: ResolutionDecision
    ) -> ResolutionResult:
        """
        Player makes decision during resolution.
        
        Decisions affect:
        - Resolution speed
        - Quality/accuracy
        - Money cost
        - Specialist burnout
        """
        pass
Decision Tree Example:
JSON
// data/resolution_trees.json
{
  "ddos_attack": {
    "name": "DDoS Attack Resolution",
    "stages": [
      {
        "stage_id": "containment",
        "prompt": "DDoS attack detected. How do you respond?",
        "decisions": [
          {
            "id": "block_ips",
            "text": "Block attacking IP ranges",
            "effects": {
              "time_multiplier": 0.8,
              "accuracy_check": true,
              "burnout_cost": 5
            }
          },
          {
            "id": "migrate_cdn",
            "text": "Migrate traffic to CDN",
            "effects": {
              "time_multiplier": 0.5,
              "money_cost": 2000,
              "burnout_cost": 2
            }
          },
          {
            "id": "analyze_first",
            "text": "Analyze attack pattern first",
            "effects": {
              "time_multiplier": 1.2,
              "accuracy_bonus": 20,
              "burnout_cost": 10
            }
          }
        ],
        "next_stage": "investigation"
      }
    ]
  }
}
Implementation Checklist:
 Create ResolutionSystem class
 Implement decision tree parser
 Add specialist skill checks (accuracy determines success)
 Create resolution trees for 5 incident types (DDoS, Malware, Phishing, Breach, Ransomware)
 Add time pressure mechanic (decisions under SLA timer)
 Integrate with existing incident flow
 Write 15+ unit tests covering all decision paths
 Document in docs/INCIDENT_RESOLUTION_SYSTEM.md
 Update workflows.instructions.md with "How to add resolution tree"
Acceptance Criteria:
✅ Player can make meaningful decisions during incident resolution
✅ Decisions affect outcome (time, money, quality)
✅ Specialist stats influence success (high accuracy = better outcomes)
✅ Time pressure creates tension (SLA ticking down)
✅ All tests passing, 80%+ coverage
✅ Documentation complete

TASK 1.2: Automation Script Builder ⭐ HIGH PRIORITY
Owner: AI Agent
Duration: 4 days
Deliverable: Player-configurable automation system

Requirements:
Python
# Create: src/core/automation_builder.py

class AutomationBuilder:
    """Visual automation rule builder (IF-THEN logic)."""
    
    def create_rule(
        self,
        name: str,
        conditions: List[Condition],
        actions: List[Action],
        priority: int = 0
    ) -> AutomationRule:
        """
        Create automation rule.
        
        Conditions: incident.difficulty < 3, specialist.available, etc.
        Actions: auto_assign, notify_player, escalate, etc.
        Priority: Higher priority rules execute first
        """
        pass
    
    def evaluate_rules(
        self,
        incident: Incident,
        game_state: GameState
    ) -> Optional[AutomationAction]:
        """
        Evaluate all rules, return action to take.
        Returns None if no rule matches.
        """
        pass
Rule Configuration:
JSON
// data/automation_rules.json
{
  "rules": [
    {
      "id": "auto_easy_incidents",
      "name": "Auto-Assign Easy Incidents",
      "unlock_level": 5,
      "conditions": [
        {
          "type": "incident_difficulty",
          "operator": "less_than",
          "value": 3
        },
        {
          "type": "specialist_available",
          "operator": "equals",
          "value": true
        },
        {
          "type": "specialty_match",
          "operator": "equals",
          "value": true
        }
      ],
      "actions": [
        {
          "type": "auto_assign",
          "target": "best_available_specialist"
        }
      ],
      "priority": 10,
      "enabled": true
    }
  ]
}
UI Integration:
Python
# Create: src/ui/panels/automation_panel.py

class AutomationPanel(Panel):
    """
    Visual rule builder.
    
    Shows:
    - List of unlocked automation rules
    - Enable/disable toggles
    - Visual rule builder (drag-and-drop)
    - Test automation button (simulate rules)
    """
    pass
Implementation Checklist:
 Create AutomationBuilder class with rule evaluation
 Implement condition types (10+ types: difficulty, specialty, level, burnout, etc.)
 Implement action types (auto_assign, notify, escalate, skip)
 Add priority system (higher priority = execute first)
 Create default automation rules (5 templates)
 Build visual rule builder UI panel
 Add rule testing/simulation mode
 Integrate with incident assignment flow
 Write 20+ unit tests covering all condition/action types
 Document in docs/AUTOMATION_SYSTEM.md
 Update workflows.instructions.md with "How to create automation rule"
Acceptance Criteria:
✅ Player can create custom automation rules
✅ Rules execute based on priority
✅ 10+ condition types available
✅ 5+ action types available
✅ Visual UI for rule management
✅ Can test rules before enabling
✅ All tests passing, 80%+ coverage
✅ Documentation complete

TASK 1.3: Progressive Difficulty Curve
Owner: AI Agent
Duration: 2 days
Deliverable: Natural difficulty progression

Requirements:
Python
# Update: src/core/incident_generator.py

class IncidentGenerator:
    """Generate incidents with progressive difficulty."""
    
    def calculate_difficulty_range(
        self,
        game_state: GameState
    ) -> Tuple[int, int]:
        """
        Calculate difficulty range based on game progression.
        
        Early game (0-10 min): difficulty 1-2
        Mid game (10-30 min): difficulty 2-4
        Late game (30+ min): difficulty 3-5
        
        Factors:
        - Game time elapsed
        - Average specialist level
        - SLA compliance rate
        - Prestige level
        """
        pass
Configuration:
JSON
// data/game_config.json (update)
{
  "difficulty_curve": {
    "early_game": {
      "duration_minutes": 10,
      "difficulty_range": [1, 2],
      "incident_rate_multiplier": 0.8
    },
    "mid_game": {
      "duration_minutes": 20,
      "difficulty_range": [2, 4],
      "incident_rate_multiplier": 1.0
    },
    "late_game": {
      "duration_minutes": 30,
      "difficulty_range": [3, 5],
      "incident_rate_multiplier": 1.2
    }
  }
}
Implementation Checklist:
 Update IncidentGenerator with difficulty calculation
 Add time-based progression
 Add specialist-level-based scaling
 Add SLA-performance-based scaling
 Add prestige multipliers
 Balance difficulty curve (playtest!)
 Write 10+ tests for difficulty calculation
 Document in docs/DIFFICULTY_SYSTEM.md
Acceptance Criteria:
✅ Early game is approachable (difficulty 1-2)
✅ Mid game challenges player (difficulty 2-4)
✅ Late game requires optimization (difficulty 3-5)
✅ Smooth progression (no sudden spikes)
✅ All tests passing
✅ Documentation complete

🎯 PHASE 2: PROGRESSION DEPTH (Weeks 3-4)
Goal: Make specialist progression feel meaningful and strategic.

TASK 2.1: Specialist Skill Trees
Owner: AI Agent
Duration: 5 days
Deliverable: Deep specialization system

Requirements:
Python
# Create: src/core/skill_tree_system.py

class SkillTreeSystem:
    """Manage specialist skill trees and specialization paths."""
    
    def unlock_skill(
        self,
        specialist: Specialist,
        skill_id: str
    ) -> bool:
        """
        Unlock skill if requirements met.
        
        Requirements:
        - Skill points available
        - Prerequisites unlocked
        - Level requirement met
        """
        pass
    
    def get_available_skills(
        self,
        specialist: Specialist
    ) -> List[Skill]:
        """Get skills that can be unlocked now."""
        pass
Skill Tree Configuration:
JSON
// data/skill_trees.json
{
  "network_security": {
    "name": "Network Security Specialist",
    "tiers": [
      {
        "tier": 1,
        "skills": [
          {
            "id": "packet_analysis",
            "name": "Packet Analysis",
            "description": "+10% speed on Network Security incidents",
            "cost": 1,
            "effects": {
              "speed_multiplier": 1.1,
              "specialty_filter": "Network Security"
            }
          },
          {
            "id": "firewall_mastery",
            "name": "Firewall Mastery",
            "description": "+15% accuracy on DDoS incidents",
            "cost": 1,
            "effects": {
              "accuracy_multiplier": 1.15,
              "incident_type_filter": "DDoS Attack"
            }
          }
        ]
      },
      {
        "tier": 2,
        "skills": [
          {
            "id": "advanced_mitigation",
            "name": "Advanced Mitigation",
            "description": "Unlock 'Instant Block' ability",
            "cost": 2,
            "prerequisites": ["packet_analysis", "firewall_mastery"],
            "effects": {
              "unlock_ability": "instant_block"
            }
          }
        ]
      }
    ]
  }
}
UI Integration:
Python
# Create: src/ui/panels/skill_tree_panel.py

class SkillTreePanel(Panel):
    """
    Visual skill tree browser.
    
    Shows:
    - Tree structure (nodes connected by lines)
    - Available skills (highlighted)
    - Locked skills (grayed out)
    - Skill descriptions on hover
    - Allocate skill point button
    """
    pass
Implementation Checklist:
 Create SkillTreeSystem class
 Define skill trees for 6 specialties (Network, Malware, Social Eng, Crypto, Forensics, Compliance)
 Implement 30+ skills total (5 per specialty)
 Add prerequisite validation
 Create skill tree UI panel
 Add skill point allocation
 Add respec option (costs money)
 Write 25+ tests covering all skill interactions
 Document in docs/SKILL_TREE_SYSTEM.md
 Update workflows.instructions.md with "How to add new skill"
Acceptance Criteria:
✅ 6 specialties have unique skill trees
✅ 30+ skills total implemented
✅ Prerequisites work correctly
✅ Visual skill tree UI
✅ Can allocate/respec skill points
✅ All tests passing, 80%+ coverage
✅ Documentation complete

TASK 2.2: Dual-Class System
Owner: AI Agent
Duration: 3 days
Deliverable: Specialist multiclassing

Requirements:
Python
# Update: src/models/specialist.py

class Specialist:
    """Add dual-class support."""
    
    def unlock_secondary_specialty(
        self,
        specialty: str,
        cost: int
    ) -> bool:
        """
        Unlock secondary specialty.
        
        Requirements:
        - Level 20+ in primary specialty
        - Pay unlock cost (money)
        - Creates hybrid specialist
        """
        pass
    
    def get_specialty_bonuses(self, incident: Incident) -> float:
        """
        Calculate specialty bonuses.
        
        Primary specialty: 1.5x multiplier
        Secondary specialty: 1.2x multiplier
        Hybrid bonus: If incident matches both, 1.8x multiplier!
        """
        pass
Hybrid Specialties:
JSON
// data/hybrid_specialties.json
{
  "hybrids": [
    {
      "id": "apt_hunter",
      "name": "APT Hunter",
      "primary": "Network Security",
      "secondary": "Malware Analysis",
      "description": "Expert at detecting and analyzing Advanced Persistent Threats",
      "unlock_cost": 10000,
      "hybrid_bonus_multiplier": 1.8,
      "matching_incidents": ["APT Attack", "Zero-Day Exploit", "Advanced Malware"]
    },
    {
      "id": "social_engineer_defender",
      "name": "Social Engineering Defender",
      "primary": "Social Engineering",
      "secondary": "Incident Response",
      "description": "Specializes in detecting and preventing social engineering attacks",
      "unlock_cost": 8000,
      "hybrid_bonus_multiplier": 1.8,
      "matching_incidents": ["Phishing", "Spear Phishing", "Business Email Compromise"]
    }
  ]
}
Implementation Checklist:
 Add secondary specialty field to Specialist
 Implement unlock secondary specialty logic
 Create 6 hybrid specialty combinations
 Add hybrid bonus calculation
 Update assignment system to recognize hybrids
 Add UI for unlocking secondary specialty
 Write 15+ tests for hybrid mechanics
 Document in docs/DUAL_CLASS_SYSTEM.md
Acceptance Criteria:
✅ Specialists can unlock secondary specialty at level 20
✅ 6 hybrid combinations defined
✅ Hybrid bonuses calculated correctly (1.8x)
✅ UI for unlocking secondary
✅ All tests passing
✅ Documentation complete

TASK 2.3: Prestige System Overhaul
Owner: AI Agent
Duration: 4 days
Deliverable: Meaningful prestige progression

Requirements:
python#

class PrestigeSystem:
    """Overhauled prestige with meaningful bonuses."""
    
    def calculate_prestige_points(
        self,
        game_state: GameState
    ) -> int:
        """
        Calculate prestige points earned.
        
        Based on:
        - Total money earned (1 point per $10k)
        - Incidents resolved (1 point per 100)
        - SLA compliance (bonus if >95%)
        - Achievements unlocked (10 points each)
        - Specialist levels (1 point per 10 total levels)
        """
        pass
    
    def apply_prestige_bonuses(
        self,
        game_state: GameState,
        prestige_upgrades: List[str]
    ):
        """
        Apply permanent bonuses from prestige upgrades.
        
        Example bonuses:
        - +10% XP gain
        - Start with 2 specialists instead of 1
        - +5000 starting money
        - Unlock automation at level 1
        """
        pass
Prestige Upgrades:
JSON
// data/prestige_upgrades.json
{
  "upgrades": [
    {
      "id": "experienced_leader",
      "name": "Experienced Leader",
      "description": "Start with 2 specialists instead of 1",
      "cost": 10,
      "max_purchases": 1,
      "effects": {
        "starting_specialists": 2
      }
    },
    {
      "id": "wealth_accumulation",
      "name": "Wealth Accumulation",
      "description": "+$5000 starting money",
      "cost": 15,
      "max_purchases": 5,
      "effects": {
        "starting_money_bonus": 5000
      }
    },
    {
      "id": "quick_learner",
      "name": "Quick Learner",
      "description": "+10% XP gain (stacks)",
      "cost": 20,
      "max_purchases": 10,
      "effects": {
        "xp_multiplier": 0.1
      }
    },
    {
      "id": "automation_expert",
      "name": "Automation Expert",
      "description": "Unlock automation rules at level 1",
      "cost": 25,
      "max_purchases": 1,
      "effects": {
        "automation_unlock_level": 1
      }
    }
  ]
}
Implementation Checklist:
 Update prestige point calculation (5 factors)
 Create 15+ prestige upgrades
 Add prestige upgrade shop UI
 Implement stacking upgrades
 Add prestige confirmation dialog ("Are you sure?")
 Persist prestige data across resets
 Write 20+ tests for prestige mechanics
 Document in docs/PRESTIGE_SYSTEM.md
 Update workflows.instructions.md with "How to add prestige upgrade"
Acceptance Criteria:
✅ Prestige points calculated from 5+ metrics
✅ 15+ upgrades available
✅ Upgrades persist across prestige resets
✅ Stacking upgrades work correctly
✅ UI for prestige shop
✅ All tests passing, 80%+ coverage
✅ Documentation complete

🎯 PHASE 3: TEAM DYNAMICS (Weeks 5-6)
Goal: Make specialists feel like real people with chemistry.

TASK 3.1: Enhanced Relationship System
Owner: AI Agent
Duration: 5 days
Deliverable: Dynamic team chemistry

Requirements:
Python
# Update: src/plugins/relationships_plugin.py

class RelationshipsPlugin:
    """Enhanced relationships with team synergy."""
    
    def update_relationship(
        self,
        specialist1: Specialist,
        specialist2: Specialist,
        interaction_type: str
    ):
        """
        Update relationship based on interaction.
        
        Interaction types:
        - work_together: +2 relationship (if successful)
        - work_together_failed: -1 relationship
        - mentor_junior: +5 relationship
        - compete_for_incident: -3 relationship
        """
        pass
    
    def get_team_synergy_bonus(
        self,
        specialists: List[Specialist]
    ) -> float:
        """
        Calculate team synergy bonus.
        
        Positive relationships: +5% efficiency per friendship
        Negative relationships: -10% efficiency per rivalry
        Mentor-mentee: +15% XP for mentee
        """
        pass
Relationship Tiers:
JSON
// data/relationships_config.json
{
  "tiers": [
    {
      "tier": "rivals",
      "min_value": -100,
      "max_value": -50,
      "effects": {
        "efficiency_multiplier": 0.9,
        "burnout_increase": 2,
        "description": "These specialists clash frequently"
      }
    },
    {
      "tier": "neutral",
      "min_value": -49,
      "max_value": 49,
      "effects": {
        "efficiency_multiplier": 1.0,
        "description": "Professional working relationship"
      }
    },
    {
      "tier": "friends",
      "min_value": 50,
      "max_value": 100,
      "effects": {
        "efficiency_multiplier": 1.15,
        "burnout_decrease": 2,
        "description": "These specialists work well together"
      }
    },
    {
      "tier": "best_friends",
      "min_value": 101,
      "max_value": 200,
      "effects": {
        "efficiency_multiplier": 1.25,
        "burnout_decrease": 5,
        "combo_chance": 0.1,
        "description": "Inseparable duo with incredible synergy"
      }
    }
  ]
}
Implementation Checklist:
 Update relationship calculation to 5 tiers
 Add interaction types (8+ types)
 Implement team synergy calculation
 Add mentor-mentee bonuses
 Create relationship decay over time
 Add rivalry events (personality clashes)
 Create relationship visualization UI
 Write 25+ tests for all relationship scenarios
 Document in docs/RELATIONSHIP_SYSTEM.md
Acceptance Criteria:
✅ 5 relationship tiers implemented
✅ 8+ interaction types
✅ Team synergy affects performance
✅ Mentor-mentee system works
✅ Relationships decay without interaction
✅ Visual relationship UI
✅ All tests passing, 80%+ coverage
✅ Documentation complete

TASK 3.2: Specialist Personalities
Owner: AI Agent
Duration: 3 days
Deliverable: Unique personality traits

Requirements:
Python
# Update: src/models/specialist.py

class Specialist:
    """Add personality system."""
    
    def __init__(self, ...):
        self.personality_traits = []
        self.work_style = WorkStyle.BALANCED
    
    def get_personality_modifiers(
        self,
        incident: Incident,
        team: List[Specialist]
    ) -> Dict[str, float]:
        """
        Calculate personality-based modifiers.
        
        Examples:
        - Introvert: -10% speed in teams, +20% speed alone
        - Perfectionist: +30% accuracy, -20% speed
        - Workaholic: -50% burnout rate, +10% speed
        """
        pass
Personality Traits:
JSON
// data/personality_traits.json
{
  "traits": [
    {
      "id": "introvert",
      "name": "Introvert",
      "description": "Works better alone but slower in teams",
      "rarity": "common",
      "modifiers": {
        "solo_speed_multiplier": 1.2,
        "team_speed_multiplier": 0.9,
        "burnout_rate": 1.1
      }
    },
    {
      "id": "extrovert",
      "name": "Extrovert",
      "description": "Thrives in teams but unfocused alone",
      "rarity": "common",
      "modifiers": {
        "solo_speed_multiplier": 0.9,
        "team_speed_multiplier": 1.2,
        "burnout_rate": 0.9
      }
    },
    {
      "id": "perfectionist",
      "name": "Perfectionist",
      "description": "Extremely accurate but slow and prone to burnout",
      "rarity": "uncommon",
      "modifiers": {
        "accuracy_multiplier": 1.3,
        "speed_multiplier": 0.8,
        "burnout_rate": 1.3
      }
    },
    {
      "id": "workaholic",
      "name": "Workaholic",
      "description": "Never burns out but needs therapy eventually",
      "rarity": "rare",
      "modifiers": {
        "burnout_rate": 0.5,
        "speed_multiplier": 1.1,
        "requires_therapy": true
      }
    }
  ]
}
Implementation Checklist:
 Add personality traits to Specialist model
 Create 12+ personality traits (common/uncommon/rare)
 Implement personality modifiers
 Add trait compatibility (some traits conflict)
 Generate random personalities for new specialists
 Add personality to specialist hiring UI
 Write 20+ tests for personality interactions
 Document in docs/PERSONALITY_SYSTEM.md
Acceptance Criteria:
✅ 12+ personality traits defined
✅ Traits affect specialist performance
✅ Trait rarity system (common/uncommon/rare)
✅ Traits visible in UI
✅ All tests passing
✅ Documentation complete

🎯 PHASE 4: ECONOMY & CONTRACTS (Weeks 7-8)
Goal: Make money meaningful and contracts strategic.

TASK 4.1: Advanced Contract System
Owner: AI Agent
Duration: 4 days
Deliverable: Strategic contract selection

Requirements:
Python
# Update: src/models/contract.py

class Contract:
    """Enhanced contract with negotiation and tiers."""
    
    def __init__(self, ...):
        self.tier = ContractTier.BRONZE
        self.negotiated_terms = {}
        self.performance_bonuses = []
        self.penalty_clauses = []
    
    def calculate_payout(
        self,
        incidents_resolved: int,
        sla_compliance: float
    ) -> float:
        """
        Calculate contract payout with bonuses/penalties.
        
        Base payout + performance bonuses - SLA penalties
        """
        pass
Contract Tiers:
JSON
// data/contract_tiers.json
{
  "tiers": [
    {
      "tier": "bronze",
      "name": "Bronze Contract",
      "unlock_requirement": {
        "reputation": 0
      },
      "base_payout": 5000,
      "incident_rate": 1.0,
      "difficulty_range": [1, 3],
      "sla_strictness": 0.7,
      "performance_bonus_multiplier": 1.1
    },
    {
      "tier": "silver",
      "name": "Silver Contract",
      "unlock_requirement": {
        "reputation": 100
      },
      "base_payout": 15000,
      "incident_rate": 1.5,
      "difficulty_range": [2, 4],
      "sla_strictness": 0.8,
      "performance_bonus_multiplier": 1.3
    },
    {
      "tier": "gold",
      "name": "Gold Contract",
      "unlock_requirement": {
        "reputation": 300
      },
      "base_payout": 50000,
      "incident_rate": 2.0,
      "difficulty_range": [3, 5],
      "sla_strictness": 0.95,
      "performance_bonus_multiplier": 1.5,
      "exclusive": true
    }
  ]
}
Implementation Checklist:
 Add contract tier system (Bronze/Silver/Gold/Platinum)
 Implement performance bonuses
 Add SLA penalty calculations
 Create contract selection UI
 Add contract comparison tool
 Implement exclusive contracts (can only have one)
 Write 20+ tests for contract mechanics
 Document in docs/CONTRACT_SYSTEM.md
Acceptance Criteria:
✅ 4 contract tiers implemented
✅ Performance bonuses calculated correctly
✅ SLA penalties enforced
✅ UI for contract selection
✅ Exclusive contracts work
✅ All tests passing, 80%+ coverage
✅ Documentation complete

TASK 4.2: Investment System
Owner: AI Agent
Duration: 3 days
Deliverable: Passive income diversification

Requirements:
Python
# Create: src/core/investment_system.py

class InvestmentSystem:
    """Passive income through investments."""
    
    def invest(
        self,
        game_state: GameState,
        investment_type: str,
        amount: float
    ) -> Investment:
        """
        Invest money for passive returns.
        
        Investment types:
        - low_risk: 5% annual return, safe
        - medium_risk: 15% annual return, 10% loss chance
        - high_risk: 50% annual return, 30% loss chance
        - crypto: 200% return or total loss (50/50)
        """
        pass
    
    def calculate_returns(
        self,
        investment: Investment,
        time_elapsed: float
    ) -> float:
        """Calculate investment returns over time."""
        pass
Investment Types:
JSON
// data/investments.json
{
  "types": [
    {
      "id": "low_risk_bonds",
      "name": "Government Bonds",
      "risk": "low",
      "min_investment": 10000,
      "annual_return_rate": 0.05,
      "loss_chance": 0.0,
      "description": "Safe but slow growth"
    },
    {
      "id": "index_funds",
      "name": "Index Funds",
      "risk": "medium",
      "min_investment": 25000,
      "annual_return_rate": 0.15,
      "loss_chance": 0.1,
      "description": "Balanced risk/reward"
    },
    {
      "id": "crypto",
      "name": "Cryptocurrency",
      "risk": "very_high",
      "min_investment": 5000,
      "win_return_rate": 2.0,
      "loss_chance": 0.5,
      "description": "Moon or broke"
    }
  ]
}
Implementation Checklist:
 Create InvestmentSystem class
 Define 5 investment types (low/medium/high/crypto/real_estate)
 Implement return calculation (time-based)
 Add random loss events
 Create investment UI panel
 Add portfolio visualization
 Write 15+ tests for investment mechanics
 Document in docs/INVESTMENT_SYSTEM.md
Acceptance Criteria:
✅ 5 investment types available
✅ Returns calculated over time
✅ Loss events trigger randomly
✅ Investment UI panel
✅ Portfolio tracking
✅ All tests passing
✅ Documentation complete

🎯 PHASE 5: UI/UX POLISH (Weeks 9-10)
Goal: Make the game feel AAA-quality despite being indie.

TASK 5.1: Animation System
Owner: AI Agent
Duration: 4 days
Deliverable: Smooth animations everywhere

Requirements:
Python
# Create: src/ui/animation_system.py

class AnimationSystem:
    """Easing and animation framework."""
    
    def animate(
        self,
        target: Any,
        property: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: EasingFunction = EasingFunction.EASE_IN_OUT
    ) -> Animation:
        """
        Animate property from start to end.
        
        Easing functions:
        - LINEAR
        - EASE_IN
        - EASE_OUT
        - EASE_IN_OUT
        - BOUNCE
        - ELASTIC
        """
        pass
Animations to Add:
 Panel slide-in/slide-out
 Fade transitions between views
 Number count-up (money, XP)
 Progress bar fill animations
 Button press feedback (squash/stretch)
 Notification slide + fade
 Incident card shake (urgent)
 Specialist glow (level up)
 Smooth scrolling
 Modal dialog zoom in/out
Implementation Checklist:
 Create animation framework with easing
 Implement 6 easing functions
 Add animations to all UI transitions
 Add particle effects (sparkles, explosions)
 Implement screen shake on SLA failure
 Add hover animations
 Write 10+ tests for animation system
 Document in docs/ANIMATION_SYSTEM.md
Acceptance Criteria:
✅ Smooth animations on all transitions
✅ 6 easing functions implemented
✅ Particle effects for key events
✅ No performance degradation
✅ All tests passing
✅ Documentation complete

TASK 5.2: Tutorial System
Owner: AI Agent
Duration: 3 days
Deliverable: Guided onboarding for new players

Requirements:
Python
# Create: src/core/tutorial_system.py

class TutorialSystem:
    """Step-by-step tutorial for new players."""
    
    def __init__(self):
        self.current_step = 0
        self.completed_steps = []
    
    def check_step_completion(
        self,
        game_state: GameState
    ) -> bool:
        """
        Check if current step completed.
        
        Example steps:
        1. Assign your first incident
        2. Wait for specialist to resolve
        3. Collect your reward
        4. Level up specialist
        5. Unlock automation
        """
        pass
Tutorial Steps:
JSON
// data/tutorial_steps.json
{
  "steps": [
    {
      "id": "welcome",
      "title": "Welcome to Cybersecurity Firm!",
      "description": "You're the CEO of a security incident response firm.",
      "highlight": null,
      "completion_condition": "click_continue"
    },
    {
      "id": "assign_incident",
      "title": "Assign Your First Incident",
      "description": "Click a specialist, then click an incident, then click Assign.",
      "highlight": "incident_queue_panel",
      "completion_condition": "incident_assigned"
    },
    {
      "id": "wait_resolution",
      "title": "Wait for Resolution",
      "description": "Your specialist is working on the incident. You can speed up time!",
      "highlight": "speed_controls",
      "completion_condition": "incident_resolved"
    }
  ]
}
Implementation Checklist:
 Create TutorialSystem class
 Define 10 tutorial steps
 Add highlight overlays
 Implement step completion detection
 Add skip tutorial option
 Create tutorial UI overlay
 Write 10+ tests for tutorial flow
 Document in docs/TUTORIAL_SYSTEM.md
Acceptance Criteria:
✅ 10 tutorial steps defined
✅ Highlight overlays work
✅ Completion detection works
✅ Can skip tutorial
✅ All tests passing
✅ Documentation complete

🎯 PHASE 6: ENDGAME & REPLAYABILITY (Weeks 11-12)
Goal: Give players a reason to keep playing after 100 hours.

TASK 6.1: Achievements System Enhancement
Owner: AI Agent
Duration: 3 days
Deliverable: 100+ achievements across 10 categories

Achievement Categories:
JSON
// data/achievements.json (expand)
{
  "categories": [
    "progression",
    "efficiency",
    "wealth",
    "speed",
    "specialist_mastery",
    "relationship",
    "automation",
    "prestige",
    "collection",
    "secret"
  ],
  "achievements": [
    {
      "id": "first_million",
      "category": "wealth",
      "name": "First Million",
      "description": "Earn $1,000,000 total",
      "hidden": false,
      "requirement": {
        "type": "total_money_earned",
        "value": 1000000
      },
      "rewards": {
        "prestige_points": 10,
        "title": "Millionaire"
      }
    }
  ]
}
Implementation Checklist:
 Expand to 100+ achievements
 Add 10 categories
 Implement secret achievements
 Add achievement notifications
 Create achievements UI panel
 Add achievement progress tracking
 Write tests for achievement logic
 Document in docs/ACHIEVEMENT_SYSTEM.md
TASK 6.2: Leaderboards
Owner: AI Agent
Duration: 4 days
Deliverable: Competitive rankings

Leaderboard Types:
JSON
// data/leaderboards.json
{
  "leaderboards": [
    {
      "id": "total_money",
      "name": "Richest Firms",
      "metric": "total_money_earned",
      "reset": "never"
    },
    {
      "id": "speedrun",
      "name": "Fastest to $1M",
      "metric": "time_to_first_million",
      "reset": "weekly"
    },
    {
      "id": "prestige",
      "name": "Prestige Masters",
      "metric": "prestige_level",
      "reset": "never"
    }
  ]
}
Implementation Checklist:
 Create leaderboard backend API
 Implement 5+ leaderboard types
 Add weekly/monthly/all-time rankings
 Create leaderboard UI panel
 Add player rank display
 Write tests for leaderboard logic
 Document in docs/LEADERBOARD_SYSTEM.md
📊 CRITICAL SUCCESS METRICS
Must Achieve Before v1.0:
 Playability: Player can play 2+ hours without getting bored
 Progression: Clear sense of advancement (level 1 → 20 → prestige)
 Automation: Manual → automated workflow feels natural
 Replayability: Prestige system makes players want to reset
 Polish: No game-breaking bugs, smooth animations
 Performance: 60 FPS on mid-tier hardware
 Documentation: Every system documented
 Test Coverage: 80%+ across all systems
Quality Gates:
Before merging any feature:

✅ All 15 standards met (see core-standards.instructions.md)
✅ 80%+ test coverage
✅ Documentation updated
✅ No performance regression
✅ Playtested for 30+ minutes
📝 DOCUMENTATION REQUIREMENTS
For Every Feature:
Feature Doc → docs/FEATURE_NAME.md

What it does
How to use it
JSON configuration
Code examples
Instruction Update → .github/instructions/*.md

If new pattern → update relevant instruction file
If new workflow → add to workflows.instructions.md
Progress Update → docs/PROGRESS.md

Mark task complete
Note any breaking changes
Code Comments

High-level docstrings only
Explain WHY, not WHAT
🚀 EXECUTION STRATEGY
Week-by-Week Breakdown:
Week 1: Resolution System + Automation Builder
Week 2: Difficulty Curve + Skill Trees
Week 3: Dual-Class + Prestige Overhaul
Week 4: Relationships + Personalities
Week 5: Advanced Contracts + Investments
Week 6: Buffer week for polish
Week 7: Animation System
Week 8: Tutorial System
Week 9: Achievements Enhancement
Week 10: Leaderboards
Week 11: Integration testing + bug fixes
Week 12: Polish + playtest + prepare launch

Parallel Work Strategy:
AI Agent 1: Core systems (resolution, automation, progression)
AI Agent 2: UI/UX (animations, tutorials, panels)
AI Agent 3: Content (achievements, contracts, skill trees)
Human: Architecture review, playtesting, integration
🎯 FINAL DELIVERABLE CHECKLIST
v1.0 Launch Requirements:
Core Gameplay:

 Decision-based incident resolution (5 decision trees)
 Automation builder (10+ rule types)
 Progressive difficulty (smooth 0-60 min curve)
 Specialist skill trees (30+ skills)
 Dual-class system (6 hybrids)
 Prestige system (15+ upgrades)
Team Dynamics:

 Relationship system (5 tiers)
 Personality traits (12+ traits)
 Team synergy bonuses
Economy:

 Contract tiers (4 tiers)
 Investment system (5 types)
 Balanced economy
UI/UX:

 Smooth animations
 Tutorial system (10 steps)
 Polished panels
Endgame:

 100+ achievements
 Leaderboards (5 types)
 Prestige replayability
Technical:

 80%+ test coverage
 60 FPS performance
 Save/load works
 No game-breaking bugs
Documentation:

 All systems documented
 Instruction files updated
 API reference complete
🔥 THIS IS THE PLAN. EXECUTE IT.
For AI Agents:

Follow this plan exactly
Update docs as you go
Test everything
Ask before deviating
For Human:

Review PRs against this plan
Playtest weekly
Adjust priorities as needed
Celebrate wins
Let's build something legendary. 🚀🔒
