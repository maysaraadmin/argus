import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import networkx as nx
import json
from typing import Dict, List
from datetime import datetime
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from argus.config import config
from argus.logging import get_logger
from src.ui.visualization_pages import viz_pages
from src.ui.enhanced_resolution import enhanced_resolution_ui
from src.ui.history_pages import HistoryPages

# Initialize logger
logger = get_logger(__name__)

# Page config
st.set_page_config(
    page_title="Argus MVP",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'graph_data' not in st.session_state:
    st.session_state.graph_data = {"nodes": [], "links": []}
if 'selected_entity' not in st.session_state:
    st.session_state.selected_entity = None

API_URL = "http://localhost:8000"

def call_api(endpoint: str, method: str = "GET", data: dict = None):
    """Call API endpoint"""
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=data)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def main():
    st.title("🔍 Argus MVP - Intelligence Analysis Platform")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            ["Dashboard", "History Study", "Advanced Graph Explorer", "Entity Resolution", "Data Import", 
             "Geospatial Analysis", "Temporal Analysis", "Network Metrics", "API Docs"]
        )
        
        st.divider()
        
        # Quick stats
        stats = call_api("/api/stats")
        if stats:
            st.metric("Entities", stats.get('entity_count', 0))
            st.metric("Relationships", stats.get('relationship_count', 0))
    
    # Page routing
    if page == "Dashboard":
        show_dashboard()
    elif page == "History Study":
        history_pages = HistoryPages()
        history_subpage = st.selectbox(
            "Select History Study Page",
            ["History Dashboard", "Timeline Viewer", "Figure Explorer", "Event Analyzer", "Period Browser", "Research Tools"]
        )
        
        if history_subpage == "History Dashboard":
            history_pages.render_history_dashboard()
        elif history_subpage == "Timeline Viewer":
            history_pages.render_timeline_viewer()
        elif history_subpage == "Figure Explorer":
            history_pages.render_figure_explorer()
        elif history_subpage == "Event Analyzer":
            history_pages.render_event_analyzer()
        elif history_subpage == "Period Browser":
            history_pages.render_period_browser()
        elif history_subpage == "Research Tools":
            history_pages.render_research_tools()
    elif page == "Advanced Graph Explorer":
        viz_pages.render_advanced_graph_explorer()
    elif page == "Graph Explorer":
        show_graph_explorer()
    elif page == "Entity Resolution":
        enhanced_resolution_ui.render_enhanced_resolution_page()
    elif page == "Data Import":
        show_data_import()
    elif page == "Geospatial Analysis":
        viz_pages.render_geospatial_analysis()
    elif page == "Temporal Analysis":
        viz_pages.render_temporal_analysis()
    elif page == "Network Metrics":
        viz_pages.render_network_metrics()
    elif page == "API Docs":
        show_api_docs()

def show_dashboard():
    """Dashboard page"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Quick Search")
        search_query = st.text_input("Search entities...", key="dashboard_search")
        if search_query:
            results = call_api("/api/search", data={"q": search_query})
            if results and results.get('results'):
                df = pd.DataFrame(results['results'])
                st.dataframe(df[['id', 'name', 'type']], use_container_width=True)
    
    with col2:
        st.subheader("Recent Connections")
        # Example connections
        connections = [
            {"from": "Alice", "to": "Bob", "type": "knows"},
            {"from": "Bob", "to": "Charlie", "type": "works_with"},
            {"from": "Alice", "to": "Company X", "type": "employee"}
        ]
        st.table(pd.DataFrame(connections))
    
    with col3:
        st.subheader("System Status")
        st.info("✅ API: Online")
        st.info("✅ Database: Connected")
        st.info("⚠️ Cache: 75% used")
    
    # Entity type distribution
    st.subheader("Entity Distribution")
    stats = call_api("/api/stats")
    if stats and 'entity_types' in stats:
        types_data = stats['entity_types']
        fig = go.Figure(data=[go.Pie(labels=list(types_data.keys()), 
                                    values=list(types_data.values()))])
        st.plotly_chart(fig, use_container_width=True)

def show_graph_explorer():
    """Graph explorer page"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Entity Lookup")
        
        # Entity search
        search_term = st.text_input("Find entity", placeholder="Enter name or ID")
        if search_term:
            results = call_api("/api/search", data={"q": search_term})
            if results and results.get('results'):
                entities = results['results']
                entity_options = {e['name']: e['id'] for e in entities}
                selected_name = st.selectbox("Select entity", list(entity_options.keys()))
                if selected_name:
                    st.session_state.selected_entity = entity_options[selected_name]
        
        # Manual entity ID
        entity_id = st.text_input("Or enter Entity ID", 
                                value=st.session_state.selected_entity or "")
        
        depth = st.slider("Connection Depth", 1, 5, 2)
        
        if st.button("Load Network") and entity_id:
            with st.spinner("Loading network..."):
                data = call_api(f"/api/graph/{entity_id}", 
                              data={"depth": depth})
                if data:
                    st.session_state.graph_data = data
                    st.success(f"Loaded {len(data['nodes'])} nodes")
        
        # Connection finder
        st.subheader("Find Connections")
        col_a, col_b = st.columns(2)
        with col_a:
            entity_a = st.text_input("Entity A")
        with col_b:
            entity_b = st.text_input("Entity B")
        
        if st.button("Find Paths") and entity_a and entity_b:
            paths = call_api("/api/connections", 
                           data={"source": entity_a, "target": entity_b})
            if paths and paths.get('paths'):
                st.write(f"Found {paths['path_count']} path(s):")
                for i, path in enumerate(paths['paths'][:5]):  # Show first 5
                    st.write(f"{i+1}. {' → '.join(path)}")
    
    with col2:
        st.subheader("Knowledge Graph")
        
        if st.session_state.graph_data['nodes']:
            # Create network visualization with Plotly
            fig = create_network_visualization(st.session_state.graph_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show node details
            st.subheader("Entity Details")
            nodes_df = pd.DataFrame(st.session_state.graph_data['nodes'])
            st.dataframe(nodes_df, use_container_width=True)
        else:
            st.info("No graph data loaded. Search for an entity to visualize.")

def create_network_visualization(graph_data: Dict) -> go.Figure:
    """Create Plotly network visualization"""
    # Create positions using networkx
    G = nx.Graph()
    for node in graph_data['nodes']:
        G.add_node(node['id'], **node)
    for link in graph_data['links']:
        G.add_edge(link['source'], link['target'], **link)
    
    # Use spring layout
    pos = nx.spring_layout(G, seed=42)
    
    # Create edge traces
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create node traces
    node_x, node_y, node_text, node_color = [], [], [], []
    color_map = {
        'person': '#FF6B6B',
        'organization': '#4ECDC4',
        'location': '#45B7D1',
        'default': '#96CEB4'
    }
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        node_data = G.nodes[node]
        node_text.append(f"{node_data.get('label', node)}<br>Type: {node_data.get('type', 'unknown')}")
        node_color.append(color_map.get(node_data.get('type'), color_map['default']))
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        textposition="top center",
        marker=dict(
            size=20,
            color=node_color,
            line_width=2
        ),
        text=node_text
    )
    
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=0, l=0, r=0, t=0),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                   ))
    
    return fig

def show_entity_resolution():
    """Entity resolution page"""
    st.header("Entity Resolution")
    
    tab1, tab2 = st.tabs(["Batch Resolution", "Pair Matching"])
    
    with tab1:
        st.subheader("Upload Data for Deduplication")
        
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:", df.head())
            
            if st.button("Resolve Entities"):
                with st.spinner("Resolving duplicates..."):
                    # Convert to list of dicts
                    entities = df.to_dict('records')
                    result = call_api("/api/resolve", method="POST", 
                                    data={"entities": entities})
                    
                    if result:
                        st.success(f"Found {result['matches_found']} matches")
                        
                        # Show matches
                        if result['matches']:
                            matches_df = pd.DataFrame(result['matches'])
                            st.dataframe(matches_df, use_container_width=True)
    
    with tab2:
        st.subheader("Compare Two Entities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Entity 1")
            e1_name = st.text_input("Name", key="e1_name")
            e1_dob = st.text_input("Date of Birth", key="e1_dob")
            e1_address = st.text_input("Address", key="e1_address")
        
        with col2:
            st.write("Entity 2")
            e2_name = st.text_input("Name", key="e2_name")
            e2_dob = st.text_input("Date of Birth", key="e2_dob")
            e2_address = st.text_input("Address", key="e2_address")
        
        if st.button("Compare Entities"):
            entity1 = {
                "name": e1_name,
                "dob": e1_dob,
                "address": e1_address
            }
            entity2 = {
                "name": e2_name,
                "dob": e2_dob,
                "address": e2_address
            }
            
            # Calculate similarity
            from src.core.resolver import EntityResolver
            resolver = EntityResolver()
            score, is_match = resolver.resolve_single_pair(entity1, entity2)
            
            st.metric("Similarity Score", f"{score:.2%}")
            if is_match:
                st.success("✅ Likely the same entity")
            else:
                st.warning("❌ Different entities")

def show_data_import():
    """Data import page"""
    st.header("Data Import")
    
    import_type = st.selectbox(
        "Import Type",
        ["CSV/Excel", "JSON", "Database", "API"]
    )
    
    if import_type == "CSV/Excel":
        files = st.file_uploader(
            "Upload files",
            type=['csv', 'xlsx', 'xls'],
            accept_multiple_files=True
        )
        
        if files:
            for file in files:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                st.write(f"**{file.name}** - {len(df)} rows")
                st.dataframe(df.head(), use_container_width=True)
                
                # Entity type mapping
                st.subheader("Column Mapping")
                col1, col2 = st.columns(2)
                with col1:
                    name_col = st.selectbox("Name Column", df.columns, key=f"name_{file.name}")
                    type_col = st.selectbox("Type Column", ["person", "organization", "location"], 
                                          key=f"type_{file.name}")
                with col2:
                    id_col = st.selectbox("ID Column", df.columns, key=f"id_{file.name}")
                
                if st.button(f"Import {file.name}", key=f"btn_{file.name}"):
                    # Import logic
                    st.success(f"Imported {len(df)} entities from {file.name}")
    
    elif import_type == "API":
        st.subheader("API Configuration")
        api_url = st.text_input("API URL")
        auth_type = st.selectbox("Authentication", ["None", "API Key", "OAuth2"])
        
        if auth_type == "API Key":
            api_key = st.text_input("API Key", type="password")
        
        if st.button("Test Connection"):
            st.info("Connection test would run here")

def show_api_docs():
    """API documentation page"""
    st.header("API Documentation")
    
    endpoints = [
        {
            "method": "GET",
            "endpoint": "/api/entities/{id}",
            "description": "Get entity details"
        },
        {
            "method": "POST",
            "endpoint": "/api/entities",
            "description": "Create new entity"
        },
        {
            "method": "GET",
            "endpoint": "/api/graph/{id}",
            "description": "Get entity network"
        },
        {
            "method": "GET",
            "endpoint": "/api/search",
            "description": "Search entities"
        },
        {
            "method": "GET",
            "endpoint": "/api/connections",
            "description": "Find connections between entities"
        },
        {
            "method": "POST",
            "endpoint": "/api/resolve",
            "description": "Resolve duplicate entities"
        }
    ]
    
    st.table(pd.DataFrame(endpoints))
    
    st.subheader("Quick Test")
    endpoint = st.selectbox("Select endpoint", [e["endpoint"] for e in endpoints])
    if endpoint:
        if st.button("Try it"):
            response = call_api(endpoint.replace("{id}", "test"))
            if response:
                st.json(response)

if __name__ == "__main__":
    main()