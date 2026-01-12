"""
Intelligence analysis methods for historical research.
Applies intelligence community techniques to historical data analysis.
"""

from datetime import date, datetime
from typing import List, Dict, Optional, Set, Tuple, Any
import networkx as nx
from collections import defaultdict, Counter
import math

from src.core.history_engine import HistoryEngine
from src.data.history_models import (
    HistoricalEvent, HistoricalFigure, HistoricalOrganization,
    HistoricalPeriod, EventType
)


class IntelligenceAnalyzer:
    """Apply intelligence analysis techniques to historical data"""
    
    def __init__(self, history_engine: HistoryEngine):
        self.engine = history_engine
        self.network = self._build_intelligence_network()
    
    def _build_intelligence_network(self) -> nx.DiGraph:
        """Build comprehensive intelligence network from historical data"""
        G = nx.DiGraph()
        
        # Add all entities as nodes
        for event_id, event in self.engine.events.items():
            G.add_node(event_id, type="event", data=event.dict())
        
        for figure_id, figure in self.engine.figures.items():
            G.add_node(figure_id, type="figure", data=figure.dict())
        
        for org_id, org in self.engine.organizations.items():
            G.add_node(org_id, type="organization", data=org.dict())
        
        # Add intelligence relationships
        for event_id, event in self.engine.events.items():
            # Causal relationships
            for cause_id in event.causes:
                if cause_id in self.engine.events:
                    G.add_edge(cause_id, event_id, relationship="causal", weight=1.0)
            
            # Participant relationships
            for participant_id in event.participants:
                if participant_id in self.engine.figures:
                    G.add_edge(participant_id, event_id, relationship="participated", weight=0.8)
                    G.add_edge(event_id, participant_id, relationship="involved", weight=0.8)
        
        # Figure relationships
        for figure_id, figure in self.engine.figures.items():
            for rel_type, target_id in figure.relationships.items():
                if target_id in self.engine.figures:
                    G.add_edge(figure_id, target_id, relationship=rel_type, weight=0.6)
            
            # Organizational affiliations
            for org_id in figure.affiliations:
                if org_id in self.engine.organizations:
                    G.add_edge(figure_id, org_id, relationship="member_of", weight=0.7)
                    G.add_edge(org_id, figure_id, relationship="has_member", weight=0.7)
        
        return G
    
    def find_key_players(self, time_period: Tuple[date, date] = None, 
                        event_types: List[EventType] = None) -> Dict[str, float]:
        """
        Identify key historical figures using centrality analysis
        Similar to identifying key players in intelligence networks
        """
        if time_period:
            # Filter network by time period
            relevant_nodes = self._get_nodes_in_period(time_period)
            subgraph = self.network.subgraph(relevant_nodes)
        else:
            subgraph = self.network
        
        # Check if subgraph has nodes
        if subgraph.number_of_nodes() == 0:
            return {}
        
        # Calculate multiple centrality measures
        centrality_scores = {}
        
        # Betweenness centrality (influence in information flow)
        betweenness = nx.betweenness_centrality(subgraph)
        
        # Eigenvector centrality (influence of connected nodes)
        try:
            eigenvector = nx.eigenvector_centrality(subgraph, max_iter=1000)
        except nx.NetworkXError:
            # Handle disconnected graphs
            eigenvector = {node: 0.0 for node in subgraph.nodes()}
        
        # Degree centrality (direct connections)
        degree = nx.degree_centrality(subgraph)
        
        # Combined intelligence score
        for node in subgraph.nodes():
            if subgraph.nodes[node].get('type') == 'figure':
                score = (
                    betweenness.get(node, 0) * 0.4 +
                    eigenvector.get(node, 0) * 0.4 +
                    degree.get(node, 0) * 0.2
                )
                centrality_scores[node] = score
        
        # Sort by influence score
        return dict(sorted(centrality_scores.items(), key=lambda x: x[1], reverse=True))
    
    def analyze_influence_networks(self, figure_id: str) -> Dict[str, Any]:
        """
        Comprehensive influence analysis similar to intelligence network analysis
        """
        if figure_id not in self.engine.figures:
            return {}
        
        figure = self.engine.figures[figure_id]
        
        # Direct network (1-hop)
        direct_connections = list(self.network.neighbors(figure_id))
        
        # Extended network (2-hop)
        extended_network = set()
        for neighbor in direct_connections:
            extended_network.update(self.network.neighbors(neighbor))
        extended_network.discard(figure_id)
        
        # Influence pathways
        influence_paths = self._find_influence_paths(figure_id)
        
        # Network metrics
        try:
            metrics = {
                "direct_connections": len(direct_connections),
                "extended_reach": len(extended_network),
                "betweenness_centrality": nx.betweenness_centrality(self.network).get(figure_id, 0),
                "eigenvector_centrality": nx.eigenvector_centrality(self.network, max_iter=1000).get(figure_id, 0),
                "clustering_coefficient": nx.clustering(self.network.to_undirected(), figure_id),
            }
        except nx.NetworkXError:
            # Handle network analysis errors
            metrics = {
                "direct_connections": len(direct_connections),
                "extended_reach": len(extended_network),
                "betweenness_centrality": 0.0,
                "eigenvector_centrality": 0.0,
                "clustering_coefficient": 0.0,
            }
        
        # Causal influence
        causal_events = self._analyze_causal_influence(figure_id)
        
        return {
            "figure": figure.dict(),
            "direct_connections": direct_connections,
            "extended_network": list(extended_network),
            "influence_paths": influence_paths,
            "network_metrics": metrics,
            "causal_influence": causal_events
        }
    
    def detect_historical_patterns(self, period: HistoricalPeriod) -> Dict[str, Any]:
        """
        Pattern analysis similar to intelligence pattern recognition
        """
        events = self.engine.find_events_by_period(period.id)
        
        # Event type patterns
        event_types = Counter([event.event_type for event in events])
        
        # Temporal patterns (yearly frequency)
        yearly_frequency = defaultdict(int)
        for event in events:
            year = event.date.year
            yearly_frequency[year] += 1
        
        # Location patterns
        locations = Counter([event.location for event in events])
        
        # Participant patterns
        participant_frequency = defaultdict(int)
        for event in events:
            for participant in event.participants:
                if participant in self.engine.figures:
                    participant_frequency[participant] += 1
        
        # Detect anomalies (unusual spikes)
        year_avg = sum(yearly_frequency.values()) / len(yearly_frequency) if yearly_frequency else 0
        anomalous_years = {
            year: count for year, count in yearly_frequency.items() 
            if count > year_avg * 2  # More than 2x average
        }
        
        return {
            "period": period.dict(),
            "event_patterns": dict(event_types),
            "temporal_patterns": dict(yearly_frequency),
            "location_patterns": dict(locations),
            "key_participants": dict(sorted(participant_frequency.items(), 
                                         key=lambda x: x[1], reverse=True)[:10]),
            "anomalous_years": anomalous_years,
            "total_events": len(events)
        }
    
    def trace_causal_chains(self, event_id: str, max_depth: int = 5) -> List[Dict[str, Any]]:
        """
        Advanced causal chain analysis like intelligence causal mapping
        """
        if event_id not in self.engine.events:
            return []
        
        chains = []
        visited = set()
        
        def dfs(current_id: str, path: List[str], depth: int, strength: float):
            if depth >= max_depth or current_id in visited:
                if len(path) > 1:
                    chains.append({
                        "chain": path.copy(),
                        "strength": strength,
                        "length": len(path)
                    })
                return
            
            visited.add(current_id)
            event = self.engine.events.get(current_id)
            
            if not event or not event.causes:
                if len(path) > 1:
                    chains.append({
                        "chain": path.copy(),
                        "strength": strength,
                        "length": len(path)
                    })
                visited.remove(current_id)
                return
            
            for cause_id in event.causes:
                if cause_id in self.engine.events:
                    path.append(cause_id)
                    # Calculate chain strength based on evidence
                    new_strength = strength * 0.9  # Decay factor
                    dfs(cause_id, path, depth + 1, new_strength)
                    path.pop()
            
            visited.remove(current_id)
        
        dfs(event_id, [event_id], 0, 1.0)
        
        # Sort by strength and length
        chains.sort(key=lambda x: (x["strength"], x["length"]), reverse=True)
        
        return chains[:10]  # Return top 10 chains
    
    def analyze_geospatial_intelligence(self, region: str = None, 
                                     time_period: Tuple[date, date] = None) -> Dict[str, Any]:
        """
        Geospatial intelligence analysis for historical data
        """
        events = list(self.engine.events.values())
        
        # Filter by region if specified
        if region:
            events = [e for e in events if region.lower() in e.location.lower()]
        
        # Filter by time period if specified
        if time_period:
            start_date, end_date = time_period
            events = [e for e in events if start_date <= e.date <= end_date]
        
        # Location frequency analysis
        location_frequency = Counter([event.location for event in events])
        
        # Event clustering by location
        location_events = defaultdict(list)
        for event in events:
            location_events[event.location].append(event)
        
        # Strategic importance scoring
        strategic_scores = {}
        for location, loc_events in location_events.items():
            score = 0
            # More events = higher importance
            score += len(loc_events) * 0.3
            # Military events = higher strategic value
            military_events = [e for e in loc_events if e.event_type == EventType.MILITARY]
            score += len(military_events) * 0.5
            # Political events = strategic importance
            political_events = [e for e in loc_events if e.event_type == EventType.POLITICAL]
            score += len(political_events) * 0.4
            
            strategic_scores[location] = score
        
        # Movement patterns (if coordinates available)
        movement_patterns = self._analyze_movement_patterns(events)
        
        return {
            "total_events": len(events),
            "location_frequency": dict(location_frequency.most_common(20)),
            "strategic_locations": dict(sorted(strategic_scores.items(), 
                                              key=lambda x: x[1], reverse=True)[:10]),
            "location_clusters": {loc: len(events) for loc, events in location_events.items()},
            "movement_patterns": movement_patterns
        }
    
    def threat_assessment_analysis(self, period: HistoricalPeriod) -> Dict[str, Any]:
        """
        Threat assessment approach to historical conflicts and crises
        """
        events = self.engine.find_events_by_period(period.id)
        
        # Identify threat events
        threat_events = [
            event for event in events 
            if event.event_type in [EventType.MILITARY, EventType.POLITICAL]
        ]
        
        # Threat severity scoring
        threat_scores = {}
        for event in threat_events:
            score = 0
            
            # Military events = higher threat
            if event.event_type == EventType.MILITARY:
                score += 0.7
            
            # Events with many participants = larger scale
            score += min(len(event.participants) * 0.1, 0.3)
            
            # Events with many consequences = high impact
            score += min(len(event.consequences) * 0.1, 0.3)
            
            threat_scores[event.id] = score
        
        # Threat clustering (related threats)
        threat_clusters = self._cluster_threats(threat_events)
        
        # Early warning indicators (precursor events)
        warning_indicators = self._find_warning_indicators(threat_events)
        
        return {
            "period": period.dict(),
            "total_threats": len(threat_events),
            "threat_scores": dict(sorted(threat_scores.items(), 
                                       key=lambda x: x[1], reverse=True)[:10]),
            "threat_clusters": threat_clusters,
            "warning_indicators": warning_indicators,
            "high_risk_events": [e.dict() for e_id, e in self.engine.events.items() 
                               if e_id in threat_scores and threat_scores[e_id] > 0.7]
        }
    
    def _get_nodes_in_period(self, time_period: Tuple[date, date]) -> Set[str]:
        """Get all entities active within a time period"""
        start_date, end_date = time_period
        relevant_nodes = set()
        
        # Add events in period
        for event_id, event in self.engine.events.items():
            if start_date <= event.date <= end_date:
                relevant_nodes.add(event_id)
        
        # Add figures active in period
        for figure_id, figure in self.engine.figures.items():
            if ((figure.birth_date and figure.birth_date <= end_date) and
                (figure.death_date is None or figure.death_date >= start_date)):
                relevant_nodes.add(figure_id)
        
        return relevant_nodes
    
    def _find_influence_paths(self, figure_id: str) -> List[List[str]]:
        """Find paths of influence through the network"""
        paths = []
        
        # Find paths to events
        for event_id in self.engine.events:
            try:
                if nx.has_path(self.network, figure_id, event_id):
                    path = nx.shortest_path(self.network, figure_id, event_id)
                    if len(path) > 2:  # Only meaningful paths
                        paths.append(path)
            except:
                continue
        
        return paths[:20]  # Limit to top 20 paths
    
    def _analyze_causal_influence(self, figure_id: str) -> Dict[str, Any]:
        """Analyze how a figure influenced historical events"""
        influenced_events = []
        
        for event_id, event in self.engine.events.items():
            if figure_id in event.participants:
                influenced_events.append({
                    "event": event.dict(),
                    "role": "participant",
                    "impact_score": len(event.consequences) * 0.3
                })
        
        # Sort by impact
        influenced_events.sort(key=lambda x: x["impact_score"], reverse=True)
        
        return {
            "total_influenced_events": len(influenced_events),
            "top_influences": influenced_events[:10]
        }
    
    def _analyze_movement_patterns(self, events: List[HistoricalEvent]) -> Dict[str, Any]:
        """Analyze geographic movement patterns"""
        movements = []
        
        # Sort events by date
        sorted_events = sorted(events, key=lambda e: e.date)
        
        # Track location changes over time
        location_sequence = [event.location for event in sorted_events]
        unique_locations = list(dict.fromkeys(location_sequence))  # Preserve order, remove duplicates
        
        return {
            "location_sequence": unique_locations,
            "total_locations": len(unique_locations),
            "movement_frequency": len(unique_locations) / len(events) if events else 0
        }
    
    def _cluster_threats(self, threat_events: List[HistoricalEvent]) -> List[List[str]]:
        """Cluster related threats"""
        clusters = []
        processed = set()
        
        for event in threat_events:
            if event.id in processed:
                continue
            
            cluster = [event.id]
            processed.add(event.id)
            
            # Find related threats
            for other_event in threat_events:
                if other_event.id in processed:
                    continue
                
                # Check if events are related (same location, participants, or causal links)
                if (event.location == other_event.location or
                    set(event.participants) & set(other_event.participants) or
                    other_event.id in event.causes or
                    event.id in other_event.causes):
                    
                    cluster.append(other_event.id)
                    processed.add(other_event.id)
            
            if len(cluster) > 1:
                clusters.append(cluster)
        
        return clusters
    
    def _find_warning_indicators(self, threat_events: List[HistoricalEvent]) -> List[Dict[str, Any]]:
        """Find early warning indicators before major threats"""
        indicators = []
        
        for event in threat_events:
            # Look for precursor events
            for cause_id in event.causes:
                if cause_id in self.engine.events:
                    cause_event = self.engine.events[cause_id]
                    indicators.append({
                        "warning_event": cause_event.dict(),
                        "threatened_event": event.dict(),
                        "warning_period": (event.date - cause_event.date).days
                    })
        
        return indicators
