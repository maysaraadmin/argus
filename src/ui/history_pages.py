"""
History study UI pages for Argus.
Provides specialized interfaces for historical research and analysis.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime
from typing import List, Dict
import json

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.history_engine import HistoryEngine
from data.history_models import (
    HistoricalEvent, HistoricalFigure, HistoricalOrganization,
    HistoricalPeriod, Timeline, EventType, PeriodType
)


class HistoryPages:
    """History study UI pages"""
    
    def __init__(self):
        self.engine = HistoryEngine()
        self._load_sample_data()
    
    def render_history_dashboard(self):
        """Main history study dashboard"""
        st.header("📚 History Study Dashboard")
        
        # Statistics
        stats = self.engine.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Events", stats['total_events'])
        with col2:
            st.metric("Figures", stats['total_figures'])
        with col3:
            st.metric("Organizations", stats['total_organizations'])
        with col4:
            st.metric("Periods", stats['total_periods'])
        
        # Quick actions
        st.subheader("Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📅 Create Timeline", use_container_width=True):
                st.session_state.show_timeline_creator = True
        
        with col2:
            if st.button("👤 Add Historical Figure", use_container_width=True):
                st.session_state.show_figure_creator = True
        
        with col3:
            if st.button("⚔️ Add Historical Event", use_container_width=True):
                st.session_state.show_event_creator = True
        
        # Event type distribution
        if stats['event_types']:
            st.subheader("Event Distribution")
            fig = px.pie(values=list(stats['event_types'].values()), 
                        names=list(stats['event_types'].keys()),
                        title="Events by Type")
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent events
        st.subheader("Recent Historical Events")
        recent_events = list(self.engine.events.values())[-5:]
        if recent_events:
            events_data = []
            for event in recent_events:
                events_data.append({
                    "Date": event.date,
                    "Title": event.title,
                    "Type": event.event_type.value,
                    "Location": event.location
                })
            st.dataframe(pd.DataFrame(events_data), use_container_width=True)
    
    def render_timeline_viewer(self):
        """Interactive timeline viewer"""
        st.header("📅 Historical Timeline Viewer")
        
        # Timeline selection
        timeline_options = {f"{timeline.name} ({timeline.start_date} - {timeline.end_date})": timeline_id 
                          for timeline_id, timeline in self.engine.timelines.items()}
        
        if timeline_options:
            selected_timeline_name = st.selectbox("Select Timeline", list(timeline_options.keys()))
            selected_timeline_id = timeline_options[selected_timeline_name]
            
            timeline = self.engine.timelines[selected_timeline_id]
            
            # Timeline info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Period:** {timeline.start_date} to {timeline.end_date}")
            with col2:
                st.write(f"**Events:** {len(timeline.events)}")
            with col3:
                st.write(f"**Focus:** {timeline.focus}")
            
            # Get timeline events
            events = self.engine.get_timeline_events(selected_timeline_id)
            
            if events:
                # Create timeline visualization
                fig = self._create_timeline_visualization(events)
                st.plotly_chart(fig, use_container_width=True)
                
                # Event details
                st.subheader("Event Details")
                selected_event = st.selectbox("Select Event for Details", 
                                            [event.title for event in events])
                
                if selected_event:
                    event = next(e for e in events if e.title == selected_event)
                    self._display_event_details(event)
            else:
                st.info("No events found in this timeline.")
        else:
            st.info("No timelines available. Create one to get started.")
    
    def render_figure_explorer(self):
        """Historical figures explorer"""
        st.header("👤 Historical Figures Explorer")
        
        # Search and filter
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_term = st.text_input("Search figures...")
        
        with col2:
            era_filter = st.selectbox("Filter by Era", ["All"] + list(set(fig.era for fig in self.engine.figures.values())))
        
        # Filter figures
        figures = list(self.engine.figures.values())
        
        if search_term:
            figures = [fig for fig in figures if search_term.lower() in fig.name.lower()]
        
        if era_filter != "All":
            figures = [fig for fig in figures if fig.era == era_filter]
        
        if figures:
            # Figure selection
            selected_figure = st.selectbox("Select Figure", [fig.name for fig in figures])
            
            if selected_figure:
                figure = next(fig for fig in figures if fig.name == selected_figure)
                
                # Display figure details
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.subheader("Basic Information")
                    st.write(f"**Name:** {figure.name}")
                    st.write(f"**Era:** {figure.era}")
                    if figure.birth_date:
                        st.write(f"**Born:** {figure.birth_date}")
                    if figure.death_date:
                        st.write(f"**Died:** {figure.death_date}")
                    if figure.birth_place:
                        st.write(f"**Birth Place:** {figure.birth_place}")
                    
                    st.write("**Occupations:**")
                    for occ in figure.occupation:
                        st.write(f"- {occ}")
                
                with col2:
                    st.subheader("Biography")
                    st.write(figure.biography)
                    
                    if figure.achievements:
                        st.write("**Achievements:**")
                        for achievement in figure.achievements:
                            st.write(f"• {achievement}")
                
                # Find contemporaries
                st.subheader("Contemporaries")
                contemporaries = self.engine.find_contemporaries(figure.id)
                if contemporaries:
                    cont_data = []
                    for cont in contemporaries[:10]:  # Limit to 10
                        cont_data.append({
                            "Name": cont.name,
                            "Era": cont.era,
                            "Occupation": ", ".join(cont.occupation[:2])
                        })
                    st.dataframe(pd.DataFrame(cont_data), use_container_width=True)
                else:
                    st.info("No contemporaries found.")
                
                # Influence analysis
                st.subheader("Influence Analysis")
                influence = self.engine.analyze_influence_network(figure.id)
                if influence:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Events Participated", len(influence.get('participated_events', [])))
                    with col2:
                        st.metric("Organizations", len(influence.get('affiliated_organizations', [])))
                    with col3:
                        st.metric("Influence Score", f"{influence.get('influence_score', 0):.1f}")
        else:
            st.info("No figures found matching your criteria.")
    
    def render_event_analyzer(self):
        """Historical events analyzer"""
        st.header("⚔️ Historical Events Analyzer")
        
        # Event type filter
        event_type = st.selectbox("Filter by Event Type", ["All"] + [et.value for et in EventType])
        
        # Get events
        if event_type == "All":
            events = list(self.engine.events.values())
        else:
            events = self.engine.find_events_by_type(EventType(event_type))
        
        if events:
            # Sort by date
            events.sort(key=lambda e: e.date)
            
            # Event selection
            event_options = {f"{event.date} - {event.title}": event.id for event in events}
            selected_event_id = st.selectbox("Select Event", list(event_options.keys()))
            selected_event = self.engine.events[event_options[selected_event_id]]
            
            # Display event details
            self._display_event_details(selected_event)
            
            # Causal analysis
            st.subheader("Causal Analysis")
            causal_chains = self.engine.find_causal_chain(selected_event.id)
            
            if causal_chains:
                st.write("**Causal Chains:**")
                for i, chain in enumerate(causal_chains[:3]):  # Show first 3 chains
                    chain_events = [self.engine.events[eid].title for eid in chain if eid in self.engine.events]
                    st.write(f"{i+1}. {' → '.join(reversed(chain_events))}")
            else:
                st.info("No causal chains found for this event.")
            
            # Related events
            st.subheader("Related Events")
            related_events = []
            
            # Find events with same participants
            for participant in selected_event.participants:
                for event in self.engine.events.values():
                    if event.id != selected_event.id and participant in event.participants:
                        related_events.append(event)
            
            # Find events in same location
            for event in self.engine.events.values():
                if (event.id != selected_event.id and 
                    event.location.lower() == selected_event.location.lower()):
                    related_events.append(event)
            
            if related_events:
                # Remove duplicates and sort
                related_events = list(set(related_events))
                related_events.sort(key=lambda e: e.date)
                
                related_data = []
                for event in related_events[:10]:  # Limit to 10
                    related_data.append({
                        "Date": event.date,
                        "Title": event.title,
                        "Type": event.event_type.value,
                        "Location": event.location
                    })
                st.dataframe(pd.DataFrame(related_data), use_container_width=True)
            else:
                st.info("No related events found.")
        else:
            st.info("No events found for this type.")
    
    def render_period_browser(self):
        """Historical periods browser"""
        st.header("🏛️ Historical Periods Browser")
        
        # Period selection
        periods = list(self.engine.periods.values())
        if periods:
            period_options = {period.name: period.id for period in periods}
            selected_period_name = st.selectbox("Select Period", list(period_options.keys()))
            selected_period = self.engine.periods[period_options[selected_period_name]]
            
            # Period details
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Period Information")
                st.write(f"**Name:** {selected_period.name}")
                st.write(f"**Type:** {selected_period.period_type.value}")
                st.write(f"**Duration:** {selected_period.start_date} to {selected_period.end_date or 'Present'}")
                st.write(f"**Region:** {selected_period.region}")
                
                if selected_period.key_characteristics:
                    st.write("**Key Characteristics:**")
                    for char in selected_period.key_characteristics:
                        st.write(f"• {char}")
            
            with col2:
                st.write("**Description:**")
                st.write(selected_period.description)
            
            # Events in this period
            st.subheader("Events in This Period")
            period_events = self.engine.find_events_by_period(selected_period.id)
            
            if period_events:
                events_data = []
                for event in period_events:
                    events_data.append({
                        "Date": event.date,
                        "Title": event.title,
                        "Type": event.event_type.value,
                        "Location": event.location
                    })
                st.dataframe(pd.DataFrame(events_data), use_container_width=True)
            else:
                st.info("No events found in this period.")
        else:
            st.info("No historical periods available.")
    
    def render_research_tools(self):
        """Historical research tools"""
        st.header("🔍 Historical Research Tools")
        
        tool = st.selectbox("Select Tool", [
            "Keyword Search",
            "Temporal Network Analysis",
            "Comparative Analysis",
            "Source Management"
        ])
        
        if tool == "Keyword Search":
            self._render_keyword_search()
        elif tool == "Temporal Network Analysis":
            self._render_temporal_network()
        elif tool == "Comparative Analysis":
            self._render_comparative_analysis()
        elif tool == "Source Management":
            self._render_source_management()
    
    def _create_timeline_visualization(self, events: List[HistoricalEvent]) -> go.Figure:
        """Create an interactive timeline visualization"""
        # Prepare data
        event_data = []
        for event in events:
            event_data.append({
                'title': event.title,
                'date': event.date,
                'type': event.event_type.value,
                'location': event.location,
                'description': event.description[:100] + "..." if len(event.description) > 100 else event.description
            })
        
        df = pd.DataFrame(event_data)
        
        # Create timeline
        fig = px.scatter(
            df, 
            x='date', 
            y='type',
            hover_data=['title', 'location', 'description'],
            color='type',
            title="Historical Timeline",
            labels={'date': 'Date', 'type': 'Event Type'}
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Event Type",
            height=500
        )
        
        return fig
    
    def _display_event_details(self, event: HistoricalEvent):
        """Display detailed information about a historical event"""
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write(f"**Date:** {event.date}")
            if event.end_date:
                st.write(f"**End Date:** {event.end_date}")
            st.write(f"**Type:** {event.event_type.value}")
            st.write(f"**Location:** {event.location}")
            if event.coordinates:
                st.write(f"**Coordinates:** {event.coordinates}")
            
            if event.participants:
                st.write("**Participants:**")
                for participant_id in event.participants:
                    if participant_id in self.engine.figures:
                        participant = self.engine.figures[participant_id]
                        st.write(f"• {participant.name}")
        
        with col2:
            st.write("**Description:**")
            st.write(event.description)
            
            if event.significance:
                st.write("**Historical Significance:**")
                st.write(event.significance)
            
            if event.tags:
                st.write("**Tags:**")
                tags_str = ", ".join(event.tags)
                st.write(tags_str)
    
    def _render_keyword_search(self):
        """Render keyword search tool"""
        st.subheader("Keyword Search")
        
        keyword = st.text_input("Enter keyword to search:")
        
        if keyword:
            results = self.engine.search_by_keyword(keyword)
            
            # Display results
            if any(results.values()):
                if results['events']:
                    st.write("**Events:**")
                    for event in results['events'][:5]:
                        st.write(f"• {event.title} ({event.date})")
                
                if results['figures']:
                    st.write("**Figures:**")
                    for figure in results['figures'][:5]:
                        st.write(f"• {figure.name} ({figure.era})")
                
                if results['organizations']:
                    st.write("**Organizations:**")
                    for org in results['organizations'][:5]:
                        st.write(f"• {org.name}")
                
                if results['periods']:
                    st.write("**Periods:**")
                    for period in results['periods'][:5]:
                        st.write(f"• {period.name}")
            else:
                st.info("No results found.")
    
    def _render_temporal_network(self):
        """Render temporal network analysis tool"""
        st.subheader("Temporal Network Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        
        if start_date and end_date and st.button("Analyze Network"):
            network = self.engine.create_temporal_network(start_date, end_date)
            
            st.write(f"**Network Statistics:**")
            st.write(f"• Nodes: {network.number_of_nodes()}")
            st.write(f"• Edges: {network.number_of_edges()}")
            
            if network.number_of_nodes() > 0:
                st.write("**Network Components:**")
                components = list(nx.connected_components(network))
                st.write(f"• Connected Components: {len(components)}")
                
                # Largest component
                if components:
                    largest = max(components, key=len)
                    st.write(f"• Largest Component Size: {len(largest)}")
    
    def _render_comparative_analysis(self):
        """Render comparative analysis tool"""
        st.subheader("Comparative Analysis")
        
        st.write("Compare historical figures, events, or periods")
        
        comparison_type = st.selectbox("Compare", ["Figures", "Events", "Periods"])
        
        if comparison_type == "Figures":
            figures = list(self.engine.figures.values())
            if len(figures) >= 2:
                selected_figures = st.multiselect("Select figures to compare", 
                                                 [fig.name for fig in figures])
                
                if len(selected_figures) >= 2:
                    self._compare_figures(selected_figures)
        
        elif comparison_type == "Events":
            events = list(self.engine.events.values())
            if len(events) >= 2:
                selected_events = st.multiselect("Select events to compare", 
                                                [event.title for event in events])
                
                if len(selected_events) >= 2:
                    self._compare_events(selected_events)
    
    def _render_source_management(self):
        """Render source management tool"""
        st.subheader("Source Management")
        
        st.write("Manage historical sources and references")
        
        # Add new source
        with st.expander("Add New Source"):
            title = st.text_input("Source Title")
            author = st.text_input("Author")
            source_type = st.selectbox("Source Type", ["primary", "secondary", "tertiary"])
            medium = st.selectbox("Medium", ["text", "artifact", "oral", "digital"])
            language = st.text_input("Language")
            
            if st.button("Add Source"):
                st.success("Source added successfully!")
    
    def _compare_figures(self, figure_names: List[str]):
        """Compare historical figures"""
        figures_data = []
        
        for name in figure_names:
            figure = next(fig for fig in self.engine.figures.values() if fig.name == name)
            figures_data.append({
                "Name": figure.name,
                "Era": figure.era,
                "Birth": figure.birth_date,
                "Death": figure.death_date,
                "Occupations": ", ".join(figure.occupation),
                "Achievements": len(figure.achievements)
            })
        
        st.dataframe(pd.DataFrame(figures_data), use_container_width=True)
    
    def _compare_events(self, event_titles: List[str]):
        """Compare historical events"""
        events_data = []
        
        for title in event_titles:
            event = next(event for event in self.engine.events.values() if event.title == title)
            events_data.append({
                "Title": event.title,
                "Date": event.date,
                "Type": event.event_type.value,
                "Location": event.location,
                "Participants": len(event.participants)
            })
        
        st.dataframe(pd.DataFrame(events_data), use_container_width=True)
    
    def _load_sample_data(self):
        """Load sample historical data for demonstration"""
        # Sample periods
        roman_period = HistoricalPeriod(
            name="Roman Empire",
            description="The period of Roman domination in the Mediterranean world",
            start_date=date(27, 1, 1),
            end_date=date(476, 9, 4),
            period_type=PeriodType.CLASSICAL,
            region="Europe, North Africa, Middle East",
            key_characteristics=["Centralized government", "Military conquest", "Engineering achievements"]
        )
        
        renaissance_period = HistoricalPeriod(
            name="Renaissance",
            description="Period of cultural rebirth and intellectual revival",
            start_date=date(1350, 1, 1),
            end_date=date(1600, 12, 31),
            period_type=PeriodType.RENAISSANCE,
            region="Europe",
            key_characteristics=["Humanism", "Artistic innovation", "Scientific revolution"]
        )
        
        self.engine.add_period(roman_period)
        self.engine.add_period(renaissance_period)
        
        # Sample figures
        julius_caesar = HistoricalFigure(
            name="Julius Caesar",
            birth_date=date(100, 7, 12),  # 100 BCE
            death_date=date(44, 3, 15),    # 44 BCE
            birth_place="Rome",
            death_place="Rome",
            occupation=["Military General", "Politician", "Author"],
            achievements=["Conquest of Gaul", "Civil War victory", "Calendar reform"],
            era="Roman Republic",
            biography="Roman general and statesman who played a critical role in the events that led to the demise of the Roman Republic and the rise of the Roman Empire."
        )
        
        leonardo_da_vinci = HistoricalFigure(
            name="Leonardo da Vinci",
            birth_date=date(1452, 4, 15),
            death_date=date(1519, 5, 2),
            birth_place="Vinci, Italy",
            death_place="Amboise, France",
            occupation=["Artist", "Scientist", "Inventor", "Architect"],
            achievements=["Mona Lisa", "The Last Supper", "Flying machines", "Anatomical studies"],
            era="Renaissance",
            biography="Italian polymath of the High Renaissance who was active as a painter, draughtsman, engineer, scientist, theorist, sculptor and architect."
        )
        
        self.engine.add_figure(julius_caesar)
        self.engine.add_figure(leonardo_da_vinci)
        
        # Sample events
        caesar_crossing = HistoricalEvent(
            title="Crossing of the Rubicon",
            description="Julius Caesar led his army across the Rubicon river, defying the Roman Senate",
            event_type=EventType.POLITICAL,
            date=date(49, 1, 10),  # 49 BCE
            location="Rubicon River, Italy",
            participants=[julius_caesar.id],
            significance="Marked the point of no return in Caesar's conflict with the Senate",
            tags=["civil war", "rome", "caesar"]
        )
        
        self.engine.add_event(caesar_crossing)
        
        # Sample timeline
        roman_timeline = Timeline(
            name="Roman History Timeline",
            description="Key events in Roman history",
            start_date=date(753, 1, 1),  # 753 BCE
            end_date=date(476, 9, 4),
            events=[caesar_crossing.id],
            periods=[roman_period.id],
            focus="Political and military history",
            created_by="system"
        )
        
        self.engine.create_timeline(roman_timeline)
