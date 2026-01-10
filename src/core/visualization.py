"""
Advanced visualization system for Argus MVP
Implements Plotly, PyVis, NetworkX, and mapping capabilities
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import pyvis.network as net
from pyvis.network import Network
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VisualizationEngine:
    """Advanced visualization engine for graphs and data"""
    
    def __init__(self):
        self.color_schemes = {
            'entity_types': {
                'person': '#3498db',
                'organization': '#e74c3c',
                'location': '#2ecc71',
                'event': '#f39c12',
                'document': '#9b59b6',
                'transaction': '#1abc9c',
                'vehicle': '#34495e',
                'weapon': '#c0392b'
            },
            'relationship_types': {
                'works_at': '#95a5a6',
                'owns': '#d35400',
                'located_in': '#27ae60',
                'knows': '#8e44ad',
                'related_to': '#f1c40f',
                'transaction': '#16a085',
                'member_of': '#2c3e50'
            }
        }
    
    def create_interactive_graph(self, graph_data: Dict[str, Any], 
                            layout: str = "force_directed",
                            node_size_metric: str = "degree",
                            edge_width_metric: str = "weight") -> go.Figure:
        """Create interactive 2D/3D graph using Plotly"""
        
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        if not nodes:
            return go.Figure()
        
        # Create NetworkX graph for layout calculations
        G = nx.Graph()
        
        # Add nodes with attributes
        node_positions = {}
        node_sizes = []
        node_colors = []
        node_labels = []
        
        for node in nodes:
            node_id = node['id']
            G.add_node(node_id, **node)
            
            # Calculate node size based on metric
            if node_size_metric == "degree":
                size = len([e for e in edges if e['source'] == node_id or e['target'] == node_id])
            elif node_size_metric == "betweenness":
                size = nx.betweenness_centrality(G).get(node_id, 0) * 50 + 10
            else:
                size = node.get('size', 20)
            
            node_sizes.append(size)
            
            # Color by entity type
            entity_type = node.get('type', 'default')
            color = self.color_schemes['entity_types'].get(entity_type, '#7f8c8d')
            node_colors.append(color)
            
            # Label
            node_labels.append(node.get('name', node_id))
        
        # Add edges
        for edge in edges:
            G.add_edge(edge['source'], edge['target'], **edge)
        
        # Calculate layout
        if layout == "force_directed":
            pos = nx.spring_layout(G, k=1, iterations=50)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "random":
            pos = nx.random_layout(G)
        elif layout == "shell":
            pos = nx.shell_layout(G)
        else:
            pos = nx.spring_layout(G)
        
        # Extract coordinates
        x_coords = [pos[node['id']][0] for node in nodes]
        y_coords = [pos[node['id']][1] for node in nodes]
        
        # Create edge traces
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in edges:
            x0, y0 = pos[edge['source']]
            x1, y1 = pos[edge['target']]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            # Edge info for hover
            edge_info.append(f"{edge.get('type', 'related')}")
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines',
            name='Connections'
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            mode='markers+text',
            hoverinfo='text',
            text=node_labels,
            textposition="middle center",
            hovertext=[f"{node['name']}<br>Type: {node.get('type', 'unknown')}" for node in nodes],
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='white')
            ),
            name='Entities'
        ))
        
        # Update layout
        fig.update_layout(
            title="Interactive Network Graph",
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Network Graph Visualization",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='#888', size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        return fig
    
    def create_pyvis_graph(self, graph_data: Dict[str, Any], 
                         output_file: str = "network.html") -> str:
        """Create force-directed graph using PyVis"""
        
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        # Create PyVis network
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
        
        # Add nodes
        for node in nodes:
            entity_type = node.get('type', 'default')
            color = self.color_schemes['entity_types'].get(entity_type, '#7f8c8d')
            
            net.add_node(
                node['id'],
                label=node.get('name', node['id']),
                title=f"{node.get('name', node['id'])}<br>Type: {entity_type}<br>{node.get('description', '')}",
                color=color,
                size=node.get('size', 20),
                font={'size': 12, 'color': 'white'}
            )
        
        # Add edges
        for edge in edges:
            rel_type = edge.get('type', 'related')
            color = self.color_schemes['relationship_types'].get(rel_type, '#95a5a6')
            
            net.add_edge(
                edge['source'],
                edge['target'],
                title=f"{rel_type}<br>Strength: {edge.get('strength', 1)}",
                color=color,
                width=edge.get('strength', 1),
                font={'size': 10, 'color': 'white'}
            )
        
        # Configure physics
        net.set_options("""
        var options = {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 100,
              "springConstant": 0.08
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based"
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 200,
            "hideEdgesOnDrag": true
          },
          "layout": {
            "improvedLayout": true
          }
        }
        """)
        
        # Save to file
        net.save_graph(output_file)
        return output_file
    
    def create_statistical_charts(self, data: Dict[str, Any], 
                              chart_type: str = "bar") -> go.Figure:
        """Create statistical charts using Plotly Express"""
        
        if chart_type == "entity_distribution":
            return self._create_entity_distribution_chart(data)
        elif chart_type == "relationship_types":
            return self._create_relationship_types_chart(data)
        elif chart_type == "temporal_analysis":
            return self._create_temporal_analysis_chart(data)
        elif chart_type == "centrality_analysis":
            return self._create_centrality_analysis_chart(data)
        else:
            return go.Figure()
    
    def _create_entity_distribution_chart(self, data: Dict[str, Any]) -> go.Figure:
        """Create entity type distribution chart"""
        entities = data.get('entities', [])
        
        # Count entity types
        type_counts = {}
        for entity in entities:
            entity_type = entity.get('type', 'unknown')
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        
        # Create bar chart
        fig = px.bar(
            x=list(type_counts.keys()),
            y=list(type_counts.values()),
            title="Entity Type Distribution",
            labels={'x': 'Entity Type', 'y': 'Count'},
            color=list(type_counts.keys()),
            color_discrete_map=self.color_schemes['entity_types']
        )
        
        fig.update_layout(
            showlegend=False,
            xaxis_title="Entity Type",
            yaxis_title="Count"
        )
        
        return fig
    
    def _create_relationship_types_chart(self, data: Dict[str, Any]) -> go.Figure:
        """Create relationship types pie chart"""
        relationships = data.get('relationships', [])
        
        # Count relationship types
        type_counts = {}
        for rel in relationships:
            rel_type = rel.get('type', 'unknown')
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        
        # Create pie chart
        fig = px.pie(
            values=list(type_counts.values()),
            names=list(type_counts.keys()),
            title="Relationship Types Distribution"
        )
        
        return fig
    
    def _create_temporal_analysis_chart(self, data: Dict[str, Any]) -> go.Figure:
        """Create temporal analysis chart"""
        events = data.get('events', [])
        
        if not events:
            return go.Figure()
        
        # Convert to DataFrame
        df = pd.DataFrame(events)
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            
            # Group by date
            daily_counts = df.groupby('date').size().reset_index(name='count')
            
            # Create line chart
            fig = px.line(
                daily_counts,
                x='date',
                y='count',
                title="Activity Timeline",
                labels={'date': 'Date', 'count': 'Event Count'}
            )
            
            return fig
        
        return go.Figure()
    
    def _create_centrality_analysis_chart(self, data: Dict[str, Any]) -> go.Figure:
        """Create centrality analysis chart"""
        graph_data = data.get('graph', {})
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        # Create NetworkX graph
        G = nx.Graph()
        for node in nodes:
            G.add_node(node['id'])
        for edge in edges:
            G.add_edge(edge['source'], edge['target'])
        
        # Calculate centrality measures
        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        closeness_centrality = nx.closeness_centrality(G)
        
        # Prepare data for plotting
        centrality_data = []
        for node_id in degree_centrality:
            node_name = next((n['name'] for n in nodes if n['id'] == node_id), node_id)
            centrality_data.append({
                'Node': node_name,
                'Degree Centrality': degree_centrality[node_id],
                'Betweenness Centrality': betweenness_centrality[node_id],
                'Closeness Centrality': closeness_centrality[node_id]
            })
        
        df = pd.DataFrame(centrality_data)
        
        # Create subplot
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Degree Centrality', 'Betweenness Centrality', 
                          'Closeness Centrality', 'Node Comparison'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "scatter"}]]
        )
        
        # Add centrality charts
        fig.add_trace(
            go.Bar(x=df['Node'], y=df['Degree Centrality'], name='Degree'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=df['Node'], y=df['Betweenness Centrality'], name='Betweenness'),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Bar(x=df['Node'], y=df['Closeness Centrality'], name='Closeness'),
            row=2, col=1
        )
        
        # Add scatter comparison
        fig.add_trace(
            go.Scatter(
                x=df['Degree Centrality'],
                y=df['Betweenness Centrality'],
                mode='markers+text',
                text=df['Node'],
                name='Centrality Comparison'
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=False, title_text="Network Centrality Analysis")
        
        return fig
    
    def create_geospatial_map(self, data: Dict[str, Any], 
                           map_type: str = "scatter") -> go.Figure:
        """Create geospatial visualization (placeholder for future Folium/PyDeck integration)"""
        
        # Extract location data
        entities = data.get('entities', [])
        locations = []
        
        for entity in entities:
            if entity.get('type') == 'location':
                lat = entity.get('attributes', {}).get('latitude')
                lon = entity.get('attributes', {}).get('longitude')
                if lat and lon:
                    locations.append({
                        'name': entity.get('name'),
                        'lat': lat,
                        'lon': lon,
                        'description': entity.get('description', '')
                    })
        
        if not locations:
            # Create empty map with message
            fig = go.Figure()
            fig.add_annotation(
                text="No location data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=16)
            )
            return fig
        
        # Create scatter map
        df = pd.DataFrame(locations)
        
        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            hover_name="name",
            hover_data=["description"],
            color_discrete_sequence=["red"],
            zoom=10,
            height=600
        )
        
        fig.update_layout(
            mapbox_style="open-street-map",
            title="Geospatial Distribution"
        )
        
        return fig
    
    def create_streamlit_components(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Streamlit components for interactive visualization"""
        
        components = {}
        
        # Graph layout selector
        components['layout_selector'] = st.selectbox(
            "Select Graph Layout",
            options=["force_directed", "circular", "random", "shell"],
            index=0
        )
        
        # Node size metric selector
        components['node_size_metric'] = st.selectbox(
            "Node Size Metric",
            options=["degree", "betweenness", "fixed"],
            index=0
        )
        
        # Entity type filter
        entities = data.get('entities', [])
        entity_types = list(set(entity.get('type', 'unknown') for entity in entities))
        components['entity_type_filter'] = st.multiselect(
            "Filter by Entity Type",
            options=entity_types,
            default=entity_types
        )
        
        # Relationship strength slider
        components['strength_filter'] = st.slider(
            "Minimum Relationship Strength",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1
        )
        
        # Centrality threshold
        components['centrality_threshold'] = st.slider(
            "Centrality Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.05
        )
        
        return components
    
    def export_visualization(self, fig: go.Figure, filename: str, format: str = "html"):
        """Export visualization to file"""
        
        if format == "html":
            fig.write_html(filename)
        elif format == "png":
            fig.write_image(filename)
        elif format == "pdf":
            fig.write_image(filename)
        elif format == "svg":
            fig.write_image(filename)
        
        logger.info(f"Visualization exported to {filename}")

# Global visualization engine instance
visualization_engine = VisualizationEngine()
