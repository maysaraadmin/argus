"""
Open-source map integration for Historical Intelligence Analysis System (HIAS).
Provides interactive mapping capabilities using open-source mapping libraries.
"""

import streamlit as st
import pandas as pd
import folium
from folium import plugins
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import tempfile
import os
import sys
import time

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.history_engine import HistoryEngine
from src.data.history_models import EventType, HistoricalEvent, HistoricalFigure

# Open-source mapping libraries
try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

try:
    import contextily as ctx
    CONTEXTILY_AVAILABLE = True
except ImportError:
    CONTEXTILY_AVAILABLE = False

from src.core.history_engine import HistoryEngine
from src.data.history_models import HistoricalEvent, HistoricalFigure


class OpenSourceMap:
    """Open-source mapping capabilities for historical analysis"""
    
    def __init__(self, history_engine: HistoryEngine):
        self.engine = history_engine
    
    def render_interactive_map(self):
        """Render interactive historical map"""
        st.header("🗺️ Interactive Historical Map")
        
        if not FOLIUM_AVAILABLE:
            st.error("Folium library not available. Install with: pip install folium")
            return
        
        # Map controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Map Controls")
            
            # Time period filter
            periods = list(self.engine.periods.values())
            if periods:
                period_options = {period.name: period.id for period in periods}
                selected_period_name = st.selectbox("Select Period", list(period_options.keys()))
                selected_period = self.engine.periods[period_options[selected_period_name]]
                
                # Event type filter
                event_types = ["All", "Military", "Political", "Social", "Economic", "Cultural"]
                selected_event_type = st.selectbox("Event Type", event_types)
            
            # Geographic filter
            regions = list(set(event.location for event in self.engine.events.values()))
            selected_region = st.selectbox("Filter by Region", ["All"] + regions)
        
        with col2:
            st.subheader("Map Layers")
            
            # Layer options
            show_events = st.checkbox("Show Events", True)
            show_figures = st.checkbox("Show Figures", True)
            show_routes = st.checkbox("Show Routes", False)
            show_borders = st.checkbox("Show Historical Borders", True)
            
            # Base map selection
            map_styles = ["OpenStreetMap", "CartoDB", "Stamen Terrain", "Stamen Toner"]
            selected_style = st.selectbox("Map Style", map_styles)
        
        with col3:
            st.subheader("Analysis Tools")
            
            # Analysis options
            analysis_type = st.selectbox("Analysis Type", [
                "Event Density", "Movement Patterns", "Influence Mapping", "Territorial Changes"
            ])
            
            # Heat map option
            show_heatmap = st.checkbox("Show Density Heatmap", False)
        
        # Generate map
        if st.button("Generate Map"):
            self._create_historical_map(
                selected_period, selected_event_type, selected_region,
                show_events, show_figures, show_routes, show_borders,
                selected_style, show_heatmap, analysis_type
            )
    
    def render_geospatial_analysis(self):
        """Advanced geospatial analysis with open-source tools"""
        st.header("🌍 Advanced Geospatial Analysis")
        
        if not GEOPANDAS_AVAILABLE:
            st.error("GeoPandas library not available. Install with: pip install geopandas")
            return
        
        # Analysis type selection
        analysis_type = st.selectbox("Analysis Type", [
            "Territorial Analysis",
            "Movement Analysis", 
            "Event Clustering",
            "Spatial Statistics"
        ])
        
        if analysis_type == "Territorial Analysis":
            self._render_territorial_analysis()
        elif analysis_type == "Movement Analysis":
            self._render_movement_analysis()
        elif analysis_type == "Event Clustering":
            self._render_event_clustering()
        elif analysis_type == "Spatial Statistics":
            self._render_spatial_statistics()
    
    def render_temporal_map(self):
        """Temporal map showing changes over time"""
        st.header("⏰ Temporal Historical Map")
        
        # Time controls
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Time Controls")
            
            # Date range
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            
            # Animation controls
            animation_speed = st.slider("Animation Speed (years/sec)", 1, 10, 2)
            auto_play = st.checkbox("Auto Play", False)
        
        with col2:
            st.subheader("Data Filters")
            
            # Filter options
            entity_types = st.multiselect("Show Entities", ["Events", "Figures", "Organizations"])
            min_importance = st.slider("Minimum Importance", 0, 10, 5)
        
        # Generate temporal map
        if st.button("Generate Temporal Map"):
            self._create_temporal_map(start_date, end_date, entity_types, min_importance)
    
    def _create_historical_map(self, period, event_type, region, 
                           show_events, show_figures, show_routes, show_borders,
                           map_style, show_heatmap, analysis_type):
        """Create the interactive historical map"""
        
        # Get filtered data
        events = self._get_filtered_events(period, event_type, region)
        figures = self._get_filtered_figures(period, region)
        
        # Create base map
        center_lat, center_lon = self._calculate_map_center(events, figures)
        
        # Initialize folium map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=4,
            tiles=self._get_tile_layer(map_style)
        )
        
        # Add event markers
        if show_events and events:
            for event in events:
                if event.coordinates:
                    folium.Marker(
                        location=event.coordinates,
                        popup=f"<strong>{event.title}</strong><br>{event.date}<br>{event.description[:100]}...",
                        icon=self._get_event_icon(event.event_type),
                        tooltip=event.title
                    ).add_to(m)
        
        # Add figure markers
        if show_figures and figures:
            for figure in figures:
                if figure.birth_place:
                    # Geocode birth place (simplified)
                    coords = self._geocode_location(figure.birth_place)
                    if coords:
                        folium.Marker(
                            location=coords,
                            popup=f"<strong>{figure.name}</strong><br>{figure.era}<br>{figure.occupation[0] if figure.occupation else ''}",
                            icon=folium.Icon(color='blue', icon='user'),
                            tooltip=figure.name
                        ).add_to(m)
        
        # Add movement routes
        if show_routes:
            self._add_movement_routes(m, events, figures)
        
        # Add historical borders
        if show_borders:
            self._add_historical_borders(m, period)
        
        # Add heatmap layer
        if show_heatmap and events:
            self._add_event_heatmap(m, events)
        
        # Display map
        folium_static(m, width=1200, height=600)
    
    def _render_territorial_analysis(self):
        """Render territorial change analysis"""
        st.subheader("🗺️ Territorial Analysis")
        
        # Select time periods to compare
        periods = list(self.engine.periods.values())
        if len(periods) >= 2:
            period_options = {period.name: period.id for period in periods}
            col1, col2 = st.columns(2)
            
            with col1:
                period1_name = st.selectbox("First Period", list(period_options.keys()))
                period1 = self.engine.periods[period_options[period1_name]]
            
            with col2:
                period2_name = st.selectbox("Second Period", list(period_options.keys()))
                period2 = self.engine.periods[period_options[period2_name]]
            
            if st.button("Compare Territories"):
                self._compare_territories(period1, period2)
    
    def _render_movement_analysis(self):
        """Render movement pattern analysis"""
        st.subheader("🚶 Movement Analysis")
        
        # Select figure to track
        figures = list(self.engine.figures.values())
        if figures:
            selected_figure_name = st.selectbox("Select Figure", [fig.name for fig in figures])
            selected_figure = next(fig for fig in figures if fig.name == selected_figure_name)
            
            if st.button("Analyze Movement"):
                self._analyze_figure_movement(selected_figure)
    
    def _render_event_clustering(self):
        """Render event clustering analysis"""
        st.subheader("📊 Event Clustering")
        
        # Clustering parameters
        col1, col2 = st.columns(2)
        
        with col1:
            cluster_method = st.selectbox("Clustering Method", ["K-Means", "DBSCAN", "Hierarchical"])
            n_clusters = st.slider("Number of Clusters", 2, 10, 3)
        
        with col2:
            cluster_type = st.selectbox("Cluster By", ["Location", "Time", "Event Type"])
        
        if st.button("Cluster Events"):
            self._perform_event_clustering(cluster_method, n_clusters, cluster_type)
    
    def _render_spatial_statistics(self):
        """Render spatial statistics analysis"""
        st.subheader("📈 Spatial Statistics")
        
        # Statistics type
        stat_type = st.selectbox("Statistics Type", [
            "Event Distribution",
            "Distance Analysis", 
            "Density Analysis",
            "Hotspot Detection"
        ])
        
        if stat_type == "Event Distribution":
            self._show_event_distribution()
        elif stat_type == "Distance Analysis":
            self._show_distance_analysis()
        elif stat_type == "Density Analysis":
            self._show_density_analysis()
        elif stat_type == "Hotspot Detection":
            self._show_hotspot_analysis()
    
    def _get_filtered_events(self, period, event_type, region):
        """Get events based on filters"""
        events = list(self.engine.events.values())
        
        # Filter by period
        if period:
            period_events = self.engine.find_events_by_period(period.id)
            events = [e for e in events if e in events]
        
        # Filter by type
        if event_type != "All":
            events = [e for e in events if e.event_type.value.lower() == event_type.lower()]
        
        # Filter by region
        if region != "All":
            events = [e for e in events if region.lower() in e.location.lower()]
        
        return events
    
    def _get_filtered_figures(self, period, region):
        """Get figures based on filters"""
        figures = list(self.engine.figures.values())
        
        # Filter by period
        if period:
            # Simple date overlap check
            figures = [f for f in figures if self._figure_in_period(f, period)]
        
        # Filter by region (based on birth/death places)
        if region != "All":
            figures = [f for f in figures if 
                      region.lower() in (f.birth_place or "").lower() or 
                      region.lower() in (f.death_place or "").lower()]
        
        return figures
    
    def _figure_in_period(self, figure, period):
        """Check if figure was active during period"""
        if not figure.birth_date:
            return False
        
        figure_start = figure.birth_date
        figure_end = figure.death_date or date.today()
        
        period_start = period.start_date
        period_end = period.end_date or date.today()
        
        return not (figure_end < period_start or figure_start > period_end)
    
    def _calculate_map_center(self, events, figures):
        """Calculate center point for map"""
        all_coords = []
        
        # Add event coordinates
        for event in events:
            if event.coordinates:
                all_coords.append(event.coordinates)
        
        # Add figure birth places (simplified geocoding)
        for figure in figures:
            if figure.birth_place:
                coords = self._geocode_location(figure.birth_place)
                if coords:
                    all_coords.append(coords)
        
        if all_coords:
            avg_lat = sum(coord[0] for coord in all_coords) / len(all_coords)
            avg_lon = sum(coord[1] for coord in all_coords) / len(all_coords)
            return avg_lat, avg_lon
        
        # Default center
        return 30.0, 0.0
    
    def _geocode_location(self, location_name):
        """Simple geocoding (placeholder - would use real geocoding service)"""
        # Simplified coordinate mapping for major historical locations
        location_coords = {
            "rome": (41.9028, 12.4964),
            "athens": (37.9838, 23.7275),
            "alexandria": (31.2156, 29.9553),
            "london": (51.5074, -0.1278),
            "paris": (48.8566, 2.3522),
            "constantinople": (41.0082, 28.9784),
            "vienna": (48.2082, 16.3738),
            "berlin": (52.5200, 13.4050),
        }
        
        location_key = location_name.lower().replace(",", "").strip()
        return location_coords.get(location_key)
    
    def _get_event_icon(self, event_type):
        """Get appropriate icon for event type"""
        icon_map = {
            "military": "flag",
            "political": "university",
            "social": "users",
            "economic": "usd",
            "cultural": "camera",
            "religious": "home",
            "technological": "cog",
            "default": "info-sign"
        }
        return folium.Icon(color='red', icon=icon_map.get(event_type.value, "info-sign"))
    
    def _get_tile_layer(self, style):
        """Get tile layer for map style"""
        tile_layers = {
            "OpenStreetMap": "OpenStreetMap",
            "CartoDB": "CartoDB positron",
            "Stamen Terrain": "Stamen Terrain",
            "Stamen Toner": "Stamen Toner"
        }
        return tile_layers.get(style, "OpenStreetMap")
    
    def _add_movement_routes(self, map_obj, events, figures):
        """Add movement routes to map"""
        # Simple route drawing (would be enhanced with real routing data)
        for figure in figures[:3]:  # Limit to first 3 figures
            # Find events this figure participated in
            figure_events = [e for e in events if figure.id in e.participants]
            
            if len(figure_events) > 1:
                # Create route between event locations
                route_coords = []
                for event in figure_events:
                    if event.coordinates:
                        route_coords.append(event.coordinates)
                
                if len(route_coords) > 1:
                    folium.PolyLine(
                        locations=route_coords,
                        color='blue',
                        weight=3,
                        opacity=0.7,
                        popup=f"{figure.name}'s Movement Path"
                    ).add_to(map_obj)
    
    def _add_historical_borders(self, map_obj, period):
        """Add historical borders (simplified)"""
        # Simplified historical boundaries (would use real historical GIS data)
        historical_borders = {
            "Roman Empire": [(40.0, 10.0), (50.0, 30.0), (30.0, 20.0), (40.0, 10.0)],
            "Byzantine Empire": [(35.0, 25.0), (45.0, 40.0), (40.0, 20.0), (35.0, 25.0)],
            "Ottoman Empire": [(35.0, 25.0), (45.0, 30.0), (40.0, 20.0), (35.0, 25.0)],
        }
        
        # Add relevant borders based on period
        for empire_name, coords in historical_borders.items():
            if empire_name.lower() in period.name.lower():
                folium.Polygon(
                    locations=coords,
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.2,
                    popup=empire_name
                ).add_to(map_obj)
    
    def _add_event_heatmap(self, map_obj, events):
        """Add event density heatmap"""
        if not events:
            return
        
        # Create heatmap data
        heat_data = []
        for event in events:
            if event.coordinates:
                heat_data.append(event.coordinates + [0.5])  # Add intensity
        
        if heat_data:
            plugins.HeatMap(heat_data).add_to(map_obj)
    
    def _compare_territories(self, period1, period2):
        """Compare territories between two periods"""
        st.write(f"**Comparing {period1.name} vs {period2.name}**")
        
        # Get events for each period
        events1 = self.engine.find_events_by_period(period1.id)
        events2 = self.engine.find_events_by_period(period2.id)
        
        # Create comparison data
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{period1.name}**")
            st.write(f"- Events: {len(events1)}")
            st.write(f"- Time Range: {period1.start_date} to {period1.end_date}")
            
            # Event distribution
            if events1:
                event_types = {}
                for event in events1:
                    event_types[event.event_type.value] = event_types.get(event.event_type.value, 0) + 1
                st.write("**Event Types:**")
                for event_type, count in event_types.items():
                    st.write(f"- {event_type}: {count}")
        
        with col2:
            st.write(f"**{period2.name}**")
            st.write(f"- Events: {len(events2)}")
            st.write(f"- Time Range: {period2.start_date} to {period2.end_date}")
            
            # Event distribution
            if events2:
                event_types = {}
                for event in events2:
                    event_types[event.event_type.value] = event_types.get(event.event_type.value, 0) + 1
                st.write("**Event Types:**")
                for event_type, count in event_types.items():
                    st.write(f"- {event_type}: {count}")
    
    def _analyze_figure_movement(self, figure):
        """Analyze movement patterns of a historical figure"""
        st.write(f"**Movement Analysis: {figure.name}**")
        
        # Find events this figure participated in
        figure_events = []
        for event in self.engine.events.values():
            if figure.id in event.participants:
                figure_events.append(event)
        
        if figure_events:
            # Sort by date
            figure_events.sort(key=lambda e: e.date)
            
            st.write(f"**Total Events:** {len(figure_events)}")
            st.write(f"**Time Period:** {figure.era}")
            
            # Create movement timeline
            movement_data = []
            for event in figure_events:
                if event.coordinates:
                    movement_data.append({
                        "Date": event.date,
                        "Location": event.location,
                        "Event": event.title,
                        "Type": event.event_type.value
                    })
            
            if movement_data:
                df_movement = pd.DataFrame(movement_data)
                st.dataframe(df_movement, use_container_width=True)
                
                # Create simple movement map
                if len(figure_events) > 1:
                    st.write("**Movement Path:**")
                    coords = []
                    for event in figure_events:
                        if event.coordinates:
                            coords.append(event.coordinates)
                    
                    if len(coords) > 1:
                        # Create movement map
                        center_lat = sum(c[0] for c in coords) / len(coords)
                        center_lon = sum(c[1] for c in coords) / len(coords)
                        
                        m = folium.Map(
                            location=[center_lat, center_lon],
                            zoom_start=5
                        )
                        
                        # Add path
                        folium.PolyLine(
                            locations=coords,
                            color='blue',
                            weight=3,
                            opacity=0.7
                        ).add_to(m)
                        
                        # Add markers
                        for i, (event, coord) in enumerate(zip(figure_events, coords)):
                            folium.Marker(
                                location=coord,
                                popup=f"{event.title}<br>{event.date}",
                                tooltip=event.title
                            ).add_to(m)
                        
                        folium_static(m, width=800, height=400)
        else:
            st.info("No movement data found for this figure.")
    
    def _perform_event_clustering(self, method, n_clusters, cluster_type):
        """Perform clustering analysis on events"""
        events = list(self.engine.events.values())
        
        if not events:
            st.info("No events available for clustering.")
            return
        
        # Prepare data for clustering
        if cluster_type == "Location":
            # Use coordinates for clustering
            event_coords = []
            valid_events = []
            for event in events:
                if event.coordinates:
                    event_coords.append(event.coordinates)
                    valid_events.append(event)
            
            if len(event_coords) >= n_clusters:
                from sklearn.cluster import KMeans
                import numpy as np
                
                coords_array = np.array(event_coords)
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                clusters = kmeans.fit(coords_array)
                
                # Display clusters
                st.write(f"**Event Clusters by Location ({n_clusters} clusters):**")
                for i in range(n_clusters):
                    cluster_events = [valid_events[j] for j in range(len(valid_events)) 
                                   if clusters.labels_[j] == i]
                    st.write(f"**Cluster {i+1}:** {len(cluster_events)} events")
                    for event in cluster_events[:5]:  # Show first 5
                        st.write(f"- {event.title} ({event.date})")
        
        elif cluster_type == "Time":
            # Use dates for clustering
            event_years = []
            for event in events:
                event_years.append(event.date.year)
            
            if len(event_years) >= n_clusters:
                from sklearn.cluster import KMeans
                import numpy as np
                
                years_array = np.array(event_years).reshape(-1, 1)
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                clusters = kmeans.fit(years_array)
                
                # Display temporal clusters
                st.write(f"**Event Clusters by Time ({n_clusters} clusters):**")
                for i in range(n_clusters):
                    cluster_years = [event_years[j] for j in range(len(event_years)) 
                                   if clusters.labels_[j] == i]
                    st.write(f"**Cluster {i+1}:** Years {min(cluster_years)}-{max(cluster_years)}")
        
        else:
            st.info(f"Clustering by {cluster_type} not yet implemented.")
    
    def _show_event_distribution(self):
        """Show spatial distribution of events"""
        events = list(self.engine.events.values())
        
        if events:
            # Create distribution by location
            location_counts = {}
            for event in events:
                location_counts[event.location] = location_counts.get(event.location, 0) + 1
            
            # Display top locations
            top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            st.write("**Top Event Locations:**")
            for location, count in top_locations:
                st.write(f"- {location}: {count} events")
    
    def _show_distance_analysis(self):
        """Show distance analysis between events"""
        st.info("Distance analysis feature coming soon!")
    
    def _show_density_analysis(self):
        """Show event density analysis"""
        st.info("Density analysis feature coming soon!")
    
    def _show_hotspot_analysis(self):
        """Show hotspot detection"""
        st.info("Hotspot detection feature coming soon!")


def folium_static(map_obj, width=800, height=600):
    """Display folium map in Streamlit"""
    if FOLIUM_AVAILABLE:
        # Save map to temporary file and display
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
            map_obj.save(tmp_file.name)
            
            # Read and display
            with open(tmp_file.name, 'r', encoding='utf-8') as f:
                map_html = f.read()
            
            # Display in Streamlit
            st.components.v1.html(map_html, width=width, height=height)
            
            # Clean up with enhanced error handling
            try:
                # Close file handle first to release lock
                tmp_file.close()
                time.sleep(0.5)  # Brief wait for file release
                os.unlink(tmp_file.name)
            except (PermissionError, OSError) as e:
                st.warning(f"Could not clean up temporary file: {e}")
                # File will be cleaned up by OS eventually
            except Exception as e:
                st.error(f"Unexpected error during cleanup: {e}")
                # Use print instead of logger since logger might not be available
                print(f"Temporary file cleanup error: {e}")
    else:
        st.error("Folium not available for map display")
