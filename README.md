# Argus MVP - Open Source Intelligence Platform

Argus MVP is a minimal viable product of an open-source intelligence analysis platform inspired by Palantir Gotham. It provides core capabilities for entity resolution, knowledge graph construction, and relationship analysis using a modern Python stack.

## 🚀 Features

- **Knowledge Graph Management**: Store and query entities and their relationships
- **Entity Resolution**: Identify and link duplicate entities across datasets
- **Graph Visualization**: Interactive exploration of connections
- **Search & Discovery**: Find entities and trace relationships
- **Data Integration**: Import from multiple source formats
- **REST API**: Full-featured API for programmatic access
- **Web UI**: Streamlit-based interface for interactive analysis

## 🏗️ Architecture

Built with a modern, modular architecture:

- **Backend**: FastAPI with Python 3.10+
- **Graph Engine**: NetworkX for in-memory graph operations
- **Entity Resolution**: RecordLinkage + custom algorithms
- **Storage**: File-based with optional PostgreSQL/Redis
- **UI**: Streamlit for rapid prototyping
- **Visualization**: Plotly for interactive graphs

## 📋 Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (recommended)
- Git

## 🛠️ Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd argus
   ```

2. **Copy environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the applications**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Web UI: http://localhost:8501

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL and Redis**
   ```bash
   docker-compose up postgres redis -d
   ```

3. **Start the API server**
   ```bash
   python -m src.api.server
   ```

4. **Start the UI (in another terminal)**
   ```bash
   streamlit run src/ui/app.py
   ```

## 📖 Usage

### API Usage

```python
import requests

# Create an entity
entity_data = {
    "type": "person",
    "name": "John Doe",
    "attributes": {"age": 30, "city": "New York"},
    "source": "manual",
    "confidence": 0.9
}

response = requests.post("http://localhost:8000/api/entities", json=entity_data)
entity_id = response.json()["id"]

# Get entity network
network = requests.get(f"http://localhost:8000/api/graph/{entity_id}")
print(network.json())
```

### CLI Usage

```bash
# Initialize the system
python -m src.argus.main init

# Start the API server
python -m src.argus.main serve

# Import data
python -m src.argus.main import_data data.csv --type csv

# Find connections
python -m src.argus.main find_connection entity1 entity2 --depth 3
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

## 📊 Project Structure

```
argus/
├── src/                    # Source code
│   ├── argus/             # Core framework
│   │   ├── config.py      # Configuration management
│   │   ├── logging.py     # Structured logging
│   │   └── exceptions.py  # Custom exceptions
│   ├── core/              # Business logic
│   │   ├── graph.py       # Knowledge graph operations
│   │   ├── resolver.py    # Entity resolution algorithms
│   │   └── importer.py    # Data import/export
│   ├── api/               # API layer
│   │   ├── server.py      # FastAPI application
│   │   └── routes/        # API endpoints
│   ├── ui/                # User interface
│   │   └── app.py         # Streamlit application
│   └── data/              # Data models
│       ├── models.py      # Pydantic schemas
│       └── storage.py     # Data persistence
├── tests/                 # Test suite
├── config/                # Configuration files
├── scripts/               # Utility scripts
└── docs/                  # Documentation
```

## 🔧 Configuration

Configuration is managed through YAML files and environment variables:

- **Primary config**: `config/dev.yaml`
- **Environment variables**: `.env` (copy from `.env.example`)
- **Runtime overrides**: Environment variables with `ARGUS_` prefix

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `GET /api/entities` - List entities
- `POST /api/entities` - Create entity
- `GET /api/entities/{id}` - Get entity details
- `GET /api/graph/{id}` - Get entity network
- `POST /api/search` - Search entities
- `POST /api/resolve` - Resolve duplicate entities
- `GET /api/stats` - System statistics

## 🎯 Use Cases

### Intelligence Analysis
- Track relationships between people, organizations, and events
- Identify hidden connections through graph traversal
- Resolve duplicate entities across multiple data sources

### Data Science
- Build and analyze network graphs
- Perform entity deduplication
- Visualize complex relationships

### Research
- Study relationship patterns in complex datasets
- Trace entity lineages and provenance
- Collaborative knowledge building

## 🔒 Security

- Input validation on all endpoints
- CORS configuration
- Structured logging for audit trails
- Environment-based configuration

## 🚀 Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
# Build and deploy with production configurations
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` directory
- **Issues**: Report bugs and feature requests via GitHub Issues
- **API Health**: `GET /health` endpoint

## 🗺️ Roadmap

- [ ] PostgreSQL integration
- [ ] Advanced entity resolution algorithms
- [ ] Real-time collaboration
- [ ] Advanced visualizations
- [ ] Machine learning integration
- [ ] Multi-tenant support

## 📈 Performance

- **In-memory graph**: Fast queries for moderate datasets
- **Caching**: Redis integration for performance
- **Async operations**: Non-blocking API calls
- **Pagination**: Efficient data retrieval

---

Built with ❤️ for the open-source intelligence community.