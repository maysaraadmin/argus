#!/usr/bin/env python3
"""Import sample data for demonstration"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.core.graph import KnowledgeGraph, Entity
from src.core.resolver import EntityResolver
import uuid
import json

def create_sample_data():
    """Create sample intelligence data"""
    
    kg = KnowledgeGraph()
    
    # Create sample entities
    entities = [
        Entity(
            id=f"person_{uuid.uuid4().hex[:8]}",
            type="person",
            name="John Smith",
            attributes={
                "dob": "1980-05-15",
                "nationality": "US",
                "occupation": "Businessman"
            },
            source="sample"
        ),
        Entity(
            id=f"person_{uuid.uuid4().hex[:8]}",
            type="person",
            name="Jon Smith",
            attributes={
                "dob": "1980-05-15",
                "nationality": "USA",
                "occupation": "Entrepreneur"
            },
            source="sample"
        ),
        Entity(
            id=f"person_{uuid.uuid4().hex[:8]}",
            type="person",
            name="Alice Johnson",
            attributes={
                "dob": "1975-11-22",
                "nationality": "UK",
                "occupation": "Lawyer"
            },
            source="sample"
        ),
        Entity(
            id="org_techcorp",
            type="organization",
            name="TechCorp Inc.",
            attributes={
                "industry": "Technology",
                "country": "US",
                "founded": "2010"
            },
            source="sample"
        ),
        Entity(
            id="org_innovate",
            type="organization",
            name="Innovate LLC",
            attributes={
                "industry": "Consulting",
                "country": "UK",
                "founded": "2015"
            },
            source="sample"
        ),
        Entity(
            id="loc_nyc",
            type="location",
            name="New York City",
            attributes={
                "country": "US",
                "type": "city",
                "population": "8.4M"
            },
            source="sample"
        ),
        Entity(
            id="loc_london",
            type="location",
            name="London",
            attributes={
                "country": "UK",
                "type": "city",
                "population": "8.9M"
            },
            source="sample"
        )
    ]
    
    # Add entities to graph
    for entity in entities:
        kg.add_entity(entity)
    
    # Add relationships
    relationships = [
        ("person_0", "org_techcorp", "works_at", {"role": "CEO", "since": "2015"}),
        ("person_1", "org_techcorp", "works_at", {"role": "Advisor", "since": "2016"}),
        ("person_2", "org_innovate", "works_at", {"role": "Partner", "since": "2018"}),
        ("person_0", "person_2", "knows", {"context": "business"}),
        ("org_techcorp", "org_innovate", "partners_with", {"since": "2019"}),
        ("org_techcorp", "loc_nyc", "located_in", {}),
        ("org_innovate", "loc_london", "located_in", {}),
        ("person_0", "loc_nyc", "lives_in", {}),
        ("person_2", "loc_london", "lives_in", {})
    ]
    
    # Map entity names to IDs
    id_map = {e.name: e.id for e in entities}
    
    for source_name, target_name, rel_type, attrs in relationships:
        source_id = id_map.get(source_name) or source_name
        target_id = id_map.get(target_name) or target_name
        kg.add_relationship(source_id, target_id, rel_type, attrs)
    
    # Run entity resolution on the two John Smiths
    resolver = EntityResolver()
    john_smiths = [
        {"id": entities[0].id, "name": "John Smith", "dob": "1980-05-15", "nationality": "US"},
        {"id": entities[1].id, "name": "Jon Smith", "dob": "1980-05-15", "nationality": "USA"}
    ]
    
    matches = resolver.resolve_batch(john_smiths)
    
    # Apply matches
    for match in matches:
        if match.match_type == "same_entity":
            kg.add_relationship(
                match.entity1_id,
                match.entity2_id,
                "alias",
                {"confidence": match.confidence, "resolved": True}
            )
    
    # Export sample data
    sample_data = {
        "entities": [e.__dict__ for e in entities],
        "relationships": relationships,
        "graph_stats": {
            "nodes": len(kg.graph.nodes()),
            "edges": len(kg.graph.edges())
        }
    }
    
    with open("examples/sample_graph.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"✅ Created sample data with {len(entities)} entities")
    print(f"✅ Added {len(relationships)} relationships")
    print(f"✅ Found {len(matches)} entity matches")
    print(f"✅ Sample data saved to examples/sample_graph.json")
    
    # Print some example queries
    print("\nExample queries:")
    print("1. Find connections between person_0 and person_2:")
    paths = kg.find_connections(entities[0].id, entities[2].id, max_depth=3)
    for path in paths[:2]:  # Show first 2 paths
        print(f"   → {' → '.join(path)}")
    
    print("\n2. Search for 'Smith':")
    results = kg.search_entities("Smith")
    for result in results[:3]:
        print(f"   - {result['name']} ({result['type']})")

if __name__ == "__main__":
    create_sample_data()