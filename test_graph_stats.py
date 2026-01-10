#!/usr/bin/env python3
"""
Test graph stats to isolate the issue
"""
import sys
sys.path.insert(0, 'd:\\argus\\src')

from src.core.graph import KnowledgeGraph, Entity

def test_graph_stats():
    """Test graph stats method"""
    try:
        # Create a simple graph
        kg = KnowledgeGraph(use_cache=False)
        
        # Add some test entities
        entity1 = Entity(
            id="test1",
            type="person",
            name="John Doe",
            attributes={"age": 30},
            source="test"
        )
        
        entity2 = Entity(
            id="test2", 
            type="organization",
            name="Test Corp",
            attributes={"industry": "tech"},
            source="test"
        )
        
        kg.add_entity(entity1)
        kg.add_entity(entity2)
        
        # Add a relationship
        kg.add_relationship("test1", "test2", "works_at", {"role": "engineer"})
        
        # Get stats
        stats = kg.get_graph_stats()
        print("Graph stats:", stats)
        print("Test passed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_graph_stats()
