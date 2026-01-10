#!/usr/bin/env python3
"""
Custom exceptions for Argus MVP
"""
from typing import Optional, Dict, Any


class ArgusException(Exception):
    """Base exception for all Argus errors"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format"""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details
            }
        }


class ValidationError(ArgusException):
    """Raised when data validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        super().__init__(message, "VALIDATION_ERROR", details)


class EntityNotFoundError(ArgusException):
    """Raised when an entity is not found"""
    
    def __init__(self, entity_id: str):
        super().__init__(
            f"Entity with ID '{entity_id}' not found",
            "ENTITY_NOT_FOUND",
            {"entity_id": entity_id}
        )


class DuplicateEntityError(ArgusException):
    """Raised when trying to create a duplicate entity"""
    
    def __init__(self, entity_id: str, existing_id: Optional[str] = None):
        details = {"entity_id": entity_id}
        if existing_id:
            details["existing_id"] = existing_id
        super().__init__(
            f"Entity '{entity_id}' already exists",
            "DUPLICATE_ENTITY",
            details
        )


class GraphError(ArgusException):
    """Raised when graph operations fail"""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        details = {}
        if operation:
            details["operation"] = operation
        super().__init__(message, "GRAPH_ERROR", details)


class RelationshipError(ArgusException):
    """Raised when relationship operations fail"""
    
    def __init__(self, message: str, source_id: Optional[str] = None, target_id: Optional[str] = None):
        details = {}
        if source_id:
            details["source_id"] = source_id
        if target_id:
            details["target_id"] = target_id
        super().__init__(message, "RELATIONSHIP_ERROR", details)


class EntityResolutionError(ArgusException):
    """Raised when entity resolution fails"""
    
    def __init__(self, message: str, stage: Optional[str] = None):
        details = {}
        if stage:
            details["stage"] = stage
        super().__init__(message, "ENTITY_RESOLUTION_ERROR", details)


class ImportError(ArgusException):
    """Raised when data import fails"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, line_number: Optional[int] = None):
        details = {}
        if file_path:
            details["file_path"] = file_path
        if line_number:
            details["line_number"] = line_number
        super().__init__(message, "IMPORT_ERROR", details)


class ExportError(ArgusException):
    """Raised when data export fails"""
    
    def __init__(self, message: str, format: Optional[str] = None):
        details = {}
        if format:
            details["format"] = format
        super().__init__(message, "EXPORT_ERROR", details)


class SearchError(ArgusException):
    """Raised when search operations fail"""
    
    def __init__(self, message: str, query: Optional[str] = None):
        details = {}
        if query:
            details["query"] = query
        super().__init__(message, "SEARCH_ERROR", details)


class ConfigurationError(ArgusException):
    """Raised when configuration is invalid"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, "CONFIGURATION_ERROR", details)


class AuthenticationError(ArgusException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(ArgusException):
    """Raised when authorization fails"""
    
    def __init__(self, message: str, resource: Optional[str] = None, action: Optional[str] = None):
        details = {}
        if resource:
            details["resource"] = resource
        if action:
            details["action"] = action
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class CacheError(ArgusException):
    """Raised when cache operations fail"""
    
    def __init__(self, message: str, cache_key: Optional[str] = None):
        details = {}
        if cache_key:
            details["cache_key"] = cache_key
        super().__init__(message, "CACHE_ERROR", details)


class DatabaseError(ArgusException):
    """Raised when database operations fail"""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        details = {}
        if operation:
            details["operation"] = operation
        super().__init__(message, "DATABASE_ERROR", details)


class APIError(ArgusException):
    """Raised when API operations fail"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, endpoint: Optional[str] = None):
        details = {}
        if status_code:
            details["status_code"] = status_code
        if endpoint:
            details["endpoint"] = endpoint
        super().__init__(message, "API_ERROR", details)
