"""
Historical data models for Argus history study module.
Extends base models with history-specific attributes and relationships.
"""

from datetime import date, datetime
from typing import List, Dict, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class PeriodType(str, Enum):
    """Types of historical periods"""
    ANCIENT = "ancient"
    CLASSICAL = "classical"
    MEDIEVAL = "medieval"
    RENAISSANCE = "renaissance"
    MODERN = "modern"
    CONTEMPORARY = "contemporary"


class EventType(str, Enum):
    """Types of historical events"""
    POLITICAL = "political"
    MILITARY = "military"
    SOCIAL = "social"
    ECONOMIC = "economic"
    CULTURAL = "cultural"
    RELIGIOUS = "religious"
    SCIENTIFIC = "scientific"
    TECHNOLOGICAL = "technological"


class HistoricalPeriod(BaseModel):
    """Historical time period"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    start_date: date
    end_date: Optional[date] = None
    period_type: PeriodType
    region: str
    key_characteristics: List[str] = []
    related_periods: List[str] = []
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }


class HistoricalEvent(BaseModel):
    """Historical event with temporal and spatial attributes"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    event_type: EventType
    date: Union[date, datetime]
    end_date: Optional[Union[date, datetime]] = None
    location: str
    coordinates: Optional[tuple] = None  # (lat, lon)
    participants: List[str] = []  # Entity IDs
    causes: List[str] = []  # Event IDs
    consequences: List[str] = []  # Event IDs
    sources: List[str] = []  # Source references
    significance: str = ""
    tags: List[str] = []
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class HistoricalFigure(BaseModel):
    """Historical person/figure"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    birth_place: Optional[str] = None
    death_place: Optional[str] = None
    occupation: List[str] = []
    achievements: List[str] = []
    relationships: Dict[str, str] = {}  # relationship_type -> entity_id
    affiliations: List[str] = []  # Organization IDs
    era: str
    biography: str = ""
    portrait_url: Optional[str] = None
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }


class HistoricalOrganization(BaseModel):
    """Historical organization (kingdom, empire, institution, etc.)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    organization_type: str  # empire, kingdom, church, guild, etc.
    founded_date: Optional[date] = None
    dissolved_date: Optional[date] = None
    headquarters: Optional[str] = None
    territory: List[str] = []  # Geographic regions
    leaders: List[str] = []  # Person IDs
    achievements: List[str] = []
    conflicts: List[str] = []  # Event IDs
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }


class HistoricalSource(BaseModel):
    """Historical source/document"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    author: Optional[str] = None
    date_created: Optional[Union[date, datetime]] = None
    source_type: str  # primary, secondary, tertiary
    medium: str  # text, artifact, oral, etc.
    language: str
    location: str  # Where it's stored/archived
    reliability_score: float = Field(ge=0.0, le=1.0)
    summary: str = ""
    full_text: Optional[str] = None
    related_events: List[str] = []
    related_figures: List[str] = []
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class Timeline(BaseModel):
    """Historical timeline"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    start_date: date
    end_date: date
    events: List[str] = []  # Event IDs
    periods: List[str] = []  # Period IDs
    focus: str = ""  # Theme or focus area
    created_by: str
    is_public: bool = False
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }


class HistoricalConnection(BaseModel):
    """Relationship between historical entities"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_entity: str
    target_entity: str
    relationship_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    context: str = ""
    sources: List[str] = []
    strength: float = Field(ge=0.0, le=1.0)
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }


class HistoryStudySession(BaseModel):
    """Study session for historical analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    timeline_id: str
    focus_entities: List[str] = []
    research_questions: List[str] = []
    notes: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
