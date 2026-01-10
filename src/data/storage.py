#!/usr/bin/env python3
"""
Data persistence layer for Argus MVP
"""
import json
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
from abc import ABC, abstractmethod

from argus.config import config
from argus.logging import get_logger
from argus.exceptions import DatabaseError, ValidationError


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    def save_entity(self, entity: Dict[str, Any]) -> str:
        """Save an entity to storage"""
        pass
    
    @abstractmethod
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity by ID"""
        pass
    
    @abstractmethod
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """Update an entity"""
        pass
    
    @abstractmethod
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity"""
        pass
    
    @abstractmethod
    def list_entities(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List entities with optional filters"""
        pass
    
    @abstractmethod
    def save_relationship(self, relationship: Dict[str, Any]) -> str:
        """Save a relationship to storage"""
        pass
    
    @abstractmethod
    def get_relationships(self, entity_id: str = None) -> List[Dict[str, Any]]:
        """Get relationships, optionally filtered by entity"""
        pass


class FileStorageBackend(StorageBackend):
    """File-based storage backend using JSON files"""
    
    def __init__(self, data_dir: str = "data"):
        self.logger = get_logger(__name__)
        self.data_dir = Path(data_dir)
        self.entities_file = self.data_dir / "entities.json"
        self.relationships_file = self.data_dir / "relationships.json"
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage files
        self._initialize_files()
        
        self.logger.info(f"File storage initialized at {self.data_dir}")
    
    def _initialize_files(self):
        """Initialize storage files if they don't exist"""
        if not self.entities_file.exists():
            with open(self.entities_file, 'w') as f:
                json.dump({"entities": {}, "metadata": {"created_at": datetime.utcnow().isoformat()}}, f)
        
        if not self.relationships_file.exists():
            with open(self.relationships_file, 'w') as f:
                json.dump({"relationships": [], "metadata": {"created_at": datetime.utcnow().isoformat()}}, f)
    
    def _load_entities(self) -> Dict[str, Any]:
        """Load entities from file"""
        try:
            with open(self.entities_file, 'r') as f:
                data = json.load(f)
                return data.get("entities", {})
        except Exception as e:
            self.logger.error(f"Failed to load entities: {e}")
            raise DatabaseError(f"Failed to load entities: {e}", "load_entities")
    
    def _save_entities(self, entities: Dict[str, Any]):
        """Save entities to file"""
        try:
            # Load existing data to preserve metadata
            try:
                with open(self.entities_file, 'r') as f:
                    data = json.load(f)
            except:
                data = {"metadata": {}}
            
            data["entities"] = entities
            data["metadata"]["updated_at"] = datetime.utcnow().isoformat()
            
            with open(self.entities_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save entities: {e}")
            raise DatabaseError(f"Failed to save entities: {e}", "save_entities")
    
    def _load_relationships(self) -> List[Dict[str, Any]]:
        """Load relationships from file"""
        try:
            with open(self.relationships_file, 'r') as f:
                data = json.load(f)
                return data.get("relationships", [])
        except Exception as e:
            self.logger.error(f"Failed to load relationships: {e}")
            raise DatabaseError(f"Failed to load relationships: {e}", "load_relationships")
    
    def _save_relationships(self, relationships: List[Dict[str, Any]]):
        """Save relationships to file"""
        try:
            # Load existing data to preserve metadata
            try:
                with open(self.relationships_file, 'r') as f:
                    data = json.load(f)
            except:
                data = {"metadata": {}}
            
            data["relationships"] = relationships
            data["metadata"]["updated_at"] = datetime.utcnow().isoformat()
            
            with open(self.relationships_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save relationships: {e}")
            raise DatabaseError(f"Failed to save relationships: {e}", "save_relationships")
    
    def save_entity(self, entity: Dict[str, Any]) -> str:
        """Save an entity to storage"""
        try:
            entities = self._load_entities()
            
            # Generate ID if not provided
            if 'id' not in entity:
                entity['id'] = str(uuid.uuid4())
            
            entity_id = entity['id']
            
            # Add timestamps
            entity['created_at'] = datetime.utcnow().isoformat()
            entity['updated_at'] = datetime.utcnow().isoformat()
            
            # Save entity
            entities[entity_id] = entity
            self._save_entities(entities)
            
            self.logger.info(f"Saved entity {entity_id}")
            return entity_id
            
        except Exception as e:
            self.logger.error(f"Failed to save entity: {e}")
            raise DatabaseError(f"Failed to save entity: {e}", "save_entity")
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity by ID"""
        try:
            entities = self._load_entities()
            entity = entities.get(entity_id)
            
            if entity:
                self.logger.debug(f"Retrieved entity {entity_id}")
            else:
                self.logger.debug(f"Entity {entity_id} not found")
            
            return entity
            
        except Exception as e:
            self.logger.error(f"Failed to get entity {entity_id}: {e}")
            raise DatabaseError(f"Failed to get entity: {e}", "get_entity")
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """Update an entity"""
        try:
            entities = self._load_entities()
            
            if entity_id not in entities:
                return False
            
            # Update entity
            entity = entities[entity_id]
            entity.update(updates)
            entity['updated_at'] = datetime.utcnow().isoformat()
            
            # Save updated entities
            entities[entity_id] = entity
            self._save_entities(entities)
            
            self.logger.info(f"Updated entity {entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update entity {entity_id}: {e}")
            raise DatabaseError(f"Failed to update entity: {e}", "update_entity")
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity"""
        try:
            entities = self._load_entities()
            
            if entity_id not in entities:
                return False
            
            # Remove entity
            del entities[entity_id]
            self._save_entities(entities)
            
            # Remove related relationships
            relationships = self._load_relationships()
            relationships = [
                rel for rel in relationships 
                if rel.get('source_id') != entity_id and rel.get('target_id') != entity_id
            ]
            self._save_relationships(relationships)
            
            self.logger.info(f"Deleted entity {entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete entity {entity_id}: {e}")
            raise DatabaseError(f"Failed to delete entity: {e}", "delete_entity")
    
    def list_entities(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List entities with optional filters"""
        try:
            entities = self._load_entities()
            entity_list = list(entities.values())
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if key == 'type':
                        entity_list = [e for e in entity_list if e.get('type') == value]
                    elif key == 'source':
                        entity_list = [e for e in entity_list if e.get('source') == value]
                    else:
                        # Generic attribute filter
                        entity_list = [e for e in entity_list if e.get('attributes', {}).get(key) == value]
            
            # Apply limit
            if limit > 0:
                entity_list = entity_list[:limit]
            
            self.logger.debug(f"Listed {len(entity_list)} entities")
            return entity_list
            
        except Exception as e:
            self.logger.error(f"Failed to list entities: {e}")
            raise DatabaseError(f"Failed to list entities: {e}", "list_entities")
    
    def save_relationship(self, relationship: Dict[str, Any]) -> str:
        """Save a relationship to storage"""
        try:
            relationships = self._load_relationships()
            
            # Generate ID if not provided
            if 'id' not in relationship:
                relationship['id'] = str(uuid.uuid4())
            
            relationship_id = relationship['id']
            
            # Add timestamps
            relationship['created_at'] = datetime.utcnow().isoformat()
            
            # Save relationship
            relationships.append(relationship)
            self._save_relationships(relationships)
            
            self.logger.info(f"Saved relationship {relationship_id}")
            return relationship_id
            
        except Exception as e:
            self.logger.error(f"Failed to save relationship: {e}")
            raise DatabaseError(f"Failed to save relationship: {e}", "save_relationship")
    
    def get_relationships(self, entity_id: str = None) -> List[Dict[str, Any]]:
        """Get relationships, optionally filtered by entity"""
        try:
            relationships = self._load_relationships()
            
            if entity_id:
                relationships = [
                    rel for rel in relationships 
                    if rel.get('source_id') == entity_id or rel.get('target_id') == entity_id
                ]
            
            self.logger.debug(f"Retrieved {len(relationships)} relationships")
            return relationships
            
        except Exception as e:
            self.logger.error(f"Failed to get relationships: {e}")
            raise DatabaseError(f"Failed to get relationships: {e}", "get_relationships")


class MemoryStorageBackend(StorageBackend):
    """In-memory storage backend for testing and development"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relationships: List[Dict[str, Any]] = []
        
        self.logger.info("Memory storage initialized")
    
    def save_entity(self, entity: Dict[str, Any]) -> str:
        """Save an entity to memory"""
        if 'id' not in entity:
            entity['id'] = str(uuid.uuid4())
        
        entity_id = entity['id']
        entity['created_at'] = datetime.utcnow().isoformat()
        entity['updated_at'] = datetime.utcnow().isoformat()
        
        self.entities[entity_id] = entity
        self.logger.info(f"Saved entity {entity_id}")
        return entity_id
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity by ID"""
        entity = self.entities.get(entity_id)
        self.logger.debug(f"Retrieved entity {entity_id}: {entity is not None}")
        return entity
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """Update an entity"""
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        entity.update(updates)
        entity['updated_at'] = datetime.utcnow().isoformat()
        
        self.logger.info(f"Updated entity {entity_id}")
        return True
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity"""
        if entity_id not in self.entities:
            return False
        
        del self.entities[entity_id]
        
        # Remove related relationships
        self.relationships = [
            rel for rel in self.relationships 
            if rel.get('source_id') != entity_id and rel.get('target_id') != entity_id
        ]
        
        self.logger.info(f"Deleted entity {entity_id}")
        return True
    
    def list_entities(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List entities with optional filters"""
        entity_list = list(self.entities.values())
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if key == 'type':
                    entity_list = [e for e in entity_list if e.get('type') == value]
                elif key == 'source':
                    entity_list = [e for e in entity_list if e.get('source') == value]
                else:
                    entity_list = [e for e in entity_list if e.get('attributes', {}).get(key) == value]
        
        # Apply limit
        if limit > 0:
            entity_list = entity_list[:limit]
        
        self.logger.debug(f"Listed {len(entity_list)} entities")
        return entity_list
    
    def save_relationship(self, relationship: Dict[str, Any]) -> str:
        """Save a relationship to memory"""
        if 'id' not in relationship:
            relationship['id'] = str(uuid.uuid4())
        
        relationship['created_at'] = datetime.utcnow().isoformat()
        self.relationships.append(relationship)
        
        relationship_id = relationship['id']
        self.logger.info(f"Saved relationship {relationship_id}")
        return relationship_id
    
    def get_relationships(self, entity_id: str = None) -> List[Dict[str, Any]]:
        """Get relationships, optionally filtered by entity"""
        if entity_id:
            filtered_relationships = [
                rel for rel in self.relationships 
                if rel.get('source_id') == entity_id or rel.get('target_id') == entity_id
            ]
        else:
            filtered_relationships = self.relationships
        
        self.logger.debug(f"Retrieved {len(filtered_relationships)} relationships")
        return filtered_relationships


class StorageManager:
    """Storage manager that handles different backends"""
    
    def __init__(self, backend: Optional[StorageBackend] = None):
        self.logger = get_logger(__name__)
        
        if backend:
            self.backend = backend
        else:
            # Default to file storage, fallback to memory
            try:
                self.backend = FileStorageBackend()
            except Exception as e:
                self.logger.warning(f"File storage failed, using memory storage: {e}")
                self.backend = MemoryStorageBackend()
        
        self.logger.info(f"Storage manager initialized with {type(self.backend).__name__}")
    
    def save_entity(self, entity: Dict[str, Any]) -> str:
        """Save an entity"""
        return self.backend.save_entity(entity)
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity"""
        return self.backend.get_entity(entity_id)
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """Update an entity"""
        return self.backend.update_entity(entity_id, updates)
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity"""
        return self.backend.delete_entity(entity_id)
    
    def list_entities(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List entities"""
        return self.backend.list_entities(filters, limit)
    
    def save_relationship(self, relationship: Dict[str, Any]) -> str:
        """Save a relationship"""
        return self.backend.save_relationship(relationship)
    
    def get_relationships(self, entity_id: str = None) -> List[Dict[str, Any]]:
        """Get relationships"""
        return self.backend.get_relationships(entity_id)


# Global storage manager instance
storage = StorageManager()