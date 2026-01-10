# Object-Centric Data Model for Argus MVP

## 📋 Overview

The object-centric data model is the foundation of Argus MVP. Unlike traditional row-based databases, everything is stored as interconnected objects with properties and relationships, mirroring how real-world entities relate to each other.

## 🎯 Core Concepts

### 1. **Objects (Entities)**
Everything in the system is an object with:
- **Unique Identifier**: Auto-generated or user-provided ID
- **Type**: Classification (person, organization, location, event, etc.)
- **Properties**: Key-value pairs for attributes
- **Relationships**: Links to other objects
- **Source References**: Where the data came from
- **Confidence Score**: How certain we are about the data

### 2. **Relationships**
Objects are connected through typed relationships:
- **Directionality**: Can be directed or undirected
- **Attributes**: Relationship-specific properties (strength, date, etc.)
- **Weight**: Importance or confidence score

### 3. **Graph Structure**
The entire system forms a knowledge graph:
- **Nodes**: Objects/entities
- **Edges**: Relationships between objects
- **Properties**: Both nodes and edges can have attributes
- **Metadata**: Graph-level information (creation date, version, etc.)

## 📊 Data Model Examples

### Person Object Example
```json
{
  "id": "person_001",
  "type": "person",
  "name": "John Doe",
  "attributes": {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1985-03-15",
    "passport": "AB123456",
    "email": "john.doe@example.com",
    "phone": "+1-555-1234",
    "address": "123 Main St, New York, NY 10001",
    "nationality": "American",
    "occupation": "Software Engineer"
  },
  "relationships": [
    {
      "id": "rel_001",
      "type": "works_at",
      "source": "person_001",
      "target": "org_001",
      "attributes": {
        "start_date": "2020-01-15",
        "position": "Senior Developer",
        "salary": 120000
      }
    },
    {
      "id": "rel_002",
      "type": "lives_at",
      "source": "person_001",
      "target": "loc_001",
      "attributes": {
        "address": "123 Main St, New York, NY 10001",
        "since": "2020-01-01"
      }
    }
  ],
  "source_references": [
    {
      "id": "src_001",
      "type": "database",
      "name": "Employee Database",
      "extraction_date": "2020-01-10",
      "confidence": 0.95
    }
  ],
  "confidence": 0.95,
  "created_at": "2020-01-10T10:00:00Z",
  "updated_at": "2020-01-15T14:30:00Z"
}
```

### Organization Object Example
```json
{
  "id": "org_001",
  "type": "organization",
  "name": "Acme Corporation",
  "attributes": {
    "industry": "Technology",
    "founded": "2010-01-01",
    "employees": 5000,
    "revenue": 1000000000,
    "headquarters": "San Francisco, CA",
    "stock_symbol": "ACME",
    "website": "https://acme.com"
  },
  "relationships": [
    {
      "id": "rel_003",
      "type": "located_in",
      "source": "org_001",
      "target": "loc_001",
      "attributes": {
        "city": "San Francisco"
      }
    },
    {
      "id": "rel_004",
      "type": "has_ceo",
      "source": "person_002",
      "target": "org_001",
      "attributes": {
        "since": "2015-06-01",
        "title": "CEO"
      }
    }
  ],
  "source_references": [
    {
      "id": "src_002",
      "type": "public_records",
      "name": "California Business Registry",
      "extraction_date": "2020-01-05",
      "confidence": 0.98
    }
  ],
  "confidence": 0.98,
  "created_at": "2020-01-05T09:00:00Z",
  "updated_at": "2020-01-15T16:00:00Z"
}
```

### Location Object Example
```json
{
  "id": "loc_001",
  "type": "location",
  "name": "123 Main St, New York, NY 10001",
  "attributes": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "postal_code": "10001",
    "address_type": "commercial"
  },
  "relationships": [
    {
      "id": "rel_005",
      "type": "located_in",
      "source": "person_001",
      "target": "loc_001",
      "attributes": {
        "since": "2020-01-01"
      }
    }
  ]
}
```

## 🔍 Key Advantages of Object-Centric Model

### 1. **Real-World Mapping**
- Objects directly represent real-world entities
- Relationships mirror actual connections
- More intuitive than relational tables

### 2. **Flexibility**
- Easy to add new object types
- Relationships can have arbitrary attributes
- No rigid schema constraints

### 3. **Graph Analysis**
- Natural fit for network analysis
- Built-in support for graph algorithms
- Rich relationship exploration

### 4. **Data Integration**
- Multiple sources can reference same objects
- Automatic deduplication through relationships
- Source traceability maintained

### 5. **Scalability**
- Graph databases optimized for relationship queries
- Efficient traversal algorithms
- Natural partitioning and clustering

## 🛠️ Implementation in Argus MVP

### Core Classes
```python
@dataclass
class Entity:
    id: str
    type: str
    name: str
    attributes: Dict[str, Any]
    source: str
    confidence: float = 1.0
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class Relationship:
    id: str
    source: str
    target: str
    type: str
    attributes: Dict[str, Any]
    strength: float = 1.0
    created_at: datetime
    updated_at: Optional[datetime] = None

class KnowledgeGraph:
    def __init__(self, use_cache=True):
        self.graph = nx.MultiGraph()
        self.entities = {}
        self.relationships = {}
```

### Database Storage
```python
# Objects stored as JSON documents
{
  "entities": [
    {
      "id": "person_001",
      "type": "person",
      "name": "John Doe",
      "attributes": {...}
    }
  ],
  "relationships": [
    {
      "id": "rel_001",
      "source": "person_001",
      "target": "org_001",
      "type": "works_at",
      "attributes": {...}
    }
  ]
}
```

## 📊 API Integration

### REST Endpoints
```http
POST /api/entities          # Create new entity
GET /api/entities/{id}     # Get entity by ID
PUT /api/entities/{id}     # Update entity
DELETE /api/entities/{id}  # Delete entity

POST /api/relationships     # Create relationship
GET /api/relationships/{id} # Get relationship by ID
PUT /api/relationships/{id} # Update relationship
DELETE /api/relationships/{id} # Delete relationship

GET /api/graph/{id}       # Get entity network
POST /api/search          # Search entities
POST /api/resolve          # Entity resolution
```

### JSON Response Format
```json
{
  "id": "person_001",
  "type": "person",
  "name": "John Doe",
  "attributes": {
    "first_name": "John",
    "last_name": "Doe"
  },
  "relationships": [
    {
      "id": "rel_001",
      "type": "works_at",
      "source": "person_001",
      "target": "org_001"
    }
  ],
  "source_references": [
    {
      "type": "database",
      "name": "Employee Records"
    }
  ]
}
```

## 🎯 Benefits for Intelligence Analysis

### 1. **Entity Resolution**
- Automatic duplicate detection
- Relationship-based deduplication
- Confidence scoring for matches

### 2. **Network Analysis**
- Centrality measures (most important nodes)
- Path finding between entities
- Community detection
- Temporal pattern analysis

### 3. **Source Traceability**
- Complete audit trail
- Confidence scoring for data sources
- Document linking for verification

### 4. **Visualization**
- Interactive graph exploration
- Relationship strength visualization
- Temporal analysis of connections

## 🚀 Getting Started with Object-Centric Model

### 1. **Create Entities**
```python
# Using the API
entity_data = {
    "name": "John Doe",
    "type": "person",
    "attributes": {
        "email": "john.doe@example.com",
        "phone": "+1-555-1234"
    }
}

response = requests.post("http://localhost:8000/api/entities", json=entity_data)
entity_id = response.json()["id"]
```

### 2. **Create Relationships**
```python
relationship_data = {
    "source": entity_id,
    "target": target_entity_id,
    "type": "works_at",
    "attributes": {
        "start_date": "2020-01-15"
    }
}

response = requests.post("http://localhost:8000/api/relationships", json=relationship_data)
```

### 3. **Query Network**
```python
# Get entity's network
response = requests.get(f"http://localhost:8000/api/graph/{entity_id}")

# Search for connections
search_data = {
    "q": "John Doe",
    "depth": 2
}

response = requests.post("http://localhost:8000/api/search", json=search_data)
```

## 📈 Best Practices

### 1. **Entity Design**
- Use descriptive names
- Include proper type classification
- Add confidence scores
- Maintain source references

### 2. **Relationship Design**
- Use meaningful relationship types
- Include temporal information
- Add strength/weight attributes
- Avoid circular relationships

### 3. **Data Quality**
- Validate attributes before storage
- Use consistent naming conventions
- Maintain referential integrity
- Regular deduplication

### 4. **Performance**
- Use graph databases for large datasets
- Implement proper indexing
- Cache frequently accessed data
- Use batch operations for bulk updates

## 🎉 Conclusion

The object-centric data model in Argus MVP provides a powerful foundation for intelligence analysis:

✅ **Real-World Mapping**: Objects represent actual entities  
✅ **Flexible Relationships**: Rich, typed connections  
✅ **Graph Analysis**: Native support for network algorithms  
✅ **Source Traceability**: Complete audit trails  
✅ **Entity Resolution**: Automatic duplicate detection  
✅ **Scalable Storage**: Efficient for large datasets  

This model transforms your data from static tables into dynamic, interconnected knowledge networks that reveal hidden patterns and relationships.
