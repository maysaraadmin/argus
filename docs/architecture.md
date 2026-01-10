# **Argus MVP Architecture Documentation**

## **Table of Contents**

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [System Architecture](#system-architecture)
4. [Component Details](#component-details)
5. [Data Flow](#data-flow)
6. [API Design](#api-design)
7. [Security Model](#security-model)
8. [Deployment Architecture](#deployment-architecture)
9. [Scaling Considerations](#scaling-considerations)
10. [Development Guidelines](#development-guidelines)

---

## **1. Overview**

### **1.1 Purpose**
Argus MVP is a minimal viable product of an open-source intelligence analysis platform inspired by Palantir Gotham. It provides core capabilities for entity resolution, knowledge graph construction, and relationship analysis using a modern Python stack.

### **1.2 Core Capabilities**
- **Knowledge Graph Management**: Store and query entities and their relationships
- **Entity Resolution**: Identify and link duplicate entities across datasets
- **Graph Visualization**: Interactive exploration of connections
- **Search & Discovery**: Find entities and trace relationships
- **Data Integration**: Import from multiple source formats

### **1.3 Target Users**
- **Intelligence Analysts**: Investigate connections between entities
- **Data Scientists**: Build and analyze network graphs
- **Developers**: Extend and customize the platform
- **Researchers**: Study relationship patterns in complex datasets

---

## **2. Architecture Principles**

### **2.1 Design Principles**
| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Modularity** | Components are loosely coupled and independently deployable | Microservices architecture with clear interfaces |
| **Simplicity** | MVP focuses on core features, avoiding over-engineering | Minimal dependencies, clear code structure |
| **Extensibility** | Easy to add new data sources, algorithms, and visualizations | Plugin architecture, configuration-driven |
| **Performance** | Responsive even with moderate dataset sizes | Caching, efficient algorithms, async operations |
| **Transparency** | All operations are understandable and auditable | Clear logging, data lineage tracking |

### **2.2 Technology Choices**
- **Language**: Python 3.10+ (data science ecosystem, rapid development)
- **Web Framework**: FastAPI (async, automatic docs, type hints)
- **UI Framework**: Streamlit (rapid prototyping, data-focused)
- **Graph Library**: NetworkX (in-memory), Neo4j (persistent option)
- **Entity Resolution**: RecordLinkage + custom algorithms
- **Visualization**: Plotly (interactive), PyVis (network graphs)

### **2.3 Trade-offs**
| Decision | Rationale | Limitation |
|----------|-----------|------------|
| **In-memory graph** | Simplicity, no external dependencies | Limited by RAM, not persistent |
| **Streamlit UI** | Fast development, data science focus | Less customizable than React |
| **Single process** | Simpler deployment, easier debugging | Limited horizontal scaling |
| **File-based config** | Easy to understand and version control | Less dynamic than database config |

---

## **3. System Architecture**

### **3.1 High-Level Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Web UI    │  │    CLI      │  │   3rd Party Apps    │  │
│  │  (Streamlit)│  │  (Click)    │  │   (via API)         │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │            │
└─────────┼────────────────┼─────────────────────┼────────────┘
          │                │                     │
          ▼                ▼                     ▼
    ┌─────────────────────────────────────────────────────┐
    │               API Gateway (FastAPI)                 │
    │  ┌─────────┐  ┌─────────┐  ┌─────────────────────┐  │
    │  │  Auth   │  │  Rate   │  │   Request/Response  │  │
    │  │  Middle-│  │ Limiting│  │     Validation      │  │
    │  │   ware  │  │         │  │                     │  │
    │  └─────────┘  └─────────┘  └─────────────────────┘  │
    └─────────────────────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Core Service  │  │   Graph Service │  │  Resolver       │
│   Layer         │  │   (Knowledge    │  │  Service        │
│                 │  │    Graph)       │  │  (Entity        │
│  • Config       │  │                 │  │   Resolution)   │
│  • Logging      │  │  • Node/Edge    │  │                 │
│  • Utilities    │  │    Management   │  │  • Fuzzy        │
│  • Exceptions   │  │  • Traversal    │  │    Matching     │
│                 │  │  • Pathfinding  │  │  • Clustering   │
│                 │  │  • Metrics      │  │  • ML Models    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Data Layer    │  │   Cache Layer   │  │   Storage       │
│   (Import/      │  │   (Redis)       │  │   Layer         │
│    Export)      │  │                 │  │                 │
│                 │  │  • Query        │  │  • In-memory    │
│  • CSV/JSON     │  │    Results      │  │    (NetworkX)   │
│  • Excel        │  │  • Session      │  │  • Persistent   │
│  • APIs         │  │    Data         │  │    (PostgreSQL/ │
│  • Databases    │  │  • Locking      │  │     Neo4j)      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### **3.2 Component Architecture**
```
argus-mvp/
├── src/                    # Source code
│   ├── argus/             # Core framework
│   │   ├── config.py      # Configuration management
│   │   ├── logging.py     # Structured logging
│   │   └── exceptions.py  # Custom exceptions
│   │
│   ├── core/              # Business logic
│   │   ├── graph.py       # Knowledge graph operations
│   │   ├── resolver.py    # Entity resolution algorithms
│   │   └── importer.py    # Data import/export
│   │
│   ├── api/               # API layer
│   │   ├── server.py      # FastAPI application
│   │   ├── auth.py        # Authentication & authorization
│   │   └── routes/        # API endpoints
│   │       ├── entities.py
│   │       ├── graph.py
│   │       └── search.py
│   │
│   ├── ui/                # User interface
│   │   └── app.py         # Streamlit application
│   │
│   └── data/              # Data models
│       ├── models.py      # Pydantic schemas
│       └── storage.py     # Data persistence
│
├── tests/                 # Test suite
├── config/                # Configuration files
├── scripts/               # Utility scripts
└── docs/                  # Documentation
```

---

## **4. Component Details**

### **4.1 Knowledge Graph Service (`src/core/graph.py`)**

#### **Responsibilities**
- Manage entity and relationship storage
- Perform graph traversals and queries
- Calculate graph metrics and statistics
- Provide visualization data structures

#### **Key Classes**
```python
class Entity:
    """Represents a node in the knowledge graph"""
    id: str            # Unique identifier
    type: str          # Entity type (person, organization, etc.)
    name: str          # Display name
    attributes: dict   # Key-value properties
    source: str        # Data source
    confidence: float  # Data quality score

class KnowledgeGraph:
    """Main graph management class"""
    def __init__(self):
        self.graph = nx.Graph()      # NetworkX graph
        self.entity_index = {}       # Entity lookup
        self.type_index = {}         # Type-based indexing
    
    # Core operations
    def add_entity(entity: Entity) -> str
    def add_relationship(source, target, type, attributes)
    def find_paths(source, target, max_depth) -> List[List[str]]
    def get_network(entity_id, depth) -> Dict
    def search_entities(query, entity_type) -> List[Entity]
```

#### **Data Structures**
```python
# Graph representation
graph = {
    "nodes": {
        "entity_1": {
            "type": "person",
            "name": "John Smith",
            "attributes": {"age": 35, "nationality": "US"},
            "degree": 3  # Number of connections
        }
    },
    "edges": {
        ("entity_1", "entity_2"): {
            "type": "works_with",
            "strength": 0.8,
            "since": "2020"
        }
    }
}
```

### **4.2 Entity Resolution Service (`src/core/resolver.py`)**

#### **Resolution Pipeline**
```
1. Data Cleaning
   └── Normalize strings, format dates, standardize values
   
2. Blocking/Indexing
   └── Group similar records to reduce comparisons
   └── Methods: phonetic, token, rule-based blocking
   
3. Comparison
   └── Calculate similarity scores for attribute pairs
   └── Use fuzzy matching algorithms
   
4. Classification
   └── Apply threshold or ML model to determine matches
   
5. Clustering
   └── Group matching entities into clusters
   
6. Resolution
   └── Create canonical entities and relationships
```

#### **Algorithms Implemented**
```python
class EntityResolver:
    # String similarity
    - Jaro-Winkler
    - Levenshtein distance
    - Token sort ratio
    
    # Numeric similarity
    - Gaussian similarity
    - Absolute difference
    
    # Machine learning
    - Random Forest classifier (optional)
    - Logistic regression
    - Clustering (DBSCAN, hierarchical)
    
    # Rule-based
    - Exact match rules
    - Pattern-based rules
    - Composite scoring
```

#### **Configuration**
```yaml
entity_resolution:
  thresholds:
    match: 0.85
    possible_match: 0.65
    non_match: 0.3
  
  weights:
    name: 0.4
    dob: 0.3
    address: 0.2
    phone: 0.1
  
  blocking:
    methods:
      - phonetic: ["name"]
      - exact: ["country", "postcode"]
      - range: ["age", "range": 5]
```

### **4.3 API Layer (`src/api/`)**

#### **REST API Design**
```
GET    /api/entities           # List entities
POST   /api/entities           # Create entity
GET    /api/entities/{id}      # Get entity details
PUT    /api/entities/{id}      # Update entity
DELETE /api/entities/{id}      # Delete entity

GET    /api/graph/{id}         # Get entity network
GET    /api/search?q=...       # Search entities
GET    /api/connections?source=...&target=...  # Find paths
POST   /api/resolve            # Resolve entities
GET    /api/stats              # System statistics
```

#### **WebSocket Endpoints**
```python
# Real-time updates
WS     /ws/updates            # Graph updates
WS     /ws/search             # Real-time search
```

#### **Response Format**
```json
{
  "status": "success",
  "data": {
    "entities": [...],
    "pagination": {
      "page": 1,
      "per_page": 50,
      "total": 1250
    }
  },
  "metadata": {
    "request_id": "req_123",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0"
  }
}
```

### **4.4 User Interface (`src/ui/app.py`)**

#### **UI Components**
```
┌─────────────────────────────────────────────────────┐
│                    Argus MVP                        │
├─────────────────────────────────────────────────────┤
│  [Dashboard] [Graph Explorer] [Entity Res] [Import] │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────────────────────┐  │
│  │  Search     │  │                              │  │
│  │  ┌───────┐  │  │     Graph Visualization      │  │
│  │  │       │  │  │      ┌───┐     ┌───┐        │  │
│  │  └───────┘  │  │      │ A ├─────┤ B │        │  │
│  │             │  │      └─┬─┘     └─┬─┘        │  │
│  │  Filters    │  │        │         │          │  │
│  │  • Type     │  │      ┌─┴─┐     ┌─┴─┐        │  │
│  │  • Date     │  │      │ C │     │ D │        │  │
│  │  • Source   │  │      └───┘     └───┘        │  │
│  └─────────────┘  └──────────────────────────────┘  │
│                                                     │
│  ┌────────────────────────────────────────────────┐ │
│  │              Entity Details                    │ │
│  │  Name: John Smith | Type: Person              │ │
│  │  Attributes: age=35, nationality=US           │ │
│  │  Connections: 3 entities                      │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

#### **Visualization Stack**
```python
# Network graphs
- Plotly: Interactive 2D/3D graphs
- PyVis: Force-directed layouts
- NetworkX: Graph algorithms and layouts

# Charts and dashboards
- Plotly Express: Statistical charts
- Streamlit components: Interactive widgets

# Maps (future)
- Folium: Geospatial visualization
- PyDeck: Large-scale data visualization
```

---

## **5. Data Flow**

### **5.1 Entity Creation Flow**
```
1. User submits entity data via UI/API/CLI
2. API validates input against schema
3. Entity is cleaned and normalized
4. Entity is added to knowledge graph
5. Indexes are updated
6. Cache is invalidated
7. Response is returned to client
8. WebSocket notifications sent (if subscribed)
```

### **5.2 Search Flow**
```
1. User enters search query
2. Query is parsed and tokenized
3. Multiple search strategies executed:
   - Exact match in indexes
   - Fuzzy match on names
   - Attribute value search
   - Full-text search (future)
4. Results are ranked by relevance
5. Pagination is applied
6. Response is cached
7. Results returned to client
```

### **5.3 Entity Resolution Flow**
```
1. Batch of entities received
2. Data cleaning and standardization
3. Blocking phase (reduce comparisons)
4. Pairwise similarity calculation
5. Match classification
6. Cluster formation
7. Canonical entity creation
8. Relationship establishment
9. Results returned and persisted
```

### **5.4 Graph Query Flow**
```
1. Request for entity network
2. Check cache for recent query
3. Execute BFS/DFS from source node
4. Collect nodes and edges within depth
5. Format for visualization
6. Cache results
7. Return network data
```

---

## **6. API Design**

### **6.1 RESTful API Principles**
- **Resource-oriented**: Entities, relationships, searches as resources
- **Stateless**: Each request contains all necessary information
- **Cacheable**: Responses indicate cacheability
- **Uniform interface**: Consistent patterns across endpoints
- **Versioned**: API version in URL path

### **6.2 Endpoint Design Patterns**

#### **Collection Endpoints**
```python
# List with filtering, sorting, pagination
GET /api/entities?type=person&sort=name&page=1&per_page=50

# Bulk operations
POST /api/entities/batch
PUT /api/entities/batch
```

#### **Action Endpoints**
```python
# Entity-specific actions
POST /api/entities/{id}/merge
POST /api/entities/{id}/export
GET /api/entities/{id}/history
```

#### **Search Endpoints**
```python
# Advanced search
POST /api/search
{
  "query": "John Smith",
  "filters": {
    "type": ["person", "organization"],
    "date_range": {"from": "2020-01-01", "to": "2023-12-31"}
  },
  "options": {
    "fuzzy": true,
    "limit": 100
  }
}
```

### **6.3 Error Handling**
```json
{
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
```

### **6.4 Rate Limiting**
```python
# Bucket-based rate limiting
rate_limits = {
    "anonymous": "100/hour",
    "user": "1000/hour",
    "api_key": "10000/hour"
}

# Headers in response
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 997
X-RateLimit-Reset: 1642242600
```

---

## **7. Security Model**

### **7.1 Authentication**
```
┌─────────┐    Token    ┌────────────┐    Validate    ┌─────────────┐
│ Client  │───────────▶│   API      │──────────────▶│ Auth Server │
└─────────┘            │  Gateway   │               │  (JWT)      │
                       └────────────┘               └─────────────┘
                              │
                              ▼ User Context
                       ┌────────────┐
                       │  Services  │
                       └────────────┘
```

### **7.2 Authorization Model**
```python
# Attribute-Based Access Control (ABAC)
class PolicyEngine:
    def can_access(user: User, resource: Resource, action: Action) -> bool:
        # Check user attributes
        # Check resource attributes
        # Check environment conditions
        # Return decision
        
# Example policy
policies = [
    {
        "effect": "allow",
        "action": ["read", "write"],
        "resource": "entities/*",
        "condition": {
            "user.department": "intel",
            "resource.classification": ["unclassified", "secret"],
            "time.between": ["09:00", "17:00"]
        }
    }
]
```

### **7.3 Data Security**
- **Encryption at rest**: Sensitive attributes encrypted
- **Encryption in transit**: TLS 1.3 for all communications
- **Audit logging**: All operations logged with user context
- **Data masking**: Sensitive data hidden based on permissions
- **Input validation**: Strict validation of all inputs

### **7.4 Security Headers**
```python
# FastAPI middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

---

## **8. Deployment Architecture**

### **8.1 Development Environment**
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://argus:argus@postgres/argus
      - REDIS_URL=redis://redis:6379/0
    depends_on: [postgres, redis]
  
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=argus
      - POSTGRES_USER=argus
      - POSTGRES_PASSWORD=argus
    
  redis:
    image: redis:7-alpine
    
  ui:
    build:
      context: .
      dockerfile: Dockerfile.ui
    ports: ["8501:8501"]
    depends_on: [api]
```

### **8.2 Production Architecture**
```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
│                    (nginx/traefik)                      │
└───────────────┬─────────────────┬───────────────────────┘
                │                 │
                ▼                 ▼
        ┌─────────────┐   ┌─────────────┐
        │   API       │   │   API       │
        │  Instance 1 │   │  Instance 2 │
        └──────┬──────┘   └──────┬──────┘
               │                 │
               └────────┬────────┘
                        │
                        ▼
        ┌─────────────────────────────────────┐
        │           Shared Services           │
        ├─────────────────────────────────────┤
        │  ┌─────────┐  ┌─────────┐  ┌─────┐ │
        │  │  Redis  │  │ Postgres│  │ Neo4j│ │
        │  │ Cluster │  │   HA    │  │ HA  │ │
        │  └─────────┘  └─────────┘  └─────┘ │
        └─────────────────────────────────────┘
                        │
                        ▼
        ┌─────────────────────────────────────┐
        │          Object Storage             │
        │         (S3/MinIO)                  │
        │  • Exported data                    │
        │  • Backups                          │
        │  • Static files                     │
        └─────────────────────────────────────┘
```

### **8.3 Kubernetes Deployment**
```yaml
# Helm values.yaml
replicaCount: 3

image:
  repository: argus/api
  tag: latest
  pullPolicy: Always

service:
  type: ClusterIP
  port: 8000

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: argus.example.com
      paths:
        - path: /
          pathType: Prefix

resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

### **8.4 Monitoring Stack**
```
┌─────────────┐    Metrics    ┌─────────────┐    Dashboard   ┌─────────────┐
│   Argus     │──────────────▶│ Prometheus  │──────────────▶│   Grafana   │
│   Services  │               │             │               │             │
└─────────────┘               └─────────────┘               └─────────────┘
        │                            │                            │
        ▼ Logs                       ▼ Alerts                     ▼ Visualization
┌─────────────┐               ┌─────────────┐               ┌─────────────────┐
│    Loki     │──────────────▶│ Alertmanager│               │ Custom Dashboards│
│             │               │             │               │ • Graph Metrics │
└─────────────┘               └─────────────┘               │ • Entity Stats  │
                                                            │ • System Health │
                                                            └─────────────────┘
```

---

## **9. Scaling Considerations**

### **9.1 Performance Optimizations**

#### **Caching Strategy**
```python
# Multi-level caching
cache_strategy = {
    "level1": {
        "type": "in-memory",
        "backend": "LRU cache",
        "ttl": "60 seconds",
        "max_size": "10,000 items"
    },
    "level2": {
        "type": "distributed",
        "backend": "Redis",
        "ttl": "5 minutes",
        "strategy": "write-through"
    }
}

# Cacheable operations
- Search results
- Graph queries
- Entity lookups
- Statistics
```

#### **Database Optimization**
```sql
-- Index strategy
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_entities_name ON entities USING gin(to_tsvector('english', name));
CREATE INDEX idx_relationships_source ON relationships(source_id);
CREATE INDEX idx_relationships_target ON relationships(target_id);

-- Partitioning
CREATE TABLE entities_y2023 PARTITION OF entities
FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
```

### **9.2 Horizontal Scaling**

#### **Stateless Components**
- API servers (scale horizontally)
- Entity resolution workers
- Import/export processors

#### **Stateful Components**
- Database (read replicas, sharding)
- Cache (Redis cluster)
- Message queue (Celery + RabbitMQ)

#### **Load Balancing Strategy**
```nginx
# nginx configuration
upstream argus_backend {
    least_conn;
    server api1:8000;
    server api2:8000;
    server api3:8000;
    
    # Health checks
    check interval=3000 rise=2 fall=3 timeout=1000;
}

location /api/ {
    proxy_pass http://argus_backend;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

### **9.3 Data Sharding Strategies**
```python
# Shard by entity type
shard_map = {
    "person": "shard_01",
    "organization": "shard_02",
    "location": "shard_03",
    "event": "shard_04"
}

# Shard by geographic region
region_sharding = {
    "US": "shard_us",
    "EU": "shard_eu",
    "APAC": "shard_apac"
}

# Time-based sharding
time_sharding = {
    "2023": "shard_2023",
    "2024": "shard_2024"
}
```

---

## **10. Development Guidelines**

### **10.1 Code Organization**
```
src/
├── __init__.py           # Package exports
├── core/                 # Business logic
│   ├── __init__.py
│   ├── graph/           # Graph operations
│   │   ├── __init__.py
│   │   ├── builder.py   # Graph construction
│   │   ├── query.py     # Graph queries
│   │   └── metrics.py   # Graph analytics
│   │
│   ├── resolution/      # Entity resolution
│   │   ├── __init__.py
│   │   ├── matcher.py   # Matching algorithms
│   │   ├── cluster.py   # Clustering algorithms
│   │   └── validator.py # Match validation
│   │
│   └── data/           # Data operations
│       ├── __init__.py
│       ├── importers/   # Data importers
│       ├── exporters/   # Data exporters
│       └── transformers/# Data transformation
│
├── api/                 # API layer
│   ├── __init__.py
│   ├── dependencies/    # FastAPI dependencies
│   ├── middleware/      # Custom middleware
│   └── routes/         # API routes
│
├── models/              # Data models
│   ├── __init__.py
│   ├── entities.py      # Entity models
│   ├── relationships.py # Relationship models
│   └── queries.py       # Query models
│
├── utils/               # Utilities
│   ├── __init__.py
│   ├── logging.py       # Logging configuration
│   ├── config.py        # Configuration management
│   └── validators.py    # Data validation
│
└── ui/                  # User interface
    ├── __init__.py
    ├── components/      # Reusable UI components
    ├── pages/          # Application pages
    └── utils/          # UI utilities
```

### **10.2 Testing Strategy**
```python
# Test pyramid
tests/
├── unit/               # 70% - Fast, isolated tests
│   ├── test_graph.py
│   ├── test_resolver.py
│   └── test_models.py
│
├── integration/        # 20% - Component integration
│   ├── test_api.py
│   ├── test_database.py
│   └── test_cache.py
│
└── e2e/               # 10% - End-to-end workflows
    ├── test_import_flow.py
    ├── test_search_flow.py
    └── test_resolution_flow.py

# Test data management
test_data/
├── fixtures/          # Test data fixtures
├── factories/         # Test data factories
└── mocks/            # Mock services
```

### **10.3 Development Workflow**
```
1. Feature Development
   └── Create feature branch
   └── Implement with TDD
   └── Add tests and documentation

2. Code Review
   └── PR created
   └── Automated checks (linting, tests)
   └── Manual review
   └── Address feedback

3. Testing
   └── Unit tests pass
   └── Integration tests pass
   └── Performance tests (if applicable)

4. Deployment
   └── Merge to main
   └── CI/CD pipeline
   └── Staging deployment
   └── Production deployment (canary/blue-green)
```

### **10.4 Performance Monitoring**
```python
# Key metrics to track
metrics = {
    "api": {
        "request_duration_seconds": "Histogram",
        "requests_total": "Counter",
        "errors_total": "Counter"
    },
    "graph": {
        "entities_total": "Gauge",
        "relationships_total": "Gauge",
        "query_duration_seconds": "Histogram"
    },
    "resolution": {
        "entities_processed_total": "Counter",
        "matches_found_total": "Counter",
        "resolution_duration_seconds": "Histogram"
    },
    "system": {
        "memory_usage_bytes": "Gauge",
        "cpu_usage_percent": "Gauge",
        "disk_usage_bytes": "Gauge"
    }
}

# Alert thresholds
alerts = {
    "api_latency": "p95 > 1s for 5m",
    "error_rate": "error rate > 1% for 5m",
    "memory_usage": "memory > 80% for 10m",
    "disk_space": "disk < 10% free"
}
```

---

## **Conclusion**

The Argus MVP architecture is designed to be **simple yet scalable**, providing a solid foundation for building a Gotham-like intelligence analysis platform. By following these architectural principles and patterns, the system can evolve from a minimal viable product to a full-featured enterprise platform while maintaining code quality, performance, and maintainability.

**Key Takeaways:**
1. **Modular design** enables independent development and scaling
2. **Clear separation of concerns** makes the system understandable
3. **Performance considerations** are built-in from the start
4. **Security is layered** throughout the architecture
5. **Monitoring and observability** are first-class concerns

This architecture provides a blueprint for building an open-source intelligence platform that can grow with your needs while remaining manageable and extensible.