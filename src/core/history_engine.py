"""
History analysis engine for Argus.
Provides specialized functionality for historical research and analysis.
"""

from datetime import date, datetime
from typing import List, Dict, Optional, Tuple, Any
import networkx as nx
from collections import defaultdict
import json

from src.data.history_models import (
    HistoricalEvent, HistoricalFigure, HistoricalOrganization,
    HistoricalPeriod, Timeline, HistoricalConnection, HistoricalSource,
    EventType, PeriodType
)


class HistoryEngine:
    """Core engine for historical analysis operations"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.events: Dict[str, HistoricalEvent] = {}
        self.figures: Dict[str, HistoricalFigure] = {}
        self.organizations: Dict[str, HistoricalOrganization] = {}
        self.periods: Dict[str, HistoricalPeriod] = {}
        self.timelines: Dict[str, Timeline] = {}
        self.sources: Dict[str, HistoricalSource] = {}
        self.connections: Dict[str, HistoricalConnection] = {}
    
    def add_event(self, event: HistoricalEvent) -> str:
        """Add a historical event to the system"""
        self.events[event.id] = event
        self.graph.add_node(event.id, type="event", data=event.dict())
        
        # Add temporal connections
        for cause_id in event.causes:
            if cause_id in self.events:
                self.graph.add_edge(cause_id, event.id, relationship="caused")
        
        for consequence_id in event.consequences:
            if consequence_id in self.events:
                self.graph.add_edge(event.id, consequence_id, relationship="led_to")
        
        return event.id
    
    def add_figure(self, figure: HistoricalFigure) -> str:
        """Add a historical figure to the system"""
        self.figures[figure.id] = figure
        self.graph.add_node(figure.id, type="figure", data=figure.dict())
        
        # Add relationship connections
        for rel_type, target_id in figure.relationships.items():
            if target_id in self.figures:
                self.graph.add_edge(figure.id, target_id, relationship=rel_type)
        
        return figure.id
    
    def add_organization(self, org: HistoricalOrganization) -> str:
        """Add a historical organization to the system"""
        self.organizations[org.id] = org
        self.graph.add_node(org.id, type="organization", data=org.dict())
        return org.id
    
    def add_period(self, period: HistoricalPeriod) -> str:
        """Add a historical period to the system"""
        self.periods[period.id] = period
        self.graph.add_node(period.id, type="period", data=period.dict())
        return period.id
    
    def create_timeline(self, timeline: Timeline) -> str:
        """Create a historical timeline"""
        self.timelines[timeline.id] = timeline
        return timeline.id
    
    def find_events_by_period(self, period_id: str) -> List[HistoricalEvent]:
        """Find all events within a historical period"""
        if period_id not in self.periods:
            return []
        
        period = self.periods[period_id]
        events_in_period = []
        
        for event in self.events.values():
            if self._date_in_period(event.date, period):
                events_in_period.append(event)
        
        return sorted(events_in_period, key=lambda e: e.date)
    
    def find_events_by_type(self, event_type: EventType) -> List[HistoricalEvent]:
        """Find all events of a specific type"""
        return [event for event in self.events.values() if event.event_type == event_type]
    
    def find_contemporaries(self, figure_id: str) -> List[HistoricalFigure]:
        """Find historical figures who lived during the same time"""
        if figure_id not in self.figures:
            return []
        
        figure = self.figures[figure_id]
        contemporaries = []
        
        for other_id, other_figure in self.figures.items():
            if other_id == figure_id:
                continue
            
            # Check if their lifespans overlapped
            if self._lifespans_overlap(figure, other_figure):
                contemporaries.append(other_figure)
        
        return contemporaries
    
    def find_causal_chain(self, event_id: str, max_depth: int = 5) -> List[List[str]]:
        """Find causal chains leading to an event"""
        if event_id not in self.events:
            return []
        
        chains = []
        
        def dfs(current_id: str, path: List[str], depth: int):
            if depth >= max_depth:
                return
            
            event = self.events.get(current_id)
            if not event or not event.causes:
                if len(path) > 1:
                    chains.append(path.copy())
                return
            
            for cause_id in event.causes:
                if cause_id in self.events:
                    path.append(cause_id)
                    dfs(cause_id, path, depth + 1)
                    path.pop()
        
        dfs(event_id, [event_id], 0)
        return chains
    
    def analyze_influence_network(self, figure_id: str) -> Dict[str, Any]:
        """Analyze the influence network of a historical figure"""
        if figure_id not in self.figures:
            return {}
        
        figure = self.figures[figure_id]
        
        # Find events they participated in
        participated_events = [
            event for event in self.events.values()
            if figure_id in event.participants
        ]
        
        # Find organizations they were affiliated with
        affiliated_orgs = [
            org for org_id, org in self.organizations.items()
            if figure_id in org.leaders or figure_id in org.affiliations
        ]
        
        # Calculate influence metrics
        influence_score = len(participated_events) * 0.3 + len(affiliated_orgs) * 0.2
        
        return {
            "figure": figure.dict(),
            "participated_events": [e.dict() for e in participated_events],
            "affiliated_organizations": [o.dict() for o in affiliated_orgs],
            "influence_score": influence_score,
            "direct_connections": list(self.graph.neighbors(figure_id))
        }
    
    def create_temporal_network(self, start_date: date, end_date: date) -> nx.Graph:
        """Create a network of entities and events within a time range"""
        temporal_graph = nx.Graph()
        
        # Add events in range
        for event in self.events.values():
            if start_date <= event.date <= end_date:
                temporal_graph.add_node(event.id, type="event", data=event.dict())
                
                # Add participants
                for participant_id in event.participants:
                    if participant_id in self.figures:
                        temporal_graph.add_node(participant_id, type="figure", 
                                             data=self.figures[participant_id].dict())
                        temporal_graph.add_edge(event.id, participant_id, 
                                              relationship="participated")
        
        return temporal_graph
    
    def get_timeline_events(self, timeline_id: str) -> List[HistoricalEvent]:
        """Get all events in a timeline, sorted by date"""
        if timeline_id not in self.timelines:
            return []
        
        timeline = self.timelines[timeline_id]
        events = []
        
        for event_id in timeline.events:
            if event_id in self.events:
                events.append(self.events[event_id])
        
        return sorted(events, key=lambda e: e.date)
    
    def search_by_keyword(self, keyword: str) -> Dict[str, List[Any]]:
        """Search across all historical entities by keyword"""
        keyword = keyword.lower()
        results = {
            "events": [],
            "figures": [],
            "organizations": [],
            "periods": []
        }
        
        # Search events
        for event in self.events.values():
            if (keyword in event.title.lower() or 
                keyword in event.description.lower() or
                any(keyword in tag.lower() for tag in event.tags)):
                results["events"].append(event)
        
        # Search figures
        for figure in self.figures.values():
            if (keyword in figure.name.lower() or 
                keyword in figure.biography.lower() or
                any(keyword in occ.lower() for occ in figure.occupation)):
                results["figures"].append(figure)
        
        # Search organizations
        for org in self.organizations.values():
            if (keyword in org.name.lower() or 
                any(keyword in achievement.lower() for achievement in org.achievements)):
                results["organizations"].append(org)
        
        # Search periods
        for period in self.periods.values():
            if (keyword in period.name.lower() or 
                keyword in period.description.lower()):
                results["periods"].append(period)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the historical database"""
        return {
            "total_events": len(self.events),
            "total_figures": len(self.figures),
            "total_organizations": len(self.organizations),
            "total_periods": len(self.periods),
            "total_timelines": len(self.timelines),
            "total_sources": len(self.sources),
            "event_types": self._count_by_type(self.events, "event_type"),
            "period_types": self._count_by_type(self.periods, "period_type"),
            "date_range": self._get_date_range()
        }
    
    def _date_in_period(self, event_date: Union[date, datetime], period: HistoricalPeriod) -> bool:
        """Check if a date falls within a period"""
        if isinstance(event_date, datetime):
            event_date = event_date.date()
        
        return period.start_date <= event_date <= (period.end_date or date.today())
    
    def _lifespans_overlap(self, fig1: HistoricalFigure, fig2: HistoricalFigure) -> bool:
        """Check if two historical figures' lifespans overlapped"""
        if not fig1.birth_date or not fig2.birth_date:
            return False
        
        fig1_death = fig1.death_date or date.today()
        fig2_death = fig2.death_date or date.today()
        
        return not (fig1_death < fig2.birth_date or fig2_death < fig1.birth_date)
    
    def _count_by_type(self, items: Dict, type_field: str) -> Dict[str, int]:
        """Count items by their type"""
        type_counts = defaultdict(int)
        for item in items.values():
            type_val = getattr(item, type_field, "unknown")
            type_counts[type_val.value if hasattr(type_val, 'value') else str(type_val)] += 1
        return dict(type_counts)
    
    def _get_date_range(self) -> Dict[str, str]:
        """Get the overall date range of the database"""
        all_dates = []
        
        for event in self.events.values():
            all_dates.append(event.date)
            if event.end_date:
                all_dates.append(event.end_date)
        
        for figure in self.figures.values():
            if figure.birth_date:
                all_dates.append(figure.birth_date)
            if figure.death_date:
                all_dates.append(figure.death_date)
        
        if not all_dates:
            return {"earliest": None, "latest": None}
        
        earliest = min(all_dates)
        latest = max(all_dates)
        
        return {
            "earliest": earliest.isoformat() if isinstance(earliest, datetime) else earliest.isoformat(),
            "latest": latest.isoformat() if isinstance(latest, datetime) else latest.isoformat()
        }
