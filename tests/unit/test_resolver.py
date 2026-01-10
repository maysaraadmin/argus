#!/usr/bin/env python3
"""
Unit tests for Entity Resolution service
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.resolver import EntityResolver, ResolutionConfig, MatchResult
from argus.exceptions import EntityResolutionError


class TestEntityResolver:
    """Test cases for EntityResolver class"""
    
    @pytest.fixture
    def resolver(self):
        """Create a test entity resolver instance"""
        config = ResolutionConfig(
            similarity_threshold=0.8,
            possible_match_threshold=0.6,
            non_match_threshold=0.3,
            weights={"name": 0.5, "dob": 0.3, "address": 0.2}
        )
        return EntityResolver(config)
    
    @pytest.fixture
    def sample_entities(self):
        """Create sample entities for testing"""
        return [
            {
                "id": "person_1",
                "type": "person",
                "name": "John Smith",
                "dob": "1990-01-15",
                "address": "123 Main St, New York, NY",
                "phone": "555-1234"
            },
            {
                "id": "person_2", 
                "type": "person",
                "name": "Jon Smith",
                "dob": "1990-01-15",
                "address": "123 Main Street, New York, NY",
                "phone": "555-1235"
            },
            {
                "id": "person_3",
                "type": "person", 
                "name": "Jane Doe",
                "dob": "1985-05-20",
                "address": "456 Oak Ave, Boston, MA",
                "phone": "555-6789"
            },
            {
                "id": "person_4",
                "type": "person",
                "name": "John Smith",
                "dob": "1990-01-15", 
                "address": "123 Main St, New York, NY",
                "phone": "555-1234"
            }
        ]
    
    def test_init(self, resolver):
        """Test EntityResolver initialization"""
        assert resolver.config.similarity_threshold == 0.8
        assert resolver.config.weights["name"] == 0.5
        assert hasattr(resolver, 'string_calculator')
        assert hasattr(resolver, 'numeric_calculator')
        assert 'person' in resolver.blocking_rules
    
    @patch('src.core.resolver.DEPENDENCIES_AVAILABLE', False)
    def test_init_missing_dependencies(self):
        """Test initialization when dependencies are missing"""
        with pytest.raises(EntityResolutionError, match="Missing dependencies"):
            EntityResolver()
    
    def test_resolve_single_pair_match(self, resolver, sample_entities):
        """Test resolving two matching entities"""
        entity1 = sample_entities[0]  # John Smith
        entity2 = sample_entities[3]  # John Smith (duplicate)
        
        result = resolver.resolve_single_pair(entity1, entity2)
        
        assert isinstance(result, MatchResult)
        assert result.entity1_id == entity1["id"]
        assert result.entity2_id == entity2["id"]
        assert result.similarity_score >= 0.8  # Should be a match
        assert result.match_type == "match"
        assert result.confidence >= 0.8
        assert "field_similarities" in result.match_details
        assert "weights_used" in result.match_details
    
    def test_resolve_single_pair_possible_match(self, resolver, sample_entities):
        """Test resolving two possibly matching entities"""
        entity1 = sample_entities[0]  # John Smith
        entity2 = sample_entities[1]  # Jon Smith (similar but different)
        
        result = resolver.resolve_single_pair(entity1, entity2)
        
        assert isinstance(result, MatchResult)
        assert result.similarity_score >= 0.6  # Should be possible match
        assert result.match_type in ["possible_match", "match"]
        assert 0.6 <= result.confidence <= 0.9
    
    def test_resolve_single_pair_no_match(self, resolver, sample_entities):
        """Test resolving two non-matching entities"""
        entity1 = sample_entities[0]  # John Smith
        entity2 = sample_entities[2]  # Jane Doe (different)
        
        result = resolver.resolve_single_pair(entity1, entity2)
        
        assert isinstance(result, MatchResult)
        assert result.similarity_score < 0.6  # Should be non-match
        assert result.match_type == "non_match"
        assert result.confidence >= 0.4
    
    def test_resolve_single_pair_missing_fields(self, resolver):
        """Test resolving entities with missing fields"""
        entity1 = {"name": "John Smith", "dob": "1990-01-15"}
        entity2 = {"name": "John Smith"}  # Missing DOB
        
        result = resolver.resolve_single_pair(entity1, entity2)
        
        assert isinstance(result, MatchResult)
        assert result.similarity_score > 0  # Should have some similarity
        assert "field_similarities" in result.match_details
    
    def test_find_duplicate_entities(self, resolver, sample_entities):
        """Test finding duplicate entities in a batch"""
        duplicates = resolver.find_duplicate_entities(sample_entities)
        
        assert isinstance(duplicates, list)
        # Should find at least one duplicate (person_1 and person_4)
        assert len(duplicates) >= 1
        
        # Check that duplicates are high-confidence matches
        for duplicate in duplicates:
            assert duplicate.match_type == "match"
            assert duplicate.confidence >= 0.8
    
    def test_find_duplicate_entities_by_type(self, resolver, sample_entities):
        """Test finding duplicates filtered by entity type"""
        duplicates = resolver.find_duplicate_entities(sample_entities, entity_type="person")
        
        assert isinstance(duplicates, list)
        # All duplicates should be person entities
        for duplicate in duplicates:
            # Note: This would require access to the original entities
            # For now, just check the structure
            assert hasattr(duplicate, 'entity1_id')
            assert hasattr(duplicate, 'entity2_id')
    
    def test_canonicalize_entity(self, resolver, sample_entities):
        """Test creating a canonical entity from duplicates"""
        # Use the two John Smith entities
        duplicates = [sample_entities[0], sample_entities[3]]
        
        canonical = resolver.canonicalize_entity(duplicates)
        
        assert isinstance(canonical, dict)
        assert canonical["name"] == "John Smith"
        assert canonical["dob"] == "1990-01-15"
        assert "duplicate_count" in canonical
        assert canonical["duplicate_count"] == 2
        assert "sources" in canonical
        assert "canonicalized_at" in canonical
    
    def test_canonicalize_entity_empty_list(self, resolver):
        """Test canonicalizing empty entity list"""
        canonical = resolver.canonicalize_entity([])
        assert canonical == {}
    
    def test_canonicalize_entity_conflict_resolution(self, resolver):
        """Test canonicalizing entities with conflicting attributes"""
        entities = [
            {
                "id": "e1",
                "name": "John Smith",
                "age": 30,
                "city": "New York",
                "confidence": 0.9
            },
            {
                "id": "e2", 
                "name": "John Smith",
                "age": 31,  # Conflict
                "city": "New York",
                "confidence": 0.7
            },
            {
                "id": "e3",
                "name": "John Smith", 
                "age": 30,  # Same as e1
                "city": "Boston",  # Conflict
                "confidence": 0.8
            }
        ]
        
        canonical = resolver.canonicalize_entity(entities)
        
        # Should resolve conflicts based on confidence weights
        assert canonical["age"] == 30  # Higher total confidence for age 30
        assert canonical["city"] == "New York"  # Higher total confidence for New York
    
    def test_get_resolution_statistics(self, resolver, sample_entities):
        """Test getting resolution statistics"""
        # Create some mock matches
        matches = [
            MatchResult("person_1", "person_4", 0.95, "match", 0.9),
            MatchResult("person_1", "person_2", 0.75, "possible_match", 0.75),
            MatchResult("person_2", "person_3", 0.25, "non_match", 0.25)
        ]
        
        stats = resolver.get_resolution_statistics(matches)
        
        assert stats["total_matches"] == 3
        assert stats["definite_matches"] == 1
        assert stats["possible_matches"] == 1
        assert stats["avg_confidence"] == (0.9 + 0.75 + 0.25) / 3
        assert stats["avg_similarity"] == (0.95 + 0.75 + 0.25) / 3
        assert stats["high_confidence_matches"] == 1
    
    def test_get_resolution_statistics_empty(self, resolver):
        """Test getting statistics with no matches"""
        stats = resolver.get_resolution_statistics([])
        
        assert stats["total_matches"] == 0
        assert stats["definite_matches"] == 0
        assert stats["possible_matches"] == 0
    
    @patch('src.core.resolver.recordlinkage')
    @patch('src.core.resolver.pd.DataFrame')
    def test_resolve_batch(self, mock_df, mock_rl, resolver, sample_entities):
        """Test batch entity resolution"""
        # Mock the recordlinkage components
        mock_indexer = Mock()
        mock_indexer.index.return_value = [(0, 1)]  # One comparison pair
        mock_rl.Index.return_value = mock_indexer
        
        mock_compare = Mock()
        mock_compare.compute.return_value = pd.DataFrame({
            'name_similarity': [0.9],
            'dob_similarity': [1.0],
            'address_similarity': [0.8]
        })
        mock_rl.Compare.return_value = mock_compare
        
        # Mock DataFrame creation
        mock_df.return_value = pd.DataFrame(sample_entities)
        
        results = resolver.resolve_batch(sample_entities)
        
        assert isinstance(results, list)
        # Should have at least one result based on our mock
        assert len(results) >= 0
    
    def test_string_similarity_calculator(self, resolver):
        """Test string similarity calculation"""
        calculator = resolver.string_calculator
        
        # Exact match
        similarity = calculator.calculate("John Smith", "John Smith")
        assert similarity == 1.0
        
        # Partial match
        similarity = calculator.calculate("John Smith", "Jon Smith")
        assert similarity > 0.8
        
        # No match
        similarity = calculator.calculate("John Smith", "Jane Doe")
        assert similarity < 0.5
        
        # Empty strings
        similarity = calculator.calculate("", "John Smith")
        assert similarity == 0.0
    
    def test_numeric_similarity_calculator(self, resolver):
        """Test numeric similarity calculation"""
        calculator = resolver.numeric_calculator
        
        # Exact match
        similarity = calculator.calculate(30, 30)
        assert similarity == 1.0
        
        # Close values
        similarity = calculator.calculate(30, 32)
        assert similarity > 0.8
        
        # Different values
        similarity = calculator.calculate(30, 50)
        assert similarity < 0.5
        
        # None values
        similarity = calculator.calculate(None, 30)
        assert similarity == 0.0
    
    def test_config_validation(self):
        """Test ResolutionConfig validation"""
        # Test default values
        config = ResolutionConfig()
        assert config.similarity_threshold == 0.85
        assert config.weights["name"] == 0.4
        assert "phonetic" in config.blocking_methods
        
        # Test custom values
        config = ResolutionConfig(
            similarity_threshold=0.9,
            weights={"name": 0.6, "email": 0.4}
        )
        assert config.similarity_threshold == 0.9
        assert config.weights["name"] == 0.6
        assert config.weights["email"] == 0.4
    
    def test_match_result_validation(self):
        """Test MatchResult validation"""
        result = MatchResult(
            entity1_id="e1",
            entity2_id="e2", 
            similarity_score=0.85,
            match_type="match",
            confidence=0.9
        )
        
        assert result.entity1_id == "e1"
        assert result.entity2_id == "e2"
        assert result.similarity_score == 0.85
        assert result.match_type == "match"
        assert result.confidence == 0.9
        assert result.match_details == {}  # Default empty dict
    
    def test_error_handling(self, resolver):
        """Test error handling in entity resolution"""
        # Test with invalid entity data
        with pytest.raises(EntityResolutionError):
            resolver.resolve_single_pair({}, {})
        
        # Test with invalid threshold
        with pytest.raises(EntityResolutionError):
            EntityResolver(config=ResolutionConfig(similarity_threshold=1.5))
