from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Optional
import uvicorn
from datetime import datetime
import uuid

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

app = FastAPI(
    title="Argus API",
    description="Open Source Intelligence Platform",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
kg = KnowledgeGraph()
resolver = EntityResolver()

@app.get("/")
async def root():
    return {
        "name": "Argus API",
        "version": "0.1.0",
        "status": "online",
        "endpoints": {
            "entities": "/api/entities",
            "graph": "/api/graph",
            "search": "/api/search",
            "resolve": "/api/resolve"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/entities", response_model=dict)
async def create_entity(entity: EntityCreate):
    """Create a new entity"""
    entity_obj = Entity(
        id=entity.id,
        type=entity.type,
        name=entity.name,
        attributes=entity.attributes or {},
        source=entity.source
    )
    
    entity_id = kg.add_entity(entity_obj)
    return {
        "id": entity_id,
        "status": "created",
        "entity": kg.entity_index[entity_id].__dict__
    }

@app.get("/api/entities/{entity_id}")
async def get_entity(entity_id: str):
    """Get entity details"""
    if entity_id not in kg.entity_index:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    entity = kg.entity_index[entity_id]
    return {
        "id": entity_id,
        "type": entity.type,
        "name": entity.name,
        "attributes": entity.attributes,
        "connections": len(list(kg.graph.neighbors(entity_id)))
    }

@app.post("/api/relationships")
async def create_relationship(rel: RelationshipCreate):
    """Create relationship between entities"""
    try:
        kg.add_relationship(
            source_id=rel.source_id,
            target_id=rel.target_id,
            relation_type=rel.relation_type,
            attributes=rel.attributes
        )
        return {"status": "created", "relationship": rel.dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/graph/{entity_id}")
async def get_entity_network(
    entity_id: str,
    depth: int = Query(2, ge=1, le=5)
):
    """Get entity network for visualization"""
    if entity_id not in kg.graph:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return kg.get_entity_network(entity_id, depth)

@app.get("/api/search")
async def search_entities(
    q: str = Query(..., min_length=2),
    entity_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000)
):
    """Search for entities"""
    results = kg.search_entities(q, entity_type)[:limit]
    return {
        "query": q,
        "count": len(results),
        "results": results
    }

@app.get("/api/connections")
async def find_connections(
    source: str,
    target: str,
    max_depth: int = Query(3, ge=1, le=5)
):
    """Find connections between entities"""
    paths = kg.find_connections(source, target, max_depth)
    return {
        "source": source,
        "target": target,
        "max_depth": max_depth,
        "path_count": len(paths),
        "paths": paths
    }

@app.post("/api/resolve")
async def resolve_entities(request: MatchRequest):
    """Resolve duplicate entities"""
    results = resolver.resolve_batch(request.entities)
    
    # Apply matches to graph
    for match in results:
        if match.match_type == "same_entity":
            # Create alias relationship
            kg.add_relationship(
                match.entity1_id,
                match.entity2_id,
                "alias",
                {"confidence": match.confidence}
            )
    
    return {
        "matches_found": len(results),
        "matches": [
            {
                "entity1": match.entity1_id,
                "entity2": match.entity2_id,
                "score": match.similarity_score,
                "confidence": match.confidence
            }
            for match in results
        ]
    }

@app.get("/api/stats")
async def get_stats():
    """Get graph statistics"""
    return {
        "entity_count": len(kg.graph.nodes()),
        "relationship_count": len(kg.graph.edges()),
        "entity_types": {
            etype: len(ids) 
            for etype, ids in kg.type_index.items()
        },
        "density": nx.density(kg.graph) if kg.graph else 0
    }

@app.get("/visualize", response_class=HTMLResponse)
async def visualize_graph(entity_id: Optional[str] = None, depth: int = 2):
    """Visualize graph in browser"""
    if entity_id:
        data = kg.get_entity_network(entity_id, depth)
    else:
        # Show sample of graph
        nodes = list(kg.graph.nodes())[:50]
        data = {
            "nodes": [
                {
                    "id": n,
                    "label": kg.graph.nodes[n].get('name', n),
                    "type": kg.graph.nodes[n].get('type', 'unknown')
                }
                for n in nodes
            ],
            "links": [
                {
                    "source": u,
                    "target": v,
                    "type": kg.graph[u][v].get('type', 'related')
                }
                for u, v in kg.graph.subgraph(nodes).edges()
            ]
        }
    
    # Generate HTML with D3.js
    html = generate_d3_html(data)
    return HTMLResponse(content=html)

def generate_d3_html(graph_data):
    """Generate HTML with D3.js visualization"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Argus Graph Visualization</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{ margin: 0; overflow: hidden; }}
            .node {{ cursor: pointer; }}
            .link {{ stroke: #999; stroke-opacity: 0.6; }}
        </style>
    </head>
    <body>
        <svg width="100%" height="100%"></svg>
        <script>
            const graph = {graph_data};
            
            const width = window.innerWidth;
            const height = window.innerHeight;
            
            const svg = d3.select("svg")
                .attr("width", width)
                .attr("height", height);
            
            // Create simulation
            const simulation = d3.forceSimulation(graph.nodes)
                .force("link", d3.forceLink(graph.links).id(d => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2));
            
            // Draw links
            const link = svg.append("g")
                .selectAll("line")
                .data(graph.links)
                .enter().append("line")
                .attr("class", "link")
                .attr("stroke-width", 2);
            
            // Draw nodes
            const node = svg.append("g")
                .selectAll("circle")
                .data(graph.nodes)
                .enter().append("circle")
                .attr("class", "node")
                .attr("r", 10)
                .attr("fill", d => {{
                    const colors = {{
                        'person': '#ff6b6b',
                        'organization': '#4ecdc4',
                        'location': '#45b7d1',
                        'default': '#96ceb4'
                    }};
                    return colors[d.type] || colors.default;
                }})
                .call(drag(simulation));
            
            // Add labels
            const label = svg.append("g")
                .selectAll("text")
                .data(graph.nodes)
                .enter().append("text")
                .text(d => d.label || d.id)
                .attr("font-size", 12)
                .attr("dx", 12)
                .attr("dy", 4);
            
            // Update positions
            simulation.on("tick", () => {{
                link.attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                node.attr("cx", d => d.x)
                    .attr("cy", d => d.y);
                
                label.attr("x", d => d.x)
                     .attr("y", d => d.y);
            }});
            
            // Drag functions
            function drag(simulation) {{
                function dragstarted(event) {{
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    event.subject.fx = event.subject.x;
                    event.subject.fy = event.subject.y;
                }}
                
                function dragged(event) {{
                    event.subject.fx = event.x;
                    event.subject.fy = event.y;
                }}
                
                function dragended(event) {{
                    if (!event.active) simulation.alphaTarget(0);
                    event.subject.fx = null;
                    event.subject.fy = null;
                }}
                
                return d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended);
            }}
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)