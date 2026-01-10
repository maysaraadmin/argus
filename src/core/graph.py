import networkx as nx
import pandas as pd
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import json
import pickle
import hashlib
from datetime import datetime

from argus.config import config
from argus.logging import get_logger
from argus.exceptions import (
    EntityNotFoundError, 
    GraphError, 
    RelationshipError,
    CacheError
)

@dataclass
class Entity:
    id: str
    type: str
    name: str
    attributes: Dict[str, Any]
    source: str
    confidence: float = 1.0

class KnowledgeGraph:
    """Main graph management class for knowledge graph operations"""
    
    def __init__(self, use_cache: bool = True):
        self.logger = get_logger(__name__)
        self.graph = nx.MultiGraph()
        self.entity_index = {}
        self.type_index = defaultdict(set)
        self.attribute_index = defaultdict(set)
        
        # Redis cache for performance
        self.redis = None
        if use_cache:
            try:
                import redis
                redis_config = config.redis
                self.redis = redis.Redis(
                    host=redis_config.host,
                    port=redis_config.port,
                    db=redis_config.db,
                    password=redis_config.password,
                    decode_responses=False
                )
                # Test connection
                self.redis.ping()
                self.logger.info("Redis cache connected")
            except Exception as e:
                self.logger.warning(f"Redis cache not available: {e}")
                self.redis = None
        
    def add_entity(self, entity: Entity) -> str:
        """Add an entity to the knowledge graph"""
        try:
            entity_id = entity.id
            
            # Check if entity already exists
            if entity_id in self.entity_index:
                self.logger.warning(f"Entity {entity_id} already exists, updating")
            
            # Add to graph
            self.graph.add_node(
                entity_id,
                type=entity.type,
                name=entity.name,
                source=entity.source,
                confidence=entity.confidence,
                created_at=datetime.utcnow().isoformat(),
                **entity.attributes
            )
            
            # Update indexes
            self.entity_index[entity_id] = entity
            self.type_index[entity.type].add(entity_id)
            
            # Update attribute index
            for attr_key, attr_value in entity.attributes.items():
                if isinstance(attr_value, str):
                    self.attribute_index[f"{attr_key}:{attr_value}"].add(entity_id)
            
            # Clear cache
            self._clear_entity_cache(entity_id)
            
            self.logger.info(f"Added entity {entity_id} of type {entity.type}")
            return entity_id
            
        except Exception as e:
            self.logger.error(f"Failed to add entity {entity.id}: {e}")
            raise GraphError(f"Failed to add entity: {e}", "add_entity")
    
    def add_relationship(self, source_id: str, target_id: str, 
                        relation_type: str, attributes: Dict = None) -> None:
        """Add relationship between entities"""
        if source_id not in self.graph or target_id not in self.graph:
            raise ValueError("Both entities must exist")
        
        self.graph.add_edge(
            source_id, target_id,
            type=relation_type,
            **attributes or {}
        )
        
        # Clear cache
        if self.redis:
            self.redis.delete(f"connections:{source_id}:{target_id}")
    
    def find_connections(self, source_id: str, target_id: str, 
                        max_depth: int = 3) -> List[List[str]]:
        """Find all paths between two entities"""
        cache_key = f"paths:{source_id}:{target_id}:{max_depth}"
        
        # Check cache
        if self.redis:
            cached = self.redis.get(cache_key)
            if cached:
                return pickle.loads(cached)
        
        # Find paths
        try:
            paths = list(nx.all_simple_paths(
                self.graph, source_id, target_id, cutoff=max_depth
            ))
        except nx.NetworkXNoPath:
            paths = []
        
        # Cache result
        if self.redis and paths:
            self.redis.setex(cache_key, 300, pickle.dumps(paths))
        
        return paths
    
    def get_entity_network(self, entity_id: str, depth: int = 2) -> Dict:
        """Get entity and its connections for visualization"""
        if entity_id not in self.graph:
            return {"nodes": [], "links": []}
        
        # Get ego network (entity + neighbors within depth)
        subgraph = nx.ego_graph(self.graph, entity_id, radius=depth)
        
        nodes = []
        for node_id in subgraph.nodes():
            node_data = self.graph.nodes[node_id]
            nodes.append({
                "id": node_id,
                "label": node_data.get('name', node_id),
                "type": node_data.get('type', 'unknown'),
                "group": node_data.get('type', 'unknown'),
                **{k: v for k, v in node_data.items() if k not in ['name', 'type']}
            })
        
        links = []
        for source, target, data in subgraph.edges(data=True):
            links.append({
                "source": source,
                "target": target,
                "type": data.get('type', 'related'),
                "strength": data.get('strength', 1.0)
            })
        
        return {"nodes": nodes, "links": links}
    
    def search_entities(self, query: str, entity_type: Optional[str] = None) -> List[Dict]:
        """Search for entities by name or attributes"""
        results = []
        query_lower = query.lower()
        
        for entity_id, entity in self.entity_index.items():
            if entity_type and entity.type != entity_type:
                continue
            
            # Search in name
            if query_lower in entity.name.lower():
                results.append(self._entity_to_dict(entity))
                continue
            
            # Search in attributes
            for key, value in entity.attributes.items():
                if isinstance(value, str) and query_lower in value.lower():
                    results.append(self._entity_to_dict(entity))
                    break
        
        return results
    
    def _entity_to_dict(self, entity: Entity) -> Dict:
        """Convert entity to dictionary"""
        return {
            "id": entity.id,
            "type": entity.type,
            "name": entity.name,
            "attributes": entity.attributes,
            "degree": self.graph.degree(entity.id)
        }
    
    def export_graph(self, format: str = "json") -> Any:
        """Export the knowledge graph"""
        if format == "json":
            return nx.node_link_data(self.graph)
        elif format == "gexf":
            return nx.write_gexf(self.graph)
        elif format == "graphml":
            return nx.write_graphml(self.graph)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def visualize(self, entity_id: Optional[str] = None, depth: int = 2):
        """Visualize graph using pyvis"""
        try:
            from pyvis.network import Network
        except ImportError:
            print("Install pyvis: pip install pyvis")
            return
        
        net = Network(height="750px", width="100%", notebook=False)
        
        if entity_id:
            data = self.get_entity_network(entity_id, depth)
            for node in data["nodes"]:
                net.add_node(
                    node["id"],
                    label=node["label"],
                    group=node["type"],
                    title=json.dumps(node, indent=2)
                )
            
            for link in data["links"]:
                net.add_edge(
                    link["source"],
                    link["target"],
                    title=link["type"],
                    width=link.get("strength", 1.0)
                )
        else:
            # Show entire graph (limited to 100 nodes for performance)
            nodes_to_show = list(self.graph.nodes())[:100]
            subgraph = self.graph.subgraph(nodes_to_show)
            
            for node_id in subgraph.nodes():
                node_data = self.graph.nodes[node_id]
                net.add_node(
                    node_id,
                    label=node_data.get('name', node_id),
                    group=node_data.get('type', 'unknown')
                )
            
            for source, target, data in subgraph.edges(data=True):
                net.add_edge(source, target, title=data.get('type', ''))
        
        # Generate HTML
        net.show("graph.html")
        print("Graph saved to graph.html")
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID"""
        entity = self.entity_index.get(entity_id)
        if not entity:
            raise EntityNotFoundError(entity_id)
        return entity
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> Entity:
        """Update entity attributes"""
        if entity_id not in self.entity_index:
            raise EntityNotFoundError(entity_id)
        
        entity = self.entity_index[entity_id]
        
        # Update entity object
        if 'name' in updates:
            entity.name = updates['name']
        if 'type' in updates:
            # Update type index
            self.type_index[entity.type].discard(entity_id)
            entity.type = updates['type']
            self.type_index[entity.type].add(entity_id)
        if 'attributes' in updates:
            entity.attributes.update(updates['attributes'])
        
        # Update graph node
        node_data = self.graph.nodes[entity_id]
        node_data.update(updates)
        node_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Clear cache
        self._clear_entity_cache(entity_id)
        
        self.logger.info(f"Updated entity {entity_id}")
        return entity
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete entity from graph"""
        if entity_id not in self.entity_index:
            raise EntityNotFoundError(entity_id)
        
        # Remove from graph
        self.graph.remove_node(entity_id)
        
        # Update indexes
        entity = self.entity_index[entity_id]
        del self.entity_index[entity_id]
        self.type_index[entity.type].discard(entity_id)
        
        # Clear cache
        self._clear_entity_cache(entity_id)
        
        self.logger.info(f"Deleted entity {entity_id}")
        return True
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "entity_types": {
                entity_type: len(entities) 
                for entity_type, entities in self.type_index.items()
            },
            "density": nx.density(self.graph),
            "connected_components": nx.number_connected_components(self.graph),
            "avg_clustering": self._calculate_avg_clustering(),
        }
    
    def get_neighbors(self, entity_id: str, depth: int = 1) -> Set[str]:
        """Get neighboring entities within specified depth"""
        if entity_id not in self.graph:
            raise EntityNotFoundError(entity_id)
        
        if depth == 1:
            return set(self.graph.neighbors(entity_id))
        
        # Get neighbors within specified depth
        subgraph = nx.ego_graph(self.graph, entity_id, radius=depth)
        return set(subgraph.nodes()) - {entity_id}
    
    def _calculate_avg_clustering(self) -> float:
        """Calculate average clustering coefficient for MultiGraph"""
        try:
            # Convert to simple graph for clustering calculation
            if self.graph.is_multigraph():
                # For MultiGraph, convert to simple graph
                G = nx.Graph()
                for u, v, data in self.graph.edges(data=True):
                    G.add_edge(u, v, **data)
                return nx.average_clustering(G)
            else:
                # For simple graph, calculate directly
                return nx.average_clustering(self.graph)
        except Exception as e:
            self.logger.warning(f"Failed to calculate average clustering: {e}")
            return 0.0
    
    def _clear_entity_cache(self, entity_id: str):
        """Clear cache entries for entity"""
        if not self.redis:
            return
        
        try:
            patterns = [
                f"entity:{entity_id}",
                f"network:{entity_id}:*",
                f"paths:{entity_id}:*",
                f"paths:*:{entity_id}:*"
            ]
            
            for pattern in patterns:
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
        except Exception as e:
            self.logger.warning(f"Failed to clear cache for {entity_id}: {e}")
    
    def _get_cache_key(self, operation: str, *args) -> str:
        """Generate cache key for operation"""
        key_data = f"{operation}:" + ":".join(str(arg) for arg in args)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
        
        try:
            cached = self.redis.get(key)
            if cached:
                return pickle.loads(cached)
        except Exception as e:
            self.logger.warning(f"Cache get failed for {key}: {e}")
        
        return None
    
    def _cache_set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache"""
        if not self.redis:
            return
        
        try:
            self.redis.setex(key, ttl, pickle.dumps(value))
        except Exception as e:
            self.logger.warning(f"Cache set failed for {key}: {e}")