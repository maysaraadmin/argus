"""
Intelligence analysis UI pages for historical research.
Provides intelligence community tools adapted for historical study.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime
from typing import List, Dict
import networkx as nx

from src.core.intelligence_analysis import IntelligenceAnalyzer
from src.core.history_engine import HistoryEngine
from src.data.history_models import EventType


class IntelligencePages:
    """Intelligence analysis pages for historical research"""
    
    def __init__(self):
        self.history_engine = HistoryEngine()
        self.analyzer = IntelligenceAnalyzer(self.history_engine)
        self._load_sample_data()
    
    def render_intelligence_dashboard(self):
        """Main intelligence analysis dashboard"""
        st.header("🕵️ Intelligence Analysis Dashboard")
        
        # Overview metrics
        st.subheader("Intelligence Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Entities", self.analyzer.network.number_of_nodes())
        with col2:
            st.metric("Connections", self.analyzer.network.number_of_edges())
        with col3:
            st.metric("Network Density", f"{nx.density(self.analyzer.network):.3f}")
        with col4:
            st.metric("Connected Components", nx.number_connected_components(self.analyzer.network.to_undirected()))
        
        # Key Players Analysis
        st.subheader("🎯 Key Player Analysis")
        key_players = self.analyzer.find_key_players()
        
        if key_players:
            top_players = list(key_players.items())[:10]
            player_data = []
            for player_id, score in top_players:
                if player_id in self.history_engine.figures:
                    figure = self.history_engine.figures[player_id]
                    player_data.append({
                        "Name": figure.name,
                        "Era": figure.era,
                        "Influence Score": f"{score:.3f}",
                        "Occupations": ", ".join(figure.occupation[:2])
                    })
            
            df_players = pd.DataFrame(player_data)
            st.dataframe(df_players, use_container_width=True)
            
            # Visualize key players network
            self._render_key_players_network(top_players[:5])
        
        # Recent Intelligence Alerts
        st.subheader("🚨 Intelligence Alerts")
        self._render_intelligence_alerts()
    
    def render_network_analysis(self):
        """Advanced network analysis tools"""
        st.header("🌐 Network Analysis")
        
        analysis_type = st.selectbox("Analysis Type", [
            "Influence Networks",
            "Causal Chains", 
            "Connection Patterns",
            "Network Metrics"
        ])
        
        if analysis_type == "Influence Networks":
            self._render_influence_networks()
        elif analysis_type == "Causal Chains":
            self._render_causal_chains()
        elif analysis_type == "Connection Patterns":
            self._render_connection_patterns()
        elif analysis_type == "Network Metrics":
            self._render_network_metrics()
    
    def render_pattern_analysis(self):
        """Pattern recognition and analysis"""
        st.header("🔍 Pattern Analysis")
        
        # Select period for analysis
        periods = list(self.history_engine.periods.values())
        if periods:
            period_options = {period.name: period.id for period in periods}
            selected_period_name = st.selectbox("Select Period", list(period_options.keys()))
            selected_period = self.history_engine.periods[period_options[selected_period_name]]
            
            patterns = self.analyzer.detect_historical_patterns(selected_period)
            
            # Event type patterns
            st.subheader("Event Type Distribution")
            if patterns["event_patterns"]:
                fig = px.pie(
                    values=list(patterns["event_patterns"].values()),
                    names=list(patterns["event_patterns"].keys()),
                    title=f"Event Types in {selected_period.name}"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Temporal patterns
            st.subheader("Temporal Patterns")
            if patterns["temporal_patterns"]:
                years = list(patterns["temporal_patterns"].keys())
                frequencies = list(patterns["temporal_patterns"].values())
                
                fig = go.Figure(data=go.Scatter(
                    x=years, y=frequencies,
                    mode='lines+markers',
                    name='Event Frequency'
                ))
                fig.update_layout(
                    title=f"Event Frequency Over Time - {selected_period.name}",
                    xaxis_title="Year",
                    yaxis_title="Number of Events"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Anomalous years
            if patterns["anomalous_years"]:
                st.subheader("🚨 Anomalous Years Detected")
                for year, count in patterns["anomalous_years"].items():
                    st.warning(f"Year {year}: {count} events (unusual spike)")
            
            # Key participants
            st.subheader("Most Active Participants")
            if patterns["key_participants"]:
                participant_data = []
                for participant_id, count in list(patterns["key_participants"].items())[:10]:
                    if participant_id in self.history_engine.figures:
                        figure = self.history_engine.figures[participant_id]
                        participant_data.append({
                            "Name": figure.name,
                            "Event Participation": count,
                            "Era": figure.era
                        })
                
                df_participants = pd.DataFrame(participant_data)
                st.dataframe(df_participants, use_container_width=True)
    
    def render_geospatial_intelligence(self):
        """Geospatial intelligence analysis"""
        st.header("🗺️ Geospatial Intelligence")
        
        # Region filter
        regions = list(set(event.location for event in self.history_engine.events.values()))
        selected_region = st.selectbox("Filter by Region", ["All"] + regions)
        
        # Time period filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        
        if st.button("Analyze Geospatial Patterns"):
            time_period = (start_date, end_date) if start_date and end_date else None
            region = selected_region if selected_region != "All" else None
            
            geo_analysis = self.analyzer.analyze_geospatial_intelligence(region, time_period)
            
            # Strategic locations
            st.subheader("🎯 Strategic Locations")
            if geo_analysis["strategic_locations"]:
                strategic_data = []
                for location, score in geo_analysis["strategic_locations"].items():
                    strategic_data.append({
                        "Location": location,
                        "Strategic Score": f"{score:.2f}",
                        "Event Count": geo_analysis["location_frequency"].get(location, 0)
                    })
                
                df_strategic = pd.DataFrame(strategic_data)
                st.dataframe(df_strategic, use_container_width=True)
            
            # Location frequency
            st.subheader("📍 Event Frequency by Location")
            if geo_analysis["location_frequency"]:
                locations = list(geo_analysis["location_frequency"].keys())[:20]
                frequencies = list(geo_analysis["location_frequency"].values())[:20]
                
                fig = go.Figure(data=go.Bar(
                    x=locations,
                    y=frequencies,
                    orientation='v'
                ))
                fig.update_layout(
                    title="Events by Location",
                    xaxis_title="Location",
                    yaxis_title="Number of Events"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Movement patterns
            st.subheader("🔄 Movement Patterns")
            if geo_analysis["movement_patterns"]["location_sequence"]:
                st.write("**Historical Movement Sequence:**")
                for i, location in enumerate(geo_analysis["movement_patterns"]["location_sequence"][:10]):
                    st.write(f"{i+1}. {location}")
    
    def render_threat_assessment(self):
        """Threat assessment for historical conflicts"""
        st.header("⚠️ Threat Assessment")
        
        # Select period
        periods = list(self.history_engine.periods.values())
        if periods:
            period_options = {period.name: period.id for period in periods}
            selected_period_name = st.selectbox("Select Period for Threat Analysis", list(period_options.keys()))
            selected_period = self.history_engine.periods[period_options[selected_period_name]]
            
            threat_analysis = self.analyzer.threat_assessment_analysis(selected_period)
            
            # Threat overview
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Threats", threat_analysis["total_threats"])
            with col2:
                st.metric("Threat Clusters", len(threat_analysis["threat_clusters"]))
            with col3:
                high_risk = len(threat_analysis["high_risk_events"])
                st.metric("High Risk Events", high_risk)
            
            # High risk events
            if threat_analysis["high_risk_events"]:
                st.subheader("🚨 High Risk Events")
                for event in threat_analysis["high_risk_events"]:
                    with st.expander(f"{event['title']} ({event['date']})"):
                        st.write(f"**Type:** {event['event_type']}")
                        st.write(f"**Location:** {event['location']}")
                        st.write(f"**Significance:** {event['significance']}")
            
            # Threat clusters
            if threat_analysis["threat_clusters"]:
                st.subheader("🔗 Threat Clusters")
                for i, cluster in enumerate(threat_analysis["threat_clusters"][:5]):
                    st.write(f"**Cluster {i+1}:** {len(cluster)} related threats")
                    event_names = []
                    for event_id in cluster:
                        if event_id in self.history_engine.events:
                            event_names.append(self.history_engine.events[event_id].title)
                    st.write(", ".join(event_names))
            
            # Warning indicators
            if threat_analysis["warning_indicators"]:
                st.subheader("📡 Early Warning Indicators")
                for indicator in threat_analysis["warning_indicators"][:10]:
                    warning_event = indicator["warning_event"]
                    threatened_event = indicator["threatened_event"]
                    st.write(f"**{warning_event['title']}** → **{threatened_event['title']}** ({indicator['warning_period']} days)")
    
    def _render_key_players_network(self, top_players):
        """Render network visualization of key players"""
        fig = go.Figure()
        
        # Create a subgraph of top players
        player_ids = [player_id for player_id, _ in top_players]
        subgraph = self.analyzer.network.subgraph(player_ids)
        
        # Calculate positions
        pos = nx.spring_layout(subgraph, seed=42)
        
        # Add edges
        edge_x, edge_y = [], []
        for edge in subgraph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'
        ))
        
        # Add nodes
        node_x, node_y, node_text = [], [], []
        for node in subgraph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            if node in self.history_engine.figures:
                figure = self.history_engine.figures[node]
                node_text.append(figure.name)
            else:
                node_text.append(node)
        
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            marker=dict(
                size=20,
                color='lightblue',
                line_width=2
            )
        ))
        
        fig.update_layout(
            title="Key Players Network",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_intelligence_alerts(self):
        """Render intelligence alerts and warnings"""
        alerts = []
        
        # Check for anomalous patterns
        for period_id, period in self.history_engine.periods.items():
            patterns = self.analyzer.detect_historical_patterns(period)
            if patterns["anomalous_years"]:
                alerts.append({
                    "type": "anomaly",
                    "message": f"Unusual activity detected in {period.name}",
                    "severity": "medium"
                })
        
        # Check for high-risk events
        for period_id, period in self.history_engine.periods.items():
            threat_analysis = self.analyzer.threat_assessment_analysis(period)
            if threat_analysis["high_risk_events"]:
                alerts.append({
                    "type": "threat",
                    "message": f"High-risk events identified in {period.name}",
                    "severity": "high"
                })
        
        if alerts:
            for alert in alerts:
                if alert["severity"] == "high":
                    st.error(f"🚨 {alert['message']}")
                else:
                    st.warning(f"⚠️ {alert['message']}")
        else:
            st.info("✅ No immediate intelligence alerts")
    
    def _render_influence_networks(self):
        """Render influence network analysis"""
        st.subheader("Figure Influence Analysis")
        
        # Select figure
        figures = list(self.history_engine.figures.values())
        if figures:
            selected_figure_name = st.selectbox("Select Figure", [fig.name for fig in figures])
            selected_figure = next(fig for fig in figures if fig.name == selected_figure_name)
            
            influence = self.analyzer.analyze_influence_networks(selected_figure.id)
            
            if influence:
                # Network metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Direct Connections", influence["network_metrics"]["direct_connections"])
                with col2:
                    st.metric("Extended Reach", influence["network_metrics"]["extended_reach"])
                with col3:
                    st.metric("Betweenness", f"{influence['network_metrics']['betweenness_centrality']:.3f}")
                with col4:
                    st.metric("Eigenvector", f"{influence['network_metrics']['eigenvector_centrality']:.3f}")
                
                # Causal influence
                st.subheader("Causal Influence")
                if influence["causal_influence"]["top_influences"]:
                    for influence_data in influence["causal_influence"]["top_influences"][:5]:
                        event = influence_data["event"]
                        st.write(f"**{event['title']}** - Impact Score: {influence_data['impact_score']:.2f}")
    
    def _render_causal_chains(self):
        """Render causal chain analysis"""
        st.subheader("Causal Chain Analysis")
        
        # Select event
        events = list(self.history_engine.events.values())
        if events:
            selected_event_name = st.selectbox("Select Event", [event.title for event in events])
            selected_event = next(event for event in events if event.title == selected_event_name)
            
            chains = self.analyzer.trace_causal_chains(selected_event.id)
            
            if chains:
                st.write(f"Found {len(chains)} causal chains:")
                for i, chain in enumerate(chains[:5]):
                    st.write(f"**Chain {i+1}** (Strength: {chain['strength']:.2f}):")
                    event_names = []
                    for event_id in chain["chain"]:
                        if event_id in self.history_engine.events:
                            event_names.append(self.history_engine.events[event_id].title)
                    st.write(" → ".join(reversed(event_names)))
            else:
                st.info("No causal chains found for this event.")
    
    def _render_connection_patterns(self):
        """Render connection pattern analysis"""
        st.subheader("Connection Patterns")
        
        # Network density analysis
        density = nx.density(self.analyzer.network)
        st.write(f"**Network Density:** {density:.3f}")
        
        # Connected components
        components = list(nx.connected_components(self.analyzer.network.to_undirected()))
        st.write(f"**Connected Components:** {len(components)}")
        
        # Largest component
        if components:
            largest = max(components, key=len)
            st.write(f"**Largest Component Size:** {len(largest)} nodes")
        
        # Degree distribution
        degrees = dict(self.analyzer.network.degree())
        if degrees:
            avg_degree = sum(degrees.values()) / len(degrees)
            st.write(f"**Average Degree:** {avg_degree:.2f}")
    
    def _render_network_metrics(self):
        """Render detailed network metrics"""
        st.subheader("Detailed Network Metrics")
        
        # Centrality measures
        try:
            betweenness = nx.betweenness_centrality(self.analyzer.network)
            eigenvector = nx.eigenvector_centrality(self.analyzer.network, max_iter=1000)
            degree = nx.degree_centrality(self.analyzer.network)
        except nx.NetworkXError:
            # Handle network analysis errors
            betweenness = {}
            eigenvector = {node: 0.0 for node in self.analyzer.network.nodes()}
            degree = nx.degree_centrality(self.analyzer.network)
        
        # Create metrics table
        metrics_data = []
        for node in self.analyzer.network.nodes():
            if self.analyzer.network.nodes[node].get('type') == 'figure':
                figure = self.history_engine.figures.get(node)
                if figure:
                    metrics_data.append({
                        "Name": figure.name,
                        "Betweenness": f"{betweenness.get(node, 0):.3f}",
                        "Eigenvector": f"{eigenvector.get(node, 0):.3f}",
                        "Degree": f"{degree.get(node, 0):.3f}"
                    })
        
        if metrics_data:
            df_metrics = pd.DataFrame(metrics_data)
            st.dataframe(df_metrics, use_container_width=True)
    
    def _load_sample_data(self):
        """Load sample historical data for demonstration"""
        # Import sample data from history_pages
        from src.ui.history_pages import HistoryPages
        history_pages = HistoryPages()
        # Sample data is already loaded in HistoryPages constructor
