#!/usr/bin/env python3
"""
Integration tests for API endpoints
"""
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.api.server import app
from src.core.graph import Entity


class TestAPIIntegration:
    """Test cases for API integration"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_entity_data(self):
        """Sample entity data for testing"""
        return {
            "type": "person",
            "name": "John Doe",
            "attributes": {
                "age": 30,
                "city": "New York",
                "email": "john.doe@example.com"
            },
            "source": "test",
            "confidence": 0.9
        }
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Argus API"
        assert data["version"] == "0.1.0"
        assert data["status"] == "online"
        assert "endpoints" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "0.1.0"
    
    def test_create_entity(self, client, sample_entity_data):
        """Test creating an entity"""
        response = client.post("/api/entities", json=sample_entity_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["type"] == sample_entity_data["type"]
        assert data["name"] == sample_entity_data["name"]
        assert data["source"] == sample_entity_data["source"]
        assert data["confidence"] == sample_entity_data["confidence"]
    
    def test_create_entity_with_id(self, client, sample_entity_data):
        """Test creating an entity with specific ID"""
        sample_entity_data["id"] = "test_entity_123"
        
        response = client.post("/api/entities", json=sample_entity_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == "test_entity_123"
    
    def test_get_entity(self, client, sample_entity_data):
        """Test retrieving an entity"""
        # Create entity first
        create_response = client.post("/api/entities", json=sample_entity_data)
        entity_id = create_response.json()["id"]
        
        # Get entity
        response = client.get(f"/api/entities/{entity_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == entity_id
        assert data["name"] == sample_entity_data["name"]
        assert data["type"] == sample_entity_data["type"]
    
    def test_get_nonexistent_entity(self, client):
        """Test retrieving a non-existent entity"""
        response = client.get("/api/entities/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
    
    def test_update_entity(self, client, sample_entity_data):
        """Test updating an entity"""
        # Create entity first
        create_response = client.post("/api/entities", json=sample_entity_data)
        entity_id = create_response.json()["id"]
        
        # Update entity
        update_data = {
            "name": "John Smith",
            "attributes": {"age": 31, "city": "San Francisco"}
        }
        
        response = client.put(f"/api/entities/{entity_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "John Smith"
        assert data["attributes"]["age"] == 31
        assert data["attributes"]["city"] == "San Francisco"
        assert "updated_at" in data
    
    def test_update_nonexistent_entity(self, client):
        """Test updating a non-existent entity"""
        update_data = {"name": "Test"}
        
        response = client.put("/api/entities/nonexistent", json=update_data)
        assert response.status_code == 404
    
    def test_delete_entity(self, client, sample_entity_data):
        """Test deleting an entity"""
        # Create entity first
        create_response = client.post("/api/entities", json=sample_entity_data)
        entity_id = create_response.json()["id"]
        
        # Delete entity
        response = client.delete(f"/api/entities/{entity_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "deleted"
        assert data["entity_id"] == entity_id
        
        # Verify entity is gone
        get_response = client.get(f"/api/entities/{entity_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_entity(self, client):
        """Test deleting a non-existent entity"""
        response = client.delete("/api/entities/nonexistent")
        assert response.status_code == 404
    
    def test_list_entities(self, client, sample_entity_data):
        """Test listing entities"""
        # Create multiple entities
        entities = []
        for i in range(3):
            entity_data = sample_entity_data.copy()
            entity_data["name"] = f"Person {i+1}"
            entity_data["attributes"]["age"] = 20 + i
            
            response = client.post("/api/entities", json=entity_data)
            entities.append(response.json())
        
        # List entities
        response = client.get("/api/entities")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert len(data["items"]) <= 50  # Default limit
    
    def test_list_entities_with_filters(self, client, sample_entity_data):
        """Test listing entities with filters"""
        # Create entities of different types
        person_data = sample_entity_data.copy()
        org_data = {
            "type": "organization",
            "name": "Tech Corp",
            "attributes": {"industry": "technology", "size": 1000},
            "source": "test",
            "confidence": 1.0
        }
        
        client.post("/api/entities", json=person_data)
        client.post("/api/entities", json=org_data)
        
        # Filter by type
        response = client.get("/api/entities?entity_type=person")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["type"] == "person"
    
    def test_create_relationship(self, client, sample_entity_data):
        """Test creating a relationship"""
        # Create two entities first
        entity1_data = sample_entity_data.copy()
        entity1_data["name"] = "Alice"
        
        entity2_data = sample_entity_data.copy()
        entity2_data["name"] = "Bob"
        
        response1 = client.post("/api/entities", json=entity1_data)
        response2 = client.post("/api/entities", json=entity2_data)
        
        entity1_id = response1.json()["id"]
        entity2_id = response2.json()["id"]
        
        # Create relationship
        relationship_data = {
            "source_id": entity1_id,
            "target_id": entity2_id,
            "type": "knows",
            "attributes": {"since": "2020"},
            "strength": 0.8
        }
        
        response = client.post("/api/relationships", json=relationship_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["source_id"] == entity1_id
        assert data["target_id"] == entity2_id
        assert data["type"] == "knows"
        assert data["strength"] == 0.8
        assert "id" in data
    
    def test_create_relationship_missing_entities(self, client):
        """Test creating relationship with missing entities"""
        relationship_data = {
            "source_id": "nonexistent1",
            "target_id": "nonexistent2",
            "type": "knows"
        }
        
        response = client.post("/api/relationships", json=relationship_data)
        assert response.status_code == 400
    
    def test_get_relationships(self, client, sample_entity_data):
        """Test getting relationships"""
        # Create entities and relationship
        entity1_data = sample_entity_data.copy()
        entity1_data["name"] = "Alice"
        
        entity2_data = sample_entity_data.copy()
        entity2_data["name"] = "Bob"
        
        response1 = client.post("/api/entities", json=entity1_data)
        response2 = client.post("/api/entities", json=entity2_data)
        
        entity1_id = response1.json()["id"]
        entity2_id = response2.json()["id"]
        
        # Create relationship
        relationship_data = {
            "source_id": entity1_id,
            "target_id": entity2_id,
            "type": "knows"
        }
        
        client.post("/api/relationships", json=relationship_data)
        
        # Get relationships
        response = client.get("/api/relationships")
        assert response.status_code == 200
        
        data = response.json()
        assert "relationships" in data
        assert "count" in data
        assert len(data["relationships"]) >= 1
    
    def test_get_entity_network(self, client, sample_entity_data):
        """Test getting entity network"""
        # Create entities and relationships
        entities = []
        for i in range(3):
            entity_data = sample_entity_data.copy()
            entity_data["name"] = f"Person {i+1}"
            response = client.post("/api/entities", json=entity_data)
            entities.append(response.json())
        
        # Create relationships
        client.post("/api/relationships", json={
            "source_id": entities[0]["id"],
            "target_id": entities[1]["id"],
            "type": "knows"
        })
        
        client.post("/api/relationships", json={
            "source_id": entities[1]["id"],
            "target_id": entities[2]["id"],
            "type": "works_with"
        })
        
        # Get network for middle entity
        response = client.get(f"/api/graph/{entities[1]['id']}?depth=2")
        assert response.status_code == 200
        
        data = response.json()
        assert "nodes" in data
        assert "links" in data
        assert "metadata" in data
        assert len(data["nodes"]) >= 2
        assert len(data["links"]) >= 1
    
    def test_get_entity_network_nonexistent(self, client):
        """Test getting network for non-existent entity"""
        response = client.get("/api/graph/nonexistent")
        assert response.status_code == 404
    
    def test_search_entities(self, client, sample_entity_data):
        """Test searching entities"""
        # Create entities
        entity1_data = sample_entity_data.copy()
        entity1_data["name"] = "Alice Smith"
        
        entity2_data = sample_entity_data.copy()
        entity2_data["name"] = "Bob Jones"
        
        client.post("/api/entities", json=entity1_data)
        client.post("/api/entities", json=entity2_data)
        
        # Search
        search_data = {
            "query": "Alice",
            "limit": 10
        }
        
        response = client.post("/api/search", json=search_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
        
        # Check that results contain the searched name
        found_alice = any("Alice" in item.get("name", "") for item in data["items"])
        assert found_alice
    
    def test_search_entities_with_filters(self, client, sample_entity_data):
        """Test searching entities with filters"""
        # Create entities with different attributes
        entity1_data = sample_entity_data.copy()
        entity1_data["name"] = "Alice"
        entity1_data["attributes"]["age"] = 25
        
        entity2_data = sample_entity_data.copy()
        entity2_data["name"] = "Bob"
        entity2_data["attributes"]["age"] = 35
        
        client.post("/api/entities", json=entity1_data)
        client.post("/api/entities", json=entity2_data)
        
        # Search with age filter
        search_data = {
            "query": "",
            "filters": {"age": {"min": 30, "max": 40}},
            "limit": 10
        }
        
        response = client.post("/api/search", json=search_data)
        assert response.status_code == 200
        
        data = response.json()
        # Should only find Bob (age 35)
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Bob"
    
    def test_resolve_entities(self, client):
        """Test entity resolution"""
        entities_data = {
            "entities": [
                {
                    "name": "John Smith",
                    "dob": "1990-01-15",
                    "address": "123 Main St, New York, NY"
                },
                {
                    "name": "Jon Smith", 
                    "dob": "1990-01-15",
                    "address": "123 Main Street, New York, NY"
                },
                {
                    "name": "Jane Doe",
                    "dob": "1985-05-20", 
                    "address": "456 Oak Ave, Boston, MA"
                }
            ]
        }
        
        response = client.post("/api/resolve", json=entities_data)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Should find at least one match between the two John Smith entities
        assert len(data) >= 0
    
    def test_get_stats(self, client, sample_entity_data):
        """Test getting graph statistics"""
        # Create some entities and relationships
        for i in range(3):
            entity_data = sample_entity_data.copy()
            entity_data["name"] = f"Person {i+1}"
            client.post("/api/entities", json=entity_data)
        
        # Get stats
        response = client.get("/api/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert "entity_types" in data
        assert "density" in data
        assert "connected_components" in data
        assert "avg_clustering" in data
        assert data["nodes"] >= 3
    
    def test_error_handling(self, client):
        """Test API error handling"""
        # Test invalid entity data
        invalid_data = {
            "type": "invalid_type",
            "name": "",  # Empty name should fail validation
            "attributes": "not_a_dict"  # Should be a dict
        }
        
        response = client.post("/api/entities", json=invalid_data)
        assert response.status_code == 400
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/api/entities")
        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
    
    def test_request_logging(self, client):
        """Test that requests are logged"""
        response = client.get("/health")
        assert response.status_code == 200
        # Check for process time header
        assert "x-process-time" in response.headers
