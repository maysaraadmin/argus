#!/usr/bin/env python3
"""
Pydantic data models for Argus MVP
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum


class EntityType(str, Enum):
    """Supported entity types"""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    EVENT = "event"
    DOCUMENT = "document"
    ASSET = "asset"
    UNKNOWN = "unknown"


class RelationshipType(str, Enum):
    """Supported relationship types"""
    WORKS_WITH = "works_with"
    MEMBER_OF = "member_of"
    LOCATED_IN = "located_in"
    RELATED_TO = "related_to"
    KNOWS = "knows"
    OWNS = "owns"
    PARTICIPATED_IN = "participated_in"
    CREATED_BY = "created_by"
    CONNECTED_TO = "connected_to"


class EntityBase(BaseModel):
    """Base entity model"""
    type: EntityType
    name: str = Field(..., min_length=1, max_length=255)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    source: str = Field(default="manual", max_length=100)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    
    @validator('attributes')
    def validate_attributes(cls, v):
        """Validate attributes dictionary"""
        if not isinstance(v, dict):
            raise ValueError("Attributes must be a dictionary")
        return v
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Validate confidence score"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class EntityCreate(EntityBase):
    """Model for creating entities"""
    id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "type": "person",
                "name": "John Smith",
                "attributes": {
                    "age": 35,
                    "nationality": "US",
                    "email": "john.smith@example.com"
                },
                "source": "csv_import",
                "confidence": 0.9
            }
        }


class EntityUpdate(BaseModel):
    """Model for updating entities"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    attributes: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class EntityResponse(EntityBase):
    """Model for entity responses"""
    id: str
    degree: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "entity_123",
                "type": "person",
                "name": "John Smith",
                "attributes": {
                    "age": 35,
                    "nationality": "US"
                },
                "source": "csv_import",
                "confidence": 0.9,
                "degree": 3,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class RelationshipBase(BaseModel):
    """Base relationship model"""
    source_id: str
    target_id: str
    type: RelationshipType
    attributes: Dict[str, Any] = Field(default_factory=dict)
    strength: float = Field(default=1.0, ge=0.0, le=1.0)
    
    @validator('strength')
    def validate_strength(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Strength must be between 0.0 and 1.0")
        return v


class RelationshipCreate(RelationshipBase):
    """Model for creating relationships"""
    
    class Config:
        schema_extra = {
            "example": {
                "source_id": "entity_123",
                "target_id": "entity_456",
                "type": "works_with",
                "attributes": {
                    "since": "2020",
                    "department": "engineering"
                },
                "strength": 0.8
            }
        }


class RelationshipResponse(RelationshipBase):
    """Model for relationship responses"""
    id: str
    created_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": "rel_789",
                "source_id": "entity_123",
                "target_id": "entity_456",
                "type": "works_with",
                "attributes": {
                    "since": "2020"
                },
                "strength": 0.8,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class SearchQuery(BaseModel):
    """Model for search queries"""
    query: str = Field(..., min_length=1, max_length=500)
    entity_type: Optional[EntityType] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    fuzzy: bool = Field(default=True)
    
    class Config:
        schema_extra = {
            "example": {
                "query": "John Smith",
                "entity_type": "person",
                "filters": {
                    "age": {"min": 30, "max": 50},
                    "nationality": "US"
                },
                "limit": 100,
                "fuzzy": True
            }
        }


class MatchRequest(BaseModel):
    """Model for entity resolution requests"""
    entities: List[Dict[str, Any]] = Field(..., min_items=2)
    entity_type: Optional[EntityType] = None
    threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    @validator('entities')
    def validate_entities(cls, v):
        if len(v) < 2:
            raise ValueError("At least 2 entities required for resolution")
        return v


class MatchResponse(BaseModel):
    """Model for entity resolution responses"""
    entity1_id: str
    entity2_id: str
    similarity_score: float
    match_type: str
    confidence: float
    match_details: Dict[str, Any]


class GraphResponse(BaseModel):
    """Model for graph visualization responses"""
    nodes: List[Dict[str, Any]]
    links: List[Dict[str, Any]]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PathRequest(BaseModel):
    """Model for path finding requests"""
    source_id: str
    target_id: str
    max_depth: int = Field(default=3, ge=1, le=10)
    path_type: str = Field(default="shortest", pattern="^(shortest|all)$")


class PathResponse(BaseModel):
    """Model for path finding responses"""
    paths: List[List[str]]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NetworkRequest(BaseModel):
    """Model for network requests"""
    entity_id: str
    depth: int = Field(default=2, ge=1, le=5)
    include_attributes: bool = Field(default=True)
    node_limit: int = Field(default=100, ge=1, le=1000)


class StatsResponse(BaseModel):
    """Model for statistics responses"""
    nodes: int
    edges: int
    entity_types: Dict[str, int]
    density: float
    connected_components: int
    avg_clustering: float
    avg_path_length: Optional[float] = None


class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "error": {
                    "code": "ENTITY_NOT_FOUND",
                    "message": "Entity with ID '123' not found",
                    "details": {
                        "entity_id": "123",
                        "suggestions": ["124", "125"]
                    },
                    "request_id": "req_abc123",
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            }
        }


class PaginatedResponse(BaseModel):
    """Model for paginated responses"""
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
    
    @validator('pages')
    def calculate_pages(cls, v, values):
        total = values.get('total', 0)
        per_page = values.get('per_page', 1)
        return (total + per_page - 1) // per_page if per_page > 0 else 0


class ImportRequest(BaseModel):
    """Model for data import requests"""
    file_type: str = Field(..., pattern="^(csv|json|excel)$")
    options: Dict[str, Any] = Field(default_factory=dict)
    entity_type: Optional[EntityType] = None
    source: str = Field(default="import", max_length=100)


class ImportResponse(BaseModel):
    """Model for data import responses"""
    entities_imported: int
    relationships_created: int
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    processing_time: float


class ExportRequest(BaseModel):
    """Model for data export requests"""
    format: str = Field(..., pattern="^(json|csv|gexf|graphml)$")
    entity_type: Optional[EntityType] = None
    include_relationships: bool = Field(default=True)
    filters: Dict[str, Any] = Field(default_factory=dict)


class BulkOperation(BaseModel):
    """Model for bulk operations"""
    operation: str = Field(..., pattern="^(create|update|delete)$")
    entities: List[Union[EntityCreate, EntityUpdate]]
    options: Dict[str, Any] = Field(default_factory=dict)


class BulkResponse(BaseModel):
    """Model for bulk operation responses"""
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    operation_ids: List[str] = Field(default_factory=list)