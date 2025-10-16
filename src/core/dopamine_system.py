"""Dopamine System - Inject addictive mechanics into core gameplay loop.

This system adds instant gratification, risk/reward decisions, combo systems,
and meaningful progression feedback to transform boring clicking into strategic, 
rewarding gameplay.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import time
import random


class RewardTier(Enum):
    """Visual/audio feedback intensity for rewards."""
    MINOR = "minor"  # Small particle burst, subtle sound
    STANDARD = "standard"  # Normal celebration
    MAJOR = "major"  # Big explosion, fanfare
    EPIC = "epic"  # Screen shake, epic celebration


@dataclass
class ComboState:
    """Tracks player combo chains for multiplier bonuses."""
    current_combo: int = 0
    max_combo: int = 0
    combo_timer: float = 0.0
    combo_timeout: float = 10.0  # Seconds before combo breaks
    last_action_time: float = 0.0
    
    # Combo multipliers
    multiplier_thresholds: Dict[int, float] = field(default_factory=lambda: {
        3: 1.2,   # 3 combo = 1.2x rewards
        5: 1.5,   # 5 combo = 1.5x rewards
        10: 2.0,  # 10 combo = 2x rewards
        20: 3.0,  # 20 combo = 3x rewards
        50: 5.0   # 50 combo = 5x rewards
    })
    
    def get_multiplier(self) -> float:
        """Get current combo multiplier."""
        multiplier = 1.0
        for threshold in sorted(self.multiplier_thresholds.keys()):
            if self.current_combo >= threshold:
                multiplier = self.multiplier_thresholds[threshold]
        return multiplier
    
    def add_action(self) -> Tuple[int, float, bool]:
        """Register an action, update combo.
        
        Returns:
            (combo_count, multiplier, is_combo_milestone)
        """
        current_time = time.time()
        
        # Check if combo expired
        if current_time - self.last_action_time > self.combo_timeout:
            self.current_combo = 0
        
        self.current_combo += 1
        self.last_action_time = current_time
        
        if self.current_combo > self.max_combo:
            self.max_combo = self.current_combo
        
        multiplier = self.get_multiplier()
        
        # Check if hit milestone (new multiplier tier)
        is_milestone = self.current_combo in self.multiplier_thresholds
        
        return (self.current_combo, multiplier, is_milestone)
    
    def break_combo(self):
        """Break the current combo."""
        self.current_combo = 0


@dataclass
class RiskRewardContract:
    """Special high-risk, high-reward incident modifications."""
    contract_type: str  # "overload", "critical", "perfect_only", "speed_run"
    reward_multiplier: float  # Reward boost
    failure_penalty: float  # Penalty if failed
    description: str
    icon: str = "⚡"


class DopamineSystem:
    """System that injects addictive gameplay mechanics."""
    
    def __init__(self):
        self.combo_state = ComboState()
        self.session_stats = {
            "total_combos": 0,
            "max_combo_session": 0,
            "risk_contracts_accepted": 0,
            "risk_contracts_succeeded": 0,
            "perfect_completions": 0,
            "epic_rewards_earned": 0
        }
        
        # Risk/reward contract templates
        self.risk_contracts = {
            "overload": RiskRewardContract(
                contract_type="overload",
                reward_multiplier=2.5,
                failure_penalty=1.5,
                description="2.5x reward, but 1.5x penalty if failed!",
                icon="⚡"
            ),
            "critical": RiskRewardContract(
                contract_type="critical",
                reward_multiplier=3.0,
                failure_penalty=2.0,
                description="3x reward! But double penalty if failed!",
                icon="🔥"
            ),
            "perfect_only": RiskRewardContract(
                contract_type="perfect_only",
                reward_multiplier=4.0,
                failure_penalty=3.0,
                description="4x reward for PERFECT completion! Huge penalty if not!",
                icon="💎"
            ),
            "speed_run": RiskRewardContract(
                contract_type="speed_run",
                reward_multiplier=2.0,
                failure_penalty=0.5,
                description="2x reward if completed in 25% of SLA time!",
                icon="⚡"
            )
        }
    
    def register_incident_assignment(self, incident, specialist) -> Dict:
        """Register incident assignment for combo tracking.
        
        Returns:
            Feedback dict with visual/audio cues
        """
        combo, multiplier, is_milestone = self.combo_state.add_action()
        
        feedback = {
            "combo_count": combo,
            "multiplier": multiplier,
            "is_milestone": is_milestone,
            "reward_tier": self._determine_reward_tier(combo, is_milestone),
            "message": self._generate_combo_message(combo, multiplier, is_milestone)
        }
        
        if is_milestone:
            self.session_stats["total_combos"] += 1
        
        if combo > self.session_stats["max_combo_session"]:
            self.session_stats["max_combo_session"] = combo
        
        return feedback
    
    def register_incident_completion(self, incident, specialist, success: bool, 
                                     is_sla_met: bool) -> Dict:
        """Register incident completion for reward calculation and feedback.
        
        Returns:
            Feedback dict with rewards, visual/audio cues
        """
        base_reward = incident.base_reward
        base_xp = incident.xp_reward
        
        # Apply combo multiplier
        multiplier = self.combo_state.get_multiplier()
        final_reward = int(base_reward * multiplier)
        final_xp = int(base_xp * multiplier)
        
        # Check for perfect completion (fast + successful)
        is_perfect = False
        if success and is_sla_met and hasattr(incident, 'completion_time'):
            time_used = incident.completion_time - incident.spawn_time
            if time_used < (incident.sla_seconds * 0.25):
                is_perfect = True
                final_reward = int(final_reward * 1.5)  # Extra bonus
                final_xp = int(final_xp * 1.5)
                self.session_stats["perfect_completions"] += 1
        
        # Determine reward tier for visual feedback
        if is_perfect:
            reward_tier = RewardTier.EPIC
        elif multiplier >= 3.0:
            reward_tier = RewardTier.MAJOR
        elif multiplier >= 1.5:
            reward_tier = RewardTier.STANDARD
        else:
            reward_tier = RewardTier.MINOR
        
        feedback = {
            "final_reward": final_reward,
            "final_xp": final_xp,
            "multiplier": multiplier,
            "is_perfect": is_perfect,
            "reward_tier": reward_tier,
            "message": self._generate_completion_message(final_reward, multiplier, is_perfect),
            "combo_count": self.combo_state.current_combo
        }
        
        # Break combo if failed
        if not success:
            self.combo_state.break_combo()
            feedback["combo_broken"] = True
        
        return feedback
    
    def offer_risk_contract(self, incident, difficulty: int) -> Optional[RiskRewardContract]:
        """Randomly offer a risk/reward contract for an incident.
        
        Higher difficulty = higher chance of risk contract offer.
        
        Returns:
            RiskRewardContract if offered, None otherwise
        """
        # Validate difficulty is an integer
        try:
            difficulty = int(difficulty)
        except (TypeError, ValueError):
            return None  # Can't offer contract if difficulty is invalid
        
        # Ensure self.risk_contracts is initialized
        if not hasattr(self, 'risk_contracts') or not self.risk_contracts:
            return None
        
        # Chance increases with difficulty
        offer_chance = difficulty * 0.15  # 15%, 30%, 45%, 60%, 75%
        
        if random.random() < offer_chance:
            # Weight by difficulty - harder incidents get harder contracts
            if difficulty >= 4:
                contract_types = ["critical", "perfect_only", "overload"]
            elif difficulty >= 3:
                contract_types = ["overload", "critical", "speed_run"]
            else:
                contract_types = ["overload", "speed_run"]
            
            try:
                contract_type = random.choice(contract_types)
                # Make sure contract_type is a string and exists in risk_contracts
                if isinstance(contract_type, str) and contract_type in self.risk_contracts:
                    return self.risk_contracts[contract_type]
            except (KeyError, TypeError):
                pass  # Silently fail if lookup fails
        
        return None
    
    def apply_risk_contract(self, incident, contract: RiskRewardContract):
        """Apply risk contract modifiers to an incident."""
        # Store original values
        incident.original_base_reward = incident.base_reward
        incident.risk_contract = contract.contract_type
        
        # Modify incident for display
        incident.base_reward = int(incident.base_reward * contract.reward_multiplier)
        incident.risk_multiplier = contract.reward_multiplier
        incident.risk_penalty = contract.failure_penalty
        incident.risk_description = contract.description
        incident.risk_icon = contract.icon
        
        self.session_stats["risk_contracts_accepted"] += 1
    
    def calculate_risk_reward(self, incident, success: bool, is_sla_met: bool) -> int:
        """Calculate final reward for risk contract.
        
        Returns:
            Final reward (or penalty if failed)
        """
        if not hasattr(incident, 'risk_contract'):
            return incident.base_reward
        
        contract = self.risk_contracts[incident.risk_contract]
        base = incident.original_base_reward
        
        if success:
            # Check speed_run special condition
            if contract.contract_type == "speed_run":
                if hasattr(incident, 'completion_time'):
                    time_used = incident.completion_time - incident.spawn_time
                    if time_used < (incident.sla_seconds * 0.25):
                        reward = int(base * contract.reward_multiplier)
                        self.session_stats["risk_contracts_succeeded"] += 1
                        return reward
                # Speed run failed - return base reward
                return base
            
            # Check perfect_only special condition
            if contract.contract_type == "perfect_only":
                if is_sla_met and hasattr(incident, 'completion_time'):
                    time_used = incident.completion_time - incident.spawn_time
                    if time_used < (incident.sla_seconds * 0.5):
                        reward = int(base * contract.reward_multiplier)
                        self.session_stats["risk_contracts_succeeded"] += 1
                        return reward
                # Not perfect - apply penalty
                return -int(base * contract.failure_penalty)
            
            # Standard success
            reward = int(base * contract.reward_multiplier)
            self.session_stats["risk_contracts_succeeded"] += 1
            return reward
        else:
            # Failed - apply penalty
            return -int(base * contract.failure_penalty)
    
    def _determine_reward_tier(self, combo: int, is_milestone: bool) -> RewardTier:
        """Determine visual reward tier based on combo."""
        if is_milestone and combo >= 20:
            return RewardTier.EPIC
        elif is_milestone and combo >= 10:
            return RewardTier.MAJOR
        elif is_milestone:
            return RewardTier.STANDARD
        else:
            return RewardTier.MINOR
    
    def _generate_combo_message(self, combo: int, multiplier: float, is_milestone: bool) -> str:
        """Generate exciting combo message."""
        if is_milestone:
            if combo >= 50:
                return f"🔥 LEGENDARY {combo}X COMBO! {multiplier}x REWARDS! 🔥"
            elif combo >= 20:
                return f"⚡ MEGA {combo}X COMBO! {multiplier}x REWARDS! ⚡"
            elif combo >= 10:
                return f"💥 SUPER {combo}X COMBO! {multiplier}x REWARDS!"
            elif combo >= 5:
                return f"✨ COMBO x{combo}! {multiplier}x REWARDS!"
            else:
                return f"Combo x{combo}! {multiplier}x rewards"
        else:
            return f"Combo x{combo}"
    
    def _generate_completion_message(self, reward: int, multiplier: float, is_perfect: bool) -> str:
        """Generate exciting completion message."""
        if is_perfect:
            return f"💎 PERFECT! +${reward:,.0f} ({multiplier}x combo bonus)"
        elif multiplier >= 3.0:
            return f"🔥 AMAZING! +${reward:,.0f} ({multiplier}x combo!)"
        elif multiplier >= 1.5:
            return f"⚡ GREAT! +${reward:,.0f} ({multiplier}x combo)"
        else:
            return f"+${reward:,.0f}"
    
    def get_combo_display_color(self, combo: int) -> tuple:
        """Get color for combo counter based on tier."""
        if combo >= 50:
            return (255, 50, 255)  # Epic purple
        elif combo >= 20:
            return (255, 100, 0)  # Mega orange
        elif combo >= 10:
            return (255, 200, 0)  # Super yellow
        elif combo >= 5:
            return (0, 255, 200)  # Combo cyan
        elif combo >= 3:
            return (0, 255, 100)  # Active green
        else:
            return (200, 200, 200)  # Normal gray
    
    def update(self, delta_time: float):
        """Update combo timer and check for expiration."""
        current_time = time.time()
        if self.combo_state.current_combo > 0:
            if current_time - self.combo_state.last_action_time > self.combo_state.combo_timeout:
                self.combo_state.break_combo()
