"""
History API routes for Argus.
Provides REST endpoints for historical data management and analysis.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional, Any
from datetime import date, datetime
from pydantic import BaseModel

from src.core.history_engine import HistoryEngine
from src.data.history_models import (
    HistoricalEvent, HistoricalFigure, HistoricalOrganization,
    HistoricalPeriod, Timeline, EventType, PeriodType
)

router = APIRouter(prefix="/api/history", tags=["history"])
history_engine = HistoryEngine()


# Pydantic models for API requests/responses
class EventCreate(BaseModel):
    title: str
    description: str
    event_type: EventType
    date: str  # ISO date string
    end_date: Optional[str] = None
    location: str
    coordinates: Optional[List[float]] = None
    participants: List[str] = []
    causes: List[str] = []
    consequences: List[str] = []
    sources: List[str] = []
    significance: str = ""
    tags: List[str] = []


class FigureCreate(BaseModel):
    name: str
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    birth_place: Optional[str] = None
    death_place: Optional[str] = None
    occupation: List[str] = []
    achievements: List[str] = []
    relationships: Dict[str, str] = {}
    affiliations: List[str] = []
    era: str
    biography: str = ""
    portrait_url: Optional[str] = None


class OrganizationCreate(BaseModel):
    name: str
    organization_type: str
    founded_date: Optional[str] = None
    dissolved_date: Optional[str] = None
    headquarters: Optional[str] = None
    territory: List[str] = []
    leaders: List[str] = []
    achievements: List[str] = []
    conflicts: List[str] = []


class PeriodCreate(BaseModel):
    name: str
    description: str
    start_date: str
    end_date: Optional[str] = None
    period_type: PeriodType
    region: str
    key_characteristics: List[str] = []
    related_periods: List[str] = []


class TimelineCreate(BaseModel):
    name: str
    description: str
    start_date: str
    end_date: str
    events: List[str] = []
    periods: List[str] = []
    focus: str = ""
    created_by: str
    is_public: bool = False


# Event endpoints
@router.post("/events", response_model=Dict[str, str])
async def create_event(event_data: EventCreate):
    """Create a new historical event"""
    try:
        # Parse dates
        event_date = datetime.fromisoformat(event_data.date).date()
        end_date = None
        if event_data.end_date:
            end_date = datetime.fromisoformat(event_data.end_date).date()
        
        event = HistoricalEvent(
            title=event_data.title,
            description=event_data.description,
            event_type=event_data.event_type,
            date=event_date,
            end_date=end_date,
            location=event_data.location,
            coordinates=tuple(event_data.coordinates) if event_data.coordinates else None,
            participants=event_data.participants,
            causes=event_data.causes,
            consequences=event_data.consequences,
            sources=event_data.sources,
            significance=event_data.significance,
            tags=event_data.tags
        )
        
        event_id = history_engine.add_event(event)
        return {"event_id": event_id, "status": "created"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/events", response_model=List[Dict])
async def get_events(
    event_type: Optional[EventType] = None,
    limit: int = Query(default=50, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Get historical events with optional filtering"""
    try:
        if event_type:
            events = history_engine.find_events_by_type(event_type)
        else:
            events = list(history_engine.events.values())
        
        # Sort by date and paginate
        events.sort(key=lambda e: e.date)
        paginated_events = events[offset:offset + limit]
        
        return [event.dict() for event in paginated_events]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}", response_model=Dict)
async def get_event(event_id: str):
    """Get a specific historical event"""
    event = history_engine.events.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event.dict()


# Figure endpoints
@router.post("/figures", response_model=Dict[str, str])
async def create_figure(figure_data: FigureCreate):
    """Create a new historical figure"""
    try:
        # Parse dates
        birth_date = None
        death_date = None
        if figure_data.birth_date:
            birth_date = datetime.fromisoformat(figure_data.birth_date).date()
        if figure_data.death_date:
            death_date = datetime.fromisoformat(figure_data.death_date).date()
        
        figure = HistoricalFigure(
            name=figure_data.name,
            birth_date=birth_date,
            death_date=death_date,
            birth_place=figure_data.birth_place,
            death_place=figure_data.death_place,
            occupation=figure_data.occupation,
            achievements=figure_data.achievements,
            relationships=figure_data.relationships,
            affiliations=figure_data.affiliations,
            era=figure_data.era,
            biography=figure_data.biography,
            portrait_url=figure_data.portrait_url
        )
        
        figure_id = history_engine.add_figure(figure)
        return {"figure_id": figure_id, "status": "created"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/figures", response_model=List[Dict])
async def get_figures(
    era: Optional[str] = None,
    limit: int = Query(default=50, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Get historical figures with optional filtering"""
    try:
        figures = list(history_engine.figures.values())
        
        if era:
            figures = [fig for fig in figures if fig.era == era]
        
        # Sort by name and paginate
        figures.sort(key=lambda f: f.name)
        paginated_figures = figures[offset:offset + limit]
        
        return [figure.dict() for figure in paginated_figures]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/figures/{figure_id}", response_model=Dict)
async def get_figure(figure_id: str):
    """Get a specific historical figure"""
    figure = history_engine.figures.get(figure_id)
    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")
    
    return figure.dict()


@router.get("/figures/{figure_id}/contemporaries", response_model=List[Dict])
async def get_figure_contemporaries(figure_id: str):
    """Get contemporaries of a historical figure"""
    contemporaries = history_engine.find_contemporaries(figure_id)
    return [contemporary.dict() for contemporary in contemporaries]


@router.get("/figures/{figure_id}/influence", response_model=Dict)
async def get_figure_influence(figure_id: str):
    """Get influence analysis for a historical figure"""
    influence = history_engine.analyze_influence_network(figure_id)
    if not influence:
        raise HTTPException(status_code=404, detail="Figure not found")
    
    return influence


# Organization endpoints
@router.post("/organizations", response_model=Dict[str, str])
async def create_organization(org_data: OrganizationCreate):
    """Create a new historical organization"""
    try:
        # Parse dates
        founded_date = None
        dissolved_date = None
        if org_data.founded_date:
            founded_date = datetime.fromisoformat(org_data.founded_date).date()
        if org_data.dissolved_date:
            dissolved_date = datetime.fromisoformat(org_data.dissolved_date).date()
        
        organization = HistoricalOrganization(
            name=org_data.name,
            organization_type=org_data.organization_type,
            founded_date=founded_date,
            dissolved_date=dissolved_date,
            headquarters=org_data.headquarters,
            territory=org_data.territory,
            leaders=org_data.leaders,
            achievements=org_data.achievements,
            conflicts=org_data.conflicts
        )
        
        org_id = history_engine.add_organization(organization)
        return {"organization_id": org_id, "status": "created"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/organizations", response_model=List[Dict])
async def get_organizations(
    org_type: Optional[str] = None,
    limit: int = Query(default=50, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Get historical organizations with optional filtering"""
    try:
        organizations = list(history_engine.organizations.values())
        
        if org_type:
            organizations = [org for org in organizations if org.organization_type == org_type]
        
        # Sort by name and paginate
        organizations.sort(key=lambda o: o.name)
        paginated_orgs = organizations[offset:offset + limit]
        
        return [org.dict() for org in paginated_orgs]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Period endpoints
@router.post("/periods", response_model=Dict[str, str])
async def create_period(period_data: PeriodCreate):
    """Create a new historical period"""
    try:
        # Parse dates
        start_date = datetime.fromisoformat(period_data.start_date).date()
        end_date = None
        if period_data.end_date:
            end_date = datetime.fromisoformat(period_data.end_date).date()
        
        period = HistoricalPeriod(
            name=period_data.name,
            description=period_data.description,
            start_date=start_date,
            end_date=end_date,
            period_type=period_data.period_type,
            region=period_data.region,
            key_characteristics=period_data.key_characteristics,
            related_periods=period_data.related_periods
        )
        
        period_id = history_engine.add_period(period)
        return {"period_id": period_id, "status": "created"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/periods/{period_id}/events", response_model=List[Dict])
async def get_period_events(period_id: str):
    """Get events within a historical period"""
    events = history_engine.find_events_by_period(period_id)
    return [event.dict() for event in events]


# Timeline endpoints
@router.post("/timelines", response_model=Dict[str, str])
async def create_timeline(timeline_data: TimelineCreate):
    """Create a new historical timeline"""
    try:
        # Parse dates
        start_date = datetime.fromisoformat(timeline_data.start_date).date()
        end_date = datetime.fromisoformat(timeline_data.end_date).date()
        
        timeline = Timeline(
            name=timeline_data.name,
            description=timeline_data.description,
            start_date=start_date,
            end_date=end_date,
            events=timeline_data.events,
            periods=timeline_data.periods,
            focus=timeline_data.focus,
            created_by=timeline_data.created_by,
            is_public=timeline_data.is_public
        )
        
        timeline_id = history_engine.create_timeline(timeline)
        return {"timeline_id": timeline_id, "status": "created"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/timelines/{timeline_id}/events", response_model=List[Dict])
async def get_timeline_events(timeline_id: str):
    """Get events in a timeline"""
    events = history_engine.get_timeline_events(timeline_id)
    return [event.dict() for event in events]


# Analysis endpoints
@router.get("/search", response_model=Dict[str, List[Dict]])
async def search_history(keyword: str = Query(..., min_length=1)):
    """Search across all historical entities"""
    results = history_engine.search_by_keyword(keyword)
    
    # Convert to JSON-serializable format
    return {
        "events": [event.dict() for event in results["events"]],
        "figures": [figure.dict() for figure in results["figures"]],
        "organizations": [org.dict() for org in results["organizations"]],
        "periods": [period.dict() for period in results["periods"]]
    }


@router.get("/events/{event_id}/causal-chains", response_model=List[List[str]])
async def get_causal_chains(
    event_id: str,
    max_depth: int = Query(default=5, ge=1, le=10)
):
    """Get causal chains leading to an event"""
    chains = history_engine.find_causal_chain(event_id, max_depth)
    return chains


@router.post("/temporal-network", response_model=Dict)
async def get_temporal_network(
    start_date: str,
    end_date: str
):
    """Create a temporal network for a date range"""
    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        
        network = history_engine.create_temporal_network(start, end)
        
        # Convert network to JSON-serializable format
        nodes = []
        edges = []
        
        for node_id in network.nodes():
            node_data = network.nodes[node_id]
            nodes.append({
                "id": node_id,
                "type": node_data.get("type"),
                "data": node_data.get("data", {})
            })
        
        for source, target in network.edges():
            edge_data = network[source][target]
            edges.append({
                "source": source,
                "target": target,
                "relationship": edge_data.get("relationship", "connected")
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "node_count": network.number_of_nodes(),
                "edge_count": network.number_of_edges()
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics", response_model=Dict)
async def get_history_statistics():
    """Get statistics about the historical database"""
    return history_engine.get_statistics()
