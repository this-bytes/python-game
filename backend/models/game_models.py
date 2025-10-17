"""Pydantic models for game entities.

These models provide validation and type safety for API requests/responses.
"""
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from datetime import datetime


class SpecialistStats(BaseModel):
    """Specialist stats model."""
    speed: int = Field(ge=0, le=100)
    accuracy: int = Field(ge=0, le=100)
    experience_bonus: float = Field(ge=1.0)


class SpecialistUpdate(BaseModel):
    """Model for updating specialist data."""
    name: Optional[str] = None
    level: Optional[int] = Field(None, ge=1)
    xp: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None


class IncidentSpawn(BaseModel):
    """Model for spawning incidents."""
    incident_type: Optional[str] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    client_id: Optional[str] = None


class BatchSpawn(BaseModel):
    """Model for batch spawning incidents."""
    count: int = Field(ge=1, le=100, default=10)
    incident_type: Optional[str] = None
    difficulty_range: Optional[tuple[int, int]] = None


class MoneyAdjustment(BaseModel):
    """Model for adjusting money."""
    amount: float = Field(ge=0)
    reason: Optional[str] = "Admin adjustment"


class TimeControl(BaseModel):
    """Model for time control operations."""
    speed: Optional[float] = Field(None, ge=0.1, le=10.0)
    seconds: Optional[int] = Field(None, ge=1)


class ConfigUpdate(BaseModel):
    """Model for configuration updates."""
    file_name: str
    content: Dict[str, Any]


class FeatureFlag(BaseModel):
    """Model for feature flags."""
    name: str
    enabled: bool
    description: Optional[str] = None
    rollout_percentage: Optional[int] = Field(None, ge=0, le=100)


class EventSchedule(BaseModel):
    """Model for scheduling live events."""
    event_type: str
    schedule_time: datetime
    parameters: Optional[Dict[str, Any]] = None
    repeat_interval: Optional[int] = None


class GodModeCommand(BaseModel):
    """Model for god mode commands."""
    command: str
    parameters: Optional[Dict[str, Any]] = None


class ClientUpdate(BaseModel):
    """Model for updating client data."""
    incident_rate_per_minute: Optional[float] = Field(None, ge=0)
    sla_multiplier: Optional[float] = Field(None, ge=0)
    reputation: Optional[int] = Field(None, ge=0, le=100)
    contract_value: Optional[int] = Field(None, ge=0)


class SaveSlot(BaseModel):
    """Model for save operations."""
    slot: int = Field(ge=1, le=10)
    name: Optional[str] = None


class AnalyticsQuery(BaseModel):
    """Model for analytics queries."""
    metric: str
    time_range: Optional[str] = "24h"
    group_by: Optional[str] = None
