#!/usr/bin/env python3
"""
Unit tests for Knowledge Graph service
"""
import pytest
import networkx as nx
from unittest.mock import Mock, patch
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.graph import KnowledgeGraph, Entity
from argus.exceptions import EntityNotFoundError, GraphError


class TestKnowledgeGraph:
    """Test cases for KnowledgeGraph class"""
    
    @pytest.fixture
    def kg(self):
        """Create a test knowledge graph instance"""
        return KnowledgeGraph(use_cache=False)
    
    @pytest.fixture
    def sample_entity(self):
        """Create a sample entity for testing"""
        return Entity(
            id="test_entity_1",
            type="person",
            name="John Doe",
            attributes={"age": 30, "city": "New York"},
            source="test",
            confidence=0.9
        )
    
    @pytest.fixture
    def sample_entities(self):
        """Create multiple sample entities"""
        return [
            Entity(
                id="person_1",
                type="person",
                name="Alice Smith",
                attributes={"age": 25, "city": "Boston"},
                source="test",
                confidence=0.8
            ),
            Entity(
                id="person_2", 
                type="person",
                name="Bob Jones",
                attributes={"age": 35, "city": "New York"},
                source="test",
                confidence=0.9
            ),
            Entity(
                id="company_1",
                type="organization",
                name="Tech Corp",
                attributes={"industry": "technology", "size": 1000},
                source="test",
                confidence=1.0
            )
        ]
    
    def test_init(self, kg):
        """Test KnowledgeGraph initialization"""
        assert isinstance(kg.graph, nx.MultiGraph)
        assert kg.entity_index == {}
        assert kg.type_index == {}
        assert kg.attribute_index == {}
        assert kg.redis is None
    
    def test_add_entity(self, kg, sample_entity):
        """Test adding an entity to the graph"""
        entity_id = kg.add_entity(sample_entity)
        
        assert entity_id == "test_entity_1"
        assert entity_id in kg.entity_index
        assert entity_id in kg.graph.nodes
        assert sample_entity.type in kg.type_index
        assert entity_id in kg.type_index[sample_entity.type]
        
        # Check graph node data
        node_data = kg.graph.nodes[entity_id]
        assert node_data['type'] == sample_entity.type
        assert node_data['name'] == sample_entity.name
        assert node_data['source'] == sample_entity.source
        assert node_data['confidence'] == sample_entity.confidence
        assert 'created_at' in node_data
    
    def test_add_duplicate_entity(self, kg, sample_entity):
        """Test adding a duplicate entity"""
        kg.add_entity(sample_entity)
        
        # Add same entity again (should update)
        entity_id = kg.add_entity(sample_entity)
        assert entity_id == "test_entity_1"
        assert len(kg.entity_index) == 1
    
    def test_get_entity(self, kg, sample_entity):
        """Test retrieving an entity"""
        kg.add_entity(sample_entity)
        
        retrieved_entity = kg.get_entity("test_entity_1")
        assert retrieved_entity.id == sample_entity.id
        assert retrieved_entity.name == sample_entity.name
        assert retrieved_entity.type == sample_entity.type
    
    def test_get_nonexistent_entity(self, kg):
        """Test retrieving a non-existent entity"""
        with pytest.raises(EntityNotFoundError):
            kg.get_entity("nonexistent")
    
    def test_update_entity(self, kg, sample_entity):
        """Test updating an entity"""
        kg.add_entity(sample_entity)
        
        updates = {
            "name": "John Smith",
            "attributes": {"age": 31, "city": "San Francisco"}
        }
        
        updated_entity = kg.update_entity("test_entity_1", updates)
        assert updated_entity.name == "John Smith"
        assert updated_entity.attributes["age"] == 31
        assert updated_entity.attributes["city"] == "San Francisco"
    
    def test_update_nonexistent_entity(self, kg):
        """Test updating a non-existent entity"""
        with pytest.raises(EntityNotFoundError):
            kg.update_entity("nonexistent", {"name": "Test"})
    
    def test_delete_entity(self, kg, sample_entity):
        """Test deleting an entity"""
        entity_id = kg.add_entity(sample_entity)
        
        result = kg.delete_entity(entity_id)
        assert result is True
        assert entity_id not in kg.entity_index
        assert entity_id not in kg.graph.nodes
        assert entity_id not in kg.type_index[sample_entity.type]
    
    def test_delete_nonexistent_entity(self, kg):
        """Test deleting a non-existent entity"""
        with pytest.raises(EntityNotFoundError):
            kg.delete_entity("nonexistent")
    
    def test_add_relationship(self, kg, sample_entities):
        """Test adding a relationship between entities"""
        # Add entities first
        kg.add_entity(sample_entities[0])
        kg.add_entity(sample_entities[1])
        
        # Add relationship
        kg.add_relationship(
            source_id="person_1",
            target_id="person_2", 
            relation_type="knows",
            attributes={"since": "2020"}
        )
        
        # Check relationship exists
        assert kg.graph.has_edge("person_1", "person_2")
        edge_data = kg.graph.get_edge_data("person_1", "person_2")
        assert edge_data["type"] == "knows"
        assert edge_data["since"] == "2020"
    
    def test_add_relationship_missing_entity(self, kg, sample_entities):
        """Test adding relationship with missing entity"""
        kg.add_entity(sample_entities[0])
        
        with pytest.raises(ValueError, match="Both entities must exist"):
            kg.add_relationship("person_1", "nonexistent", "knows")
    
    def test_find_connections(self, kg, sample_entities):
        """Test finding connections between entities"""
        # Add entities
        for entity in sample_entities:
            kg.add_entity(entity)
        
        # Create relationships
        kg.add_relationship("person_1", "person_2", "knows")
        kg.add_relationship("person_2", "company_1", "works_for")
        kg.add_relationship("person_1", "company_1", "consults_for")
        
        # Find paths
        paths = kg.find_connections("person_1", "company_1", max_depth=3)
        assert len(paths) >= 1
        assert ["person_1", "company_1"] in paths
    
    def test_find_connections_no_path(self, kg, sample_entities):
        """Test finding connections when no path exists"""
        # Add entities but no relationships
        for entity in sample_entities:
            kg.add_entity(entity)
        
        paths = kg.find_connections("person_1", "company_1", max_depth=3)
        assert len(paths) == 0
    
    def test_get_entity_network(self, kg, sample_entities):
        """Test getting entity network for visualization"""
        # Add entities and relationships
        for entity in sample_entities:
            kg.add_entity(entity)
        
        kg.add_relationship("person_1", "person_2", "knows")
        kg.add_relationship("person_2", "company_1", "works_for")
        
        network = kg.get_entity_network("person_2", depth=2)
        
        assert "nodes" in network
        assert "links" in network
        assert len(network["nodes"]) == 3  # All entities should be included
        assert len(network["links"]) == 2  # Both relationships
        
        # Check node structure
        node_ids = [node["id"] for node in network["nodes"]]
        assert "person_1" in node_ids
        assert "person_2" in node_ids
        assert "company_1" in node_ids
    
    def test_get_entity_network_nonexistent(self, kg):
        """Test getting network for non-existent entity"""
        network = kg.get_entity_network("nonexistent", depth=2)
        assert network["nodes"] == []
        assert network["links"] == []
    
    def test_search_entities(self, kg, sample_entities):
        """Test searching entities"""
        # Add entities
        for entity in sample_entities:
            kg.add_entity(entity)
        
        # Search by name
        results = kg.search_entities("Alice")
        assert len(results) == 1
        assert results[0]["id"] == "person_1"
        
        # Search by attribute
        results = kg.search_entities("New York")
        assert len(results) == 1
        assert results[0]["id"] == "person_2"
        
        # Search by type
        results = kg.search_entities("", entity_type="organization")
        assert len(results) == 1
        assert results[0]["id"] == "company_1"
    
    def test_search_entities_no_results(self, kg):
        """Test searching with no results"""
        results = kg.search_entities("nonexistent")
        assert len(results) == 0
    
    def test_get_graph_stats(self, kg, sample_entities):
        """Test getting graph statistics"""
        # Add entities and relationships
        for entity in sample_entities:
            kg.add_entity(entity)
        
        kg.add_relationship("person_1", "person_2", "knows")
        kg.add_relationship("person_2", "company_1", "works_for")
        
        stats = kg.get_graph_stats()
        
        assert stats["nodes"] == 3
        assert stats["edges"] == 2
        assert "person" in stats["entity_types"]
        assert "organization" in stats["entity_types"]
        assert stats["entity_types"]["person"] == 2
        assert stats["entity_types"]["organization"] == 1
        assert 0 <= stats["density"] <= 1
        assert stats["connected_components"] == 1
    
    def test_get_neighbors(self, kg, sample_entities):
        """Test getting neighboring entities"""
        # Add entities and relationships
        for entity in sample_entities:
            kg.add_entity(entity)
        
        kg.add_relationship("person_1", "person_2", "knows")
        kg.add_relationship("person_2", "company_1", "works_for")
        
        # Get direct neighbors
        neighbors = kg.get_neighbors("person_2", depth=1)
        assert len(neighbors) == 2
        assert "person_1" in neighbors
        assert "company_1" in neighbors
        
        # Get neighbors within depth 2
        neighbors = kg.get_neighbors("person_1", depth=2)
        assert len(neighbors) == 2  # person_2 and company_1
    
    def test_get_neighbors_nonexistent(self, kg):
        """Test getting neighbors for non-existent entity"""
        with pytest.raises(EntityNotFoundError):
            kg.get_neighbors("nonexistent")
    
    def test_entity_to_dict(self, kg, sample_entity):
        """Test converting entity to dictionary"""
        kg.add_entity(sample_entity)
        
        entity_dict = kg._entity_to_dict(sample_entity)
        assert entity_dict["id"] == sample_entity.id
        assert entity_dict["type"] == sample_entity.type
        assert entity_dict["name"] == sample_entity.name
        assert entity_dict["attributes"] == sample_entity.attributes
        assert "degree" in entity_dict
    
    @patch('src.core.graph.redis.Redis')
    def test_cache_initialization(self, mock_redis):
        """Test Redis cache initialization"""
        mock_redis_instance = Mock()
        mock_redis.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        
        kg = KnowledgeGraph(use_cache=True)
        
        assert kg.redis is not None
        mock_redis_instance.ping.assert_called_once()
    
    def test_cache_disabled(self, kg):
        """Test operation with cache disabled"""
        assert kg.redis is None
        
        # Operations should work normally without cache
        entity_id = kg.add_entity(Entity(
            id="test",
            type="person",
            name="Test",
            attributes={},
            source="test"
        ))
        assert entity_id == "test"
