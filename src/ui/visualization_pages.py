"""
Enhanced visualization pages for Historical Intelligence Analysis System (HIAS)
Integrates Plotly, PyVis, NetworkX, and mapping capabilities
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import networkx as nx
import requests
import json
from typing import Dict, List, Any, Optional
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.visualization import visualization_engine
from src.core.graph import KnowledgeGraph
from src.core.security import security_manager

class VisualizationPages:
    """Enhanced visualization pages for Streamlit"""
    
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.kg = KnowledgeGraph()
    
    def render_advanced_graph_explorer(self):
        """Render advanced graph exploration page"""
        st.title("🌐 Advanced Graph Explorer")
        st.markdown("---")
        
        # Sidebar controls
        st.sidebar.header("Graph Controls")
        
        # Get graph data
        try:
            response = requests.get(f"{self.api_base}/api/entities")
            if response.status_code == 200:
                entities = response.json().get('entities', [])
            else:
                entities = []
        except:
            entities = []
        
        # Visualization controls
        layout = st.sidebar.selectbox(
            "Layout Algorithm",
            options=["Force Directed", "Circular", "Random", "Shell"],
            index=0
        ).lower().replace(" ", "_")
        
        node_size_metric = st.sidebar.selectbox(
            "Node Size Metric",
            options=["Degree", "Betweenness Centrality", "Fixed Size"],
            index=0
        ).lower().replace(" ", "_")
        
        # Entity type filter
        if entities:
            entity_types = list(set(entity.get('type', 'unknown') for entity in entities))
            selected_types = st.sidebar.multiselect(
                "Filter by Entity Type",
                options=entity_types,
                default=entity_types
            )
        else:
            selected_types = []
        
        # Get filtered graph data
        graph_data = self._get_filtered_graph_data(entities, selected_types)
        
        if not graph_data['nodes']:
            st.warning("No entities found. Please import some data first.")
            return
        
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["📊 Plotly Interactive", "🕸️ PyVis Network", "📈 Statistical Analysis"])
        
        with tab1:
            st.subheader("Interactive Plotly Graph")
            
            # Create interactive graph
            fig = visualization_engine.create_interactive_graph(
                graph_data, 
                layout=layout,
                node_size_metric=node_size_metric
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Graph statistics
            self._display_graph_statistics(graph_data)
        
        with tab2:
            st.subheader("PyVis Force-Directed Network")
            
            # Create PyVis graph
            html_file = visualization_engine.create_pyvis_graph(graph_data)
            
            # Display in Streamlit
            if os.path.exists(html_file):
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                st.components.v1.html(html_content, height=750)
            else:
                st.error("Failed to generate PyVis visualization")
        
        with tab3:
            st.subheader("Statistical Analysis")
            
            # Create statistical charts
            stats_data = {
                'entities': entities,
                'relationships': [],  # Would get from API
                'graph': graph_data
            }
            
            # Chart type selector
            chart_type = st.selectbox(
                "Select Analysis Type",
                options=["Entity Distribution", "Relationship Types", "Centrality Analysis"],
                index=0
            ).lower().replace(" ", "_")
            
            if chart_type == "entity_distribution":
                fig = visualization_engine.create_statistical_charts(stats_data, "entity_distribution")
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "relationship_types":
                fig = visualization_engine.create_statistical_charts(stats_data, "relationship_types")
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "centrality_analysis":
                fig = visualization_engine.create_statistical_charts(stats_data, "centrality_analysis")
                st.plotly_chart(fig, use_container_width=True)
    
    def render_geospatial_analysis(self):
        """Render geospatial analysis page"""
        st.title("🗺️ Geospatial Analysis")
        st.markdown("---")
        
        # Get location data
        try:
            response = requests.get(f"{self.api_base}/api/entities")
            if response.status_code == 200:
                entities = response.json().get('entities', [])
            else:
                entities = []
        except:
            entities = []
        
        # Filter location entities
        location_entities = [
            entity for entity in entities 
            if entity.get('type') == 'location'
        ]
        
        if not location_entities:
            st.warning("No location entities found. Please import location data first.")
            return
        
        # Create geospatial visualization
        map_data = {
            'entities': location_entities
        }
        
        fig = visualization_engine.create_geospatial_map(map_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Location details
        st.subheader("Location Details")
        
        for location in location_entities:
            with st.expander(f"📍 {location.get('name', 'Unknown Location')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Type:**", location.get('type', 'Unknown'))
                    st.write("**ID:**", location.get('id', 'Unknown'))
                    
                    # Display coordinates if available
                    attrs = location.get('attributes', {})
                    if 'latitude' in attrs and 'longitude' in attrs:
                        st.write("**Coordinates:**", f"{attrs['latitude']}, {attrs['longitude']}")
                
                with col2:
                    st.write("**Description:**", location.get('description', 'No description'))
                    
                    # Display other attributes
                    for key, value in attrs.items():
                        if key not in ['latitude', 'longitude']:
                            st.write(f"**{key.title()}:**", value)
    
    def render_temporal_analysis(self):
        """Render temporal analysis page"""
        st.title("⏰ Temporal Analysis")
        st.markdown("---")
        
        # Date range selector
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Start Date")
        
        with col2:
            end_date = st.date_input("End Date")
        
        # Analysis type selector
        analysis_type = st.selectbox(
            "Analysis Type",
            options=["Entity Creation Timeline", "Relationship Formation", "Activity Heatmap"],
            index=0
        )
        
        # Get temporal data
        try:
            response = requests.get(f"{self.api_base}/api/entities")
            if response.status_code == 200:
                entities = response.json().get('entities', [])
            else:
                entities = []
        except:
            entities = []
        
        # Filter by date range
        filtered_entities = []
        for entity in entities:
            created_at = entity.get('created_at')
            if created_at:
                # Parse date (simplified)
                entity_date = pd.to_datetime(created_at).date()
                if start_date <= entity_date <= end_date:
                    filtered_entities.append(entity)
        
        if not filtered_entities:
            st.warning("No entities found in selected date range.")
            return
        
        # Create temporal visualization
        temporal_data = {
            'entities': filtered_entities,
            'events': []  # Would get from API
        }
        
        fig = visualization_engine.create_statistical_charts(temporal_data, "temporal_analysis")
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        st.subheader("Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Entities", len(filtered_entities))
        
        with col2:
            # Calculate entities per day
            if filtered_entities:
                date_range = (end_date - start_date).days + 1
                entities_per_day = len(filtered_entities) / date_range
                st.metric("Entities Per Day", f"{entities_per_day:.1f}")
            else:
                st.metric("Entities Per Day", "0")
        
        with col3:
            # Most active day (placeholder)
            st.metric("Most Active Day", "TBD")
    
    def render_network_metrics(self):
        """Render network metrics dashboard"""
        st.title("📊 Network Metrics Dashboard")
        st.markdown("---")
        
        # Get graph statistics
        try:
            response = requests.get(f"{self.api_base}/api/stats")
            if response.status_code == 200:
                stats = response.json()
            else:
                stats = {}
        except:
            stats = {}
        
        if not stats:
            st.warning("No statistics available. Please add some data first.")
            return
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Nodes", stats.get('nodes', 0))
        
        with col2:
            st.metric("Total Edges", stats.get('edges', 0))
        
        with col3:
            st.metric("Density", f"{stats.get('density', 0):.3f}")
        
        with col4:
            st.metric("Components", stats.get('connected_components', 0))
        
        # Advanced metrics
        st.subheader("Advanced Network Metrics")
        
        metric_tabs = st.tabs(["📈 Centrality", "🔗 Connectivity", "📐 Structure"])
        
        with metric_tabs[0]:
            st.write("**Centrality Analysis**")
            st.info("Centrality metrics help identify the most important nodes in the network.")
            
            # Placeholder for centrality analysis
            centrality_data = {
                'graph': self._get_graph_data()
            }
            
            if centrality_data['graph']['nodes']:
                fig = visualization_engine.create_statistical_charts(centrality_data, "centrality_analysis")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available for centrality analysis.")
        
        with metric_tabs[1]:
            st.write("**Connectivity Analysis**")
            st.info("Connectivity metrics show how well-connected the network is.")
            
            # Connectivity metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Average Clustering", f"{stats.get('avg_clustering', 0):.3f}")
                st.metric("Network Diameter", "TBD")  # Would calculate from graph
            
            with col2:
                st.metric("Average Path Length", "TBD")  # Would calculate from graph
                st.metric("Graph Radius", "TBD")  # Would calculate from graph
        
        with metric_tabs[2]:
            st.write("**Structural Analysis**")
            st.info("Structural metrics reveal the overall shape and properties of the network.")
            
            # Entity type distribution
            try:
                response = requests.get(f"{self.api_base}/api/entities")
                if response.status_code == 200:
                    entities = response.json().get('entities', [])
                    
                    distribution_data = {'entities': entities}
                    fig = visualization_engine.create_statistical_charts(distribution_data, "entity_distribution")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Failed to fetch entity data")
            except:
                st.error("Error connecting to API")
    
    def _get_filtered_graph_data(self, entities: List[Dict], selected_types: List[str]) -> Dict[str, Any]:
        """Get filtered graph data based on selected entity types"""
        
        # Filter entities
        filtered_entities = [
            entity for entity in entities 
            if entity.get('type') in selected_types
        ]
        
        # Get relationships (placeholder - would get from API)
        filtered_relationships = []
        
        return {
            'nodes': filtered_entities,
            'edges': filtered_relationships
        }
    
    def _get_graph_data(self) -> Dict[str, Any]:
        """Get complete graph data"""
        try:
            response = requests.get(f"{self.api_base}/api/entities")
            if response.status_code == 200:
                entities = response.json().get('entities', [])
            else:
                entities = []
        except:
            entities = []
        
        return {
            'nodes': entities,
            'edges': []  # Would get from API
        }
    
    def _display_graph_statistics(self, graph_data: Dict[str, Any]):
        """Display graph statistics"""
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        st.subheader("Graph Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nodes", len(nodes))
        
        with col2:
            st.metric("Edges", len(edges))
        
        with col3:
            if nodes:
                density = (2 * len(edges)) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0
                st.metric("Density", f"{density:.3f}")
            else:
                st.metric("Density", "0.000")
        
        # Entity type breakdown
        if nodes:
            entity_types = {}
            for node in nodes:
                entity_type = node.get('type', 'unknown')
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
            
            st.write("**Entity Types:**")
            for entity_type, count in entity_types.items():
                st.write(f"- {entity_type}: {count}")

# Create visualization pages instance
viz_pages = VisualizationPages()
