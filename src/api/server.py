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
from src.core.security import security_manager, setup_demo_users, Permission, ClearanceLevel
from src.core.collaboration import collaboration_manager, AnnotationType, WorkspaceRole
from src.core.traceability import traceability_manager, SourceType, DocumentType, ConfidenceLevel
from src.core.alerting import alerting_manager, AlertSeverity, PatternType, AlertStatus
from src.core.plugins import plugin_manager, PluginType
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

# ===== SECURITY ENDPOINTS =====

@app.post("/api/auth/login")
async def login(username: str, password: str):
    """Authenticate user and return session token"""
    try:
        token = security_manager.authenticate(username, password)
        if token:
            return {"token": token, "message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/logout")
async def logout(token: str):
    """Logout user and invalidate token"""
    try:
        security_manager.logout(token)
        return {"message": "Logout successful"}
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/security/audit-log")
async def get_audit_log(token: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    """Get audit log (admin only)"""
    try:
        audit_log = security_manager.get_audit_log(token, start_date, end_date)
        return {"audit_log": audit_log}
    except Exception as e:
        logger.error(f"Failed to get audit log: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== COLLABORATION ENDPOINTS =====

@app.post("/api/workspaces")
async def create_workspace(name: str, description: str, token: str):
    """Create a new workspace"""
    try:
        session = security_manager.validate_token(token)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        workspace_id = collaboration_manager.create_workspace(name, description, session['user_id'])
        return {"workspace_id": workspace_id, "message": "Workspace created"}
    except Exception as e:
        logger.error(f"Failed to create workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workspaces")
async def get_user_workspaces(token: str):
    """Get user's workspaces"""
    try:
        session = security_manager.validate_token(token)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        workspaces = collaboration_manager.get_user_workspaces(session['user_id'])
        return {"workspaces": [ws.__dict__ for ws in workspaces]}
    except Exception as e:
        logger.error(f"Failed to get workspaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workspaces/{workspace_id}/annotations")
async def add_annotation(workspace_id: str, entity_id: Optional[str] = None, 
                       relationship_id: Optional[str] = None, annotation_type: str = "note",
                       content: str = "", token: str = ""):
    """Add annotation to workspace"""
    try:
        session = security_manager.validate_token(token)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        annotation_type_enum = AnnotationType(annotation_type)
        annotation_id = collaboration_manager.add_annotation(
            workspace_id, session['user_id'], entity_id, relationship_id,
            annotation_type_enum, content
        )
        return {"annotation_id": annotation_id, "message": "Annotation added"}
    except Exception as e:
        logger.error(f"Failed to add annotation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== TRACEABILITY ENDPOINTS =====

@app.post("/api/traceability/sources")
async def add_source_document(name: str, source_type: str, document_type: str,
                          file_path: Optional[str] = None, url: Optional[str] = None):
    """Add a source document"""
    try:
        source_type_enum = SourceType(source_type)
        document_type_enum = DocumentType(document_type)
        
        document_id = traceability_manager.add_source_document(
            name, source_type_enum, document_type_enum, file_path, url
        )
        return {"document_id": document_id, "message": "Source document added"}
    except Exception as e:
        logger.error(f"Failed to add source document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/traceability/entities/{entity_id}/sources")
async def get_entity_sources(entity_id: str, field_name: Optional[str] = None):
    """Get source documents for entity"""
    try:
        sources = traceability_manager.get_entity_sources(entity_id, field_name)
        return {"sources": sources}
    except Exception as e:
        logger.error(f"Failed to get entity sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/traceability/relationships/{relationship_id}/sources")
async def get_relationship_sources(relationship_id: str):
    """Get source documents for relationship"""
    try:
        sources = traceability_manager.get_relationship_sources(relationship_id)
        return {"sources": sources}
    except Exception as e:
        logger.error(f"Failed to get relationship sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ALERTING ENDPOINTS =====

@app.post("/api/alerts/rules")
async def create_alert_rule(name: str, description: str, pattern_type: str,
                         conditions: dict, severity: str, token: str):
    """Create an alert rule"""
    try:
        session = security_manager.validate_token(token)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        pattern_type_enum = PatternType(pattern_type)
        severity_enum = AlertSeverity(severity)
        
        rule_id = alerting_manager.create_rule(
            name, description, pattern_type_enum, conditions, severity_enum, session['user_id']
        )
        return {"rule_id": rule_id, "message": "Alert rule created"}
    except Exception as e:
        logger.error(f"Failed to create alert rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts/active")
async def get_active_alerts(token: str):
    """Get active alerts"""
    try:
        session = security_manager.validate_token(token)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        alerts = alerting_manager.get_active_alerts(session['user_id'])
        return {"alerts": [alert.__dict__ for alert in alerts]}
    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, token: str, notes: Optional[str] = None):
    """Acknowledge an alert"""
    try:
        session = security_manager.validate_token(token)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        success = alerting_manager.acknowledge_alert(alert_id, session['user_id'], notes)
        if success:
            return {"message": "Alert acknowledged"}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
    except Exception as e:
        logger.error(f"Failed to acknowledge alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== PLUGIN ENDPOINTS =====

@app.get("/api/plugins")
async def get_available_plugins():
    """Get available plugins"""
    try:
        plugins = plugin_manager.get_available_plugins()
        return {"plugins": [plugin.__dict__ for plugin in plugins]}
    except Exception as e:
        logger.error(f"Failed to get plugins: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plugins/{plugin_name}/load")
async def load_plugin(plugin_name: str):
    """Load a plugin"""
    try:
        success = plugin_manager.load_plugin(plugin_name)
        if success:
            return {"message": f"Plugin {plugin_name} loaded successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to load plugin {plugin_name}")
    except Exception as e:
        logger.error(f"Failed to load plugin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plugins/{plugin_name}/configure")
async def configure_plugin(plugin_name: str, config: dict):
    """Configure a plugin"""
    try:
        success = plugin_manager.configure_plugin(plugin_name, config)
        if success:
            return {"message": f"Plugin {plugin_name} configured successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to configure plugin {plugin_name}")
    except Exception as e:
        logger.error(f"Failed to configure plugin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize demo data
@app.on_event("startup")
async def startup_event():
    """Initialize demo data on startup"""
    try:
        # Initialize knowledge graph
        kg_instance = KnowledgeGraph()
        
        # Setup demo users
        setup_demo_users()
        
        # Start alerting monitoring
        def data_provider():
            return {
                'graph': kg_instance.graph,
                'transactions': [],  # Would come from transaction data
                'events': []  # Would come from event data
            }
        
        alerting_manager.start_monitoring(data_provider, check_interval=60)
        
        logger.info("Argus API server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")

if __name__ == "__main__":
    api_config = config.api
    uvicorn.run(
        "src.api.server:app",
        host=api_config.host,
        port=api_config.port,
        reload=api_config.debug,
        log_level="info"
    )
