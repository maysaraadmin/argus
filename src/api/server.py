#!/usr/bin/env python3
"""
FastAPI server for Argus MVP
"""
from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Optional
import uvicorn
from datetime import datetime
import uuid
import time

from argus.config import config
from argus.logging import get_logger, setup_logging
from argus.exceptions import (
    EntityNotFoundError, 
    GraphError, 
    RelationshipError,
    ValidationError,
    ArgusException
)
from src.core.graph import KnowledgeGraph, Entity
from src.core.resolver import EntityResolver
from src.data.models import (
    EntityCreate, EntityUpdate, EntityResponse,
    RelationshipCreate, RelationshipResponse,
    SearchQuery, MatchRequest, MatchResponse,
    GraphResponse, PathRequest, PathResponse,
    NetworkRequest, StatsResponse,
    ErrorResponse, PaginatedResponse
)
from src.data.storage import storage

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Argus API",
    description="Open Source Intelligence Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
kg = KnowledgeGraph()
resolver = EntityResolver()

# Exception handlers
@app.exception_handler(ArgusException)
async def argus_exception_handler(request: Request, exc: ArgusException):
    """Handle custom Argus exceptions"""
    return JSONResponse(
        status_code=400,
        content=exc.to_dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
                "details": str(exc)
            }
        }
    )

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Argus API",
        "version": "0.1.0",
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "entities": "/api/entities",
            "relationships": "/api/relationships",
            "graph": "/api/graph",
            "search": "/api/search",
            "resolve": "/api/resolve",
            "stats": "/api/stats"
        }
    }

# Health check
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }

# Entity endpoints
@app.post("/api/entities", response_model=EntityResponse)
async def create_entity(entity: EntityCreate):
    """Create a new entity"""
    try:
        # Generate ID if not provided
        entity_id = entity.id or str(uuid.uuid4())
        
        # Create entity object
        entity_obj = Entity(
            id=entity_id,
            type=entity.type.value,
            name=entity.name,
            attributes=entity.attributes,
            source=entity.source,
            confidence=entity.confidence
        )
        
        # Add to knowledge graph
        kg.add_entity(entity_obj)
        
        # Get created entity
        created_entity = kg.get_entity(entity_id)
        
        logger.info(f"Created entity {entity_id}")
        return EntityResponse(
            id=entity_id,
            type=entity.type,
            name=entity.name,
            attributes=entity.attributes,
            source=entity.source,
            confidence=entity.confidence,
            degree=kg.graph.degree(entity_id),
            created_at=datetime.fromisoformat(created_entity.created_at.replace('Z', '+00:00'))
        )
        
    except Exception as e:
        logger.error(f"Failed to create entity: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: str):
    """Get entity details"""
    try:
        entity = kg.get_entity(entity_id)
        
        return EntityResponse(
            id=entity.id,
            type=entity.type,
            name=entity.name,
            attributes=entity.attributes,
            source=entity.source,
            confidence=entity.confidence,
            degree=kg.graph.degree(entity_id),
            created_at=datetime.fromisoformat(entity.created_at.replace('Z', '+00:00'))
        )
        
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    except Exception as e:
        logger.error(f"Failed to get entity {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/entities/{entity_id}", response_model=EntityResponse)
async def update_entity(entity_id: str, updates: EntityUpdate):
    """Update an entity"""
    try:
        # Prepare update data
        update_data = {}
        if updates.name is not None:
            update_data['name'] = updates.name
        if updates.attributes is not None:
            update_data['attributes'] = updates.attributes
        if updates.confidence is not None:
            update_data['confidence'] = updates.confidence
        
        # Update entity
        updated_entity = kg.update_entity(entity_id, update_data)
        
        return EntityResponse(
            id=updated_entity.id,
            type=updated_entity.type,
            name=updated_entity.name,
            attributes=updated_entity.attributes,
            source=updated_entity.source,
            confidence=updated_entity.confidence,
            degree=kg.graph.degree(entity_id),
            created_at=datetime.fromisoformat(updated_entity.created_at.replace('Z', '+00:00')),
            updated_at=datetime.utcnow()
        )
        
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    except Exception as e:
        logger.error(f"Failed to update entity {entity_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/entities/{entity_id}")
async def delete_entity(entity_id: str):
    """Delete an entity"""
    try:
        kg.delete_entity(entity_id)
        logger.info(f"Deleted entity {entity_id}")
        return {"status": "deleted", "entity_id": entity_id}
        
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    except Exception as e:
        logger.error(f"Failed to delete entity {entity_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/entities", response_model=PaginatedResponse)
async def list_entities(
    entity_type: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """List entities with pagination and filters"""
    try:
        # Build filters
        filters = {}
        if entity_type:
            filters['type'] = entity_type
        if source:
            filters['source'] = source
        
        # Get entities from storage
        entities = storage.list_entities(filters, limit + offset)
        
        # Apply pagination
        paginated_entities = entities[offset:offset + limit]
        
        # Convert to response models
        entity_responses = []
        for entity in paginated_entities:
            entity_responses.append(EntityResponse(
                id=entity['id'],
                type=entity['type'],
                name=entity['name'],
                attributes=entity.get('attributes', {}),
                source=entity.get('source', 'manual'),
                confidence=entity.get('confidence', 1.0),
                degree=kg.graph.degree(entity['id']),
                created_at=datetime.fromisoformat(entity['created_at'].replace('Z', '+00:00'))
            ))
        
        return PaginatedResponse(
            items=entity_responses,
            total=len(entities),
            page=offset // limit + 1,
            per_page=limit,
            pages=(len(entities) + limit - 1) // limit
        )
        
    except Exception as e:
        logger.error(f"Failed to list entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Relationship endpoints
@app.post("/api/relationships", response_model=RelationshipResponse)
async def create_relationship(relationship: RelationshipCreate):
    """Create a relationship between entities"""
    try:
        # Add relationship to knowledge graph
        kg.add_relationship(
            source_id=relationship.source_id,
            target_id=relationship.target_id,
            relation_type=relationship.type.value,
            attributes=relationship.attributes
        )
        
        relationship_id = str(uuid.uuid4())
        
        logger.info(f"Created relationship {relationship_id}")
        return RelationshipResponse(
            id=relationship_id,
            source_id=relationship.source_id,
            target_id=relationship.target_id,
            type=relationship.type,
            attributes=relationship.attributes,
            strength=relationship.strength,
            created_at=datetime.utcnow()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/relationships")
async def get_relationships(entity_id: Optional[str] = None):
    """Get relationships, optionally filtered by entity"""
    try:
        relationships = storage.get_relationships(entity_id)
        
        # Convert to response models
        relationship_responses = []
        for rel in relationships:
            relationship_responses.append(RelationshipResponse(
                id=rel['id'],
                source_id=rel['source_id'],
                target_id=rel['target_id'],
                type=rel['type'],
                attributes=rel.get('attributes', {}),
                strength=rel.get('strength', 1.0),
                created_at=datetime.fromisoformat(rel['created_at'].replace('Z', '+00:00'))
            ))
        
        return {"relationships": relationship_responses, "count": len(relationship_responses)}
        
    except Exception as e:
        logger.error(f"Failed to get relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Graph endpoints
@app.get("/api/graph/{entity_id}", response_model=GraphResponse)
async def get_entity_network(
    entity_id: str,
    depth: int = Query(2, ge=1, le=5),
    include_attributes: bool = True
):
    """Get entity network for visualization"""
    try:
        network_data = kg.get_entity_network(entity_id, depth)
        
        return GraphResponse(
            nodes=network_data["nodes"],
            links=network_data["links"],
            metadata={
                "entity_id": entity_id,
                "depth": depth,
                "node_count": len(network_data["nodes"]),
                "link_count": len(network_data["links"]),
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    except Exception as e:
        logger.error(f"Failed to get entity network: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/graph/paths", response_model=PathResponse)
async def find_paths(request: PathRequest):
    """Find paths between entities"""
    try:
        paths = kg.find_connections(request.source_id, request.target_id, request.max_depth)
        
        return PathResponse(
            paths=paths,
            metadata={
                "source_id": request.source_id,
                "target_id": request.target_id,
                "max_depth": request.max_depth,
                "path_count": len(paths),
                "path_type": request.path_type,
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to find paths: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Search endpoints
@app.post("/api/search", response_model=PaginatedResponse)
async def search_entities(query: SearchQuery):
    """Search for entities"""
    try:
        results = kg.search_entities(query.query, query.entity_type.value if query.entity_type else None)
        
        # Apply filters
        if query.filters:
            for key, value in query.filters.items():
                if isinstance(value, dict):
                    if 'min' in value and 'max' in value:
                        # Range filter
                        results = [
                            r for r in results 
                            if key in r.get('attributes', {}) and 
                            value['min'] <= r['attributes'][key] <= value['max']
                        ]
                else:
                    # Exact match filter
                    results = [
                        r for r in results 
                        if key in r.get('attributes', {}) and 
                        r['attributes'][key] == value
                    ]
        
        # Apply pagination
        total = len(results)
        paginated_results = results[query.offset:query.offset + query.limit]
        
        return PaginatedResponse(
            items=paginated_results,
            total=total,
            page=query.offset // query.limit + 1,
            per_page=query.limit,
            pages=(total + query.limit - 1) // query.limit
        )
        
    except Exception as e:
        logger.error(f"Failed to search entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Entity resolution endpoints
@app.post("/api/resolve", response_model=List[MatchResponse])
async def resolve_entities(request: MatchRequest):
    """Resolve duplicate entities"""
    try:
        # Use custom threshold if provided
        if request.threshold is not None:
            original_threshold = resolver.config.similarity_threshold
            resolver.config.similarity_threshold = request.threshold
        
        # Perform resolution
        matches = resolver.resolve_batch(request.entities)
        
        # Restore original threshold
        if request.threshold is not None:
            resolver.config.similarity_threshold = original_threshold
        
        # Convert to response models
        match_responses = []
        for match in matches:
            match_responses.append(MatchResponse(
                entity1_id=match.entity1_id,
                entity2_id=match.entity2_id,
                similarity_score=match.similarity_score,
                match_type=match.match_type,
                confidence=match.confidence,
                match_details=match.match_details
            ))
        
        logger.info(f"Resolved {len(matches)} matches from {len(request.entities)} entities")
        return match_responses
        
    except Exception as e:
        logger.error(f"Failed to resolve entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Statistics endpoint
@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get graph statistics"""
    try:
        stats = kg.get_graph_stats()
        
        return StatsResponse(
            nodes=stats["nodes"],
            edges=stats["edges"],
            entity_types=stats["entity_types"],
            density=stats["density"],
            connected_components=stats["connected_components"],
            avg_clustering=stats["avg_clustering"]
        )
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run server
if __name__ == "__main__":
    api_config = config.api
    uvicorn.run(
        "src.api.server:app",
        host=api_config.host,
        port=api_config.port,
        reload=api_config.debug,
        log_level="info"
    )
