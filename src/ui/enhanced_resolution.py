"""
Enhanced entity resolution UI for Argus MVP
Provides interactive match review and management
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.enhanced_resolver import enhanced_resolver, MatchingRule
from src.core.security import security_manager

class EnhancedResolutionUI:
    """Enhanced entity resolution user interface"""
    
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.current_matches = []
        self.reviewed_matches = []
    
    def render_enhanced_resolution_page(self):
        """Render the enhanced entity resolution page"""
        st.title("🔍 Enhanced Entity Resolution")
        st.markdown("---")
        
        # Create tabs for different resolution workflows
        tab1, tab2, tab3, tab4 = st.tabs([
            "⚙️ Configuration", 
            "🔍 Batch Resolution", 
            "👥 Match Review", 
            "📊 Resolution Statistics"
        ])
        
        with tab1:
            self._render_configuration_tab()
        
        with tab2:
            self._render_batch_resolution_tab()
        
        with tab3:
            self._render_match_review_tab()
        
        with tab4:
            self._render_statistics_tab()
    
    def _render_configuration_tab(self):
        """Render matching rules configuration"""
        st.subheader("🔧 Matching Rules Configuration")
        
        st.write("Configure how entities are matched during resolution:")
        
        # Display current rules
        rules_data = []
        for i, rule in enumerate(enhanced_resolver.matching_rules):
            rules_data.append({
                'Field': rule.field_name,
                'Type': rule.matching_type,
                'Weight': rule.weight,
                'Threshold': rule.threshold,
                'Enabled': '✅' if rule.enabled else '❌',
                'Preprocessing': ', '.join(rule.preprocessing) if rule.preprocessing else 'None'
            })
        
        df_rules = pd.DataFrame(rules_data)
        st.dataframe(df_rules, use_container_width=True)
        
        st.subheader("Edit Matching Rules")
        
        # Rule editor
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Add New Rule**")
            field_name = st.selectbox(
                "Field Name",
                options=["name", "email", "phone", "address", "dob", "ssn", "passport"],
                key="new_rule_field"
            )
            
            matching_type = st.selectbox(
                "Matching Type",
                options=["exact", "fuzzy", "phonetic", "numeric"],
                key="new_rule_type"
            )
            
            weight = st.slider(
                "Weight",
                min_value=0.0, max_value=1.0, value=0.1, step=0.05,
                key="new_rule_weight"
            )
            
            threshold = st.slider(
                "Threshold",
                min_value=0.0, max_value=1.0, value=0.7, step=0.05,
                key="new_rule_threshold"
            )
        
        with col2:
            st.write("**Preprocessing Options**")
            preprocessing_options = st.multiselect(
                "Preprocessing Steps",
                options=["lowercase", "uppercase", "remove_spaces", "remove_special_chars", 
                        "standardize_address", "normalize_phone", "remove_punctuation"],
                key="new_rule_preprocessing"
            )
            
            enabled = st.checkbox("Enable Rule", value=True, key="new_rule_enabled")
            
            if st.button("Add Rule", key="add_rule"):
                new_rule = MatchingRule(
                    field_name=field_name,
                    matching_type=matching_type,
                    weight=weight,
                    threshold=threshold,
                    enabled=enabled,
                    preprocessing=preprocessing_options
                )
                enhanced_resolver.matching_rules.append(new_rule)
                st.success(f"Added rule for {field_name}")
                st.rerun()
        
        # Existing rules editor
        st.subheader("Edit Existing Rules")
        
        if enhanced_resolver.matching_rules:
            rule_to_edit = st.selectbox(
                "Select Rule to Edit",
                options=[f"{rule.field_name} ({rule.matching_type})" for rule in enhanced_resolver.matching_rules],
                key="edit_rule_select"
            )
            
            if rule_to_edit:
                rule_index = [f"{rule.field_name} ({rule.matching_type})" for rule in enhanced_resolver.matching_rules].index(rule_to_edit)
                rule = enhanced_resolver.matching_rules[rule_index]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_weight = st.slider(
                        "Weight",
                        min_value=0.0, max_value=1.0, value=rule.weight, step=0.05,
                        key=f"edit_weight_{rule_index}"
                    )
                    
                    new_threshold = st.slider(
                        "Threshold",
                        min_value=0.0, max_value=1.0, value=rule.threshold, step=0.05,
                        key=f"edit_threshold_{rule_index}"
                    )
                
                with col2:
                    new_enabled = st.checkbox(
                        "Enabled",
                        value=rule.enabled,
                        key=f"edit_enabled_{rule_index}"
                    )
                    
                    if st.button("Update Rule", key=f"update_rule_{rule_index}"):
                        rule.weight = new_weight
                        rule.threshold = new_threshold
                        rule.enabled = new_enabled
                        st.success(f"Updated rule for {rule.field_name}")
                        st.rerun()
    
    def _render_batch_resolution_tab(self):
        """Render batch entity resolution"""
        st.subheader("🔍 Batch Entity Resolution")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload CSV file for entity resolution",
            type=['csv'],
            key="resolution_upload"
        )
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.write(f"📊 Loaded {len(df)} entities")
                st.dataframe(df.head(), use_container_width=True)
                
                # Resolution options
                st.subheader("Resolution Options")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    min_confidence = st.slider(
                        "Minimum Confidence",
                        min_value=0.0, max_value=1.0, value=0.5, step=0.05
                    )
                
                with col2:
                    max_candidates = st.number_input(
                        "Max Candidates per Entity",
                        min_value=1, max_value=50, value=10
                    )
                
                with col3:
                    use_blocking = st.checkbox(
                        "Use Blocking (Faster)",
                        value=True
                    )
                
                if st.button("🚀 Start Resolution", key="start_batch_resolution"):
                    with st.spinner("Resolving entities..."):
                        entities = df.to_dict('records')
                        
                        # Process entities
                        for entity in entities:
                            enhanced_resolver.processed_entities[entity.get('id', '')] = entity
                        
                        # Run resolution
                        matches = enhanced_resolver.resolve_batch(entities)
                        
                        # Filter by minimum confidence
                        filtered_matches = [
                            match for match in matches 
                            if match.confidence_score >= min_confidence
                        ]
                        
                        # Limit candidates
                        if max_candidates > 0:
                            # Group by entity1_id and limit candidates
                            entity_groups = {}
                            for match in filtered_matches:
                                if match.entity1_id not in entity_groups:
                                    entity_groups[match.entity1_id] = []
                                entity_groups[match.entity1_id].append(match)
                            
                            limited_matches = []
                            for entity_id, group_matches in entity_groups.items():
                                limited_matches.extend(group_matches[:max_candidates])
                            
                            filtered_matches = limited_matches
                        
                        self.current_matches = filtered_matches
                        
                        st.success(f"Found {len(filtered_matches)} potential matches")
                        
            except Exception as e:
                st.error(f"Error processing file: {e}")
        
        # Display current matches
        if self.current_matches:
            st.subheader(f"🎯 Match Candidates ({len(self.current_matches)} total)")
            
            # Confidence distribution
            confidences = [m.confidence_score for m in self.current_matches]
            fig = px.histogram(
                x=confidences,
                nbins=20,
                title="Confidence Score Distribution",
                labels={"x": "Confidence Score", "y": "Count"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Match details table
            self._display_matches_table(self.current_matches, "current")
    
    def _render_match_review_tab(self):
        """Render match review interface"""
        st.subheader("👥 Match Review & Confirmation")
        
        if not self.current_matches:
            st.info("No matches to review. Please run batch resolution first.")
            return
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            confidence_filter = st.slider(
                "Minimum Confidence",
                min_value=0.0, max_value=1.0, value=0.0, step=0.05
            )
        
        with col2:
            status_filter = st.selectbox(
                "Filter by Status",
                options=["All", "Pending", "Confirmed", "Rejected"],
                key="status_filter"
            )
        
        with col3:
            match_type_filter = st.multiselect(
                "Filter by Match Type",
                options=["high_confidence", "medium_confidence", "low_confidence"],
                key="match_type_filter"
            )
        
        # Apply filters
        filtered_matches = []
        for match in self.current_matches:
            # Confidence filter
            if match.confidence_score < confidence_filter:
                continue
            
            # Status filter
            if status_filter != "All":
                if status_filter == "Pending" and match.user_decision is not None:
                    continue
                elif status_filter == "Confirmed" and match.user_decision != "confirm":
                    continue
                elif status_filter == "Rejected" and match.user_decision != "reject":
                    continue
            
            # Match type filter
            if match_type_filter and match.match_type not in match_type_filter:
                continue
            
            filtered_matches.append(match)
        
        st.write(f"Showing {len(filtered_matches)} of {len(self.current_matches)} matches")
        
        if filtered_matches:
            # Match review interface
            for i, match in enumerate(filtered_matches[:10]):  # Show first 10
                with st.expander(f"🎯 Match {i+1}: {match.entity1_data.get('name', 'Unknown')} ↔ {match.entity2_data.get('name', 'Unknown')} (Confidence: {match.confidence_score:.2f})"):
                    self._render_match_details(match)
        
        # Batch actions
        st.subheader("🔧 Batch Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Confirm All High Confidence", key="confirm_high"):
                confirmed_count = 0
                for match in self.current_matches:
                    if match.confidence_score >= 0.8 and match.user_decision is None:
                        match.user_decision = "confirm"
                        match.reviewed_at = datetime.now()
                        confirmed_count += 1
                st.success(f"Confirmed {confirmed_count} high-confidence matches")
        
        with col2:
            if st.button("❌ Reject All Low Confidence", key="reject_low"):
                rejected_count = 0
                for match in self.current_matches:
                    if match.confidence_score < 0.6 and match.user_decision is None:
                        match.user_decision = "reject"
                        match.reviewed_at = datetime.now()
                        rejected_count += 1
                st.success(f"Rejected {rejected_count} low-confidence matches")
        
        with col3:
            if st.button("🔄 Reset All Decisions", key="reset_decisions"):
                for match in self.current_matches:
                    match.user_decision = None
                    match.reviewed_at = None
                    match.reviewed_by = None
                st.success("Reset all match decisions")
    
    def _render_match_details(self, match):
        """Render detailed match information"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Entity 1**")
            st.write(f"**ID:** {match.entity1_id}")
            st.write(f"**Name:** {match.entity1_data.get('name', 'N/A')}")
            st.write(f"**Type:** {match.entity1_data.get('type', 'N/A')}")
            
            # Show attributes
            attrs1 = match.entity1_data.get('attributes', {})
            if attrs1:
                st.write("**Attributes:**")
                for key, value in attrs1.items():
                    st.write(f"- {key}: {value}")
        
        with col2:
            st.write("**Entity 2**")
            st.write(f"**ID:** {match.entity2_id}")
            st.write(f"**Name:** {match.entity2_data.get('name', 'N/A')}")
            st.write(f"**Type:** {match.entity2_data.get('type', 'N/A')}")
            
            # Show attributes
            attrs2 = match.entity2_data.get('attributes', {})
            if attrs2:
                st.write("**Attributes:**")
                for key, value in attrs2.items():
                    st.write(f"- {key}: {value}")
        
        # Match details
        st.write("**Match Analysis**")
        st.write(f"**Overall Confidence:** {match.confidence_score:.3f}")
        st.write(f"**Match Type:** {match.match_type}")
        
        # Field-level scores
        if 'field_scores' in match.match_details:
            st.write("**Field-Level Scores:**")
            field_scores = match.match_details['field_scores']
            
            for field, score_info in field_scores.items():
                with st.expander(f"📊 {field.title()} Field"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.metric("Similarity", f"{score_info['similarity']:.3f}")
                        st.metric("Weight", f"{score_info['weight']:.2f}")
                        st.metric("Weighted Score", f"{score_info['weighted_score']:.3f}")
                    
                    with col_b:
                        st.write(f"**Threshold:** {score_info['threshold']:.2f}")
                        st.write(f"**Matched:** {'✅' if score_info['matched'] else '❌'}")
                        
                        # Show values if available
                        val1 = match.entity1_data.get('attributes', {}).get(field, '')
                        val2 = match.entity2_data.get('attributes', {}).get(field, '')
                        if val1 and val2:
                            st.write(f"**Value 1:** {val1}")
                            st.write(f"**Value 2:** {val2}")
        
        # Decision buttons
        st.write("**Decision**")
        col1, col2, col3 = st.columns(3)
        
        match_id = f"{match.entity1_id}_{match.entity2_id}"
        
        with col1:
            if st.button("✅ Confirm Match", key=f"confirm_{match_id}"):
                match.user_decision = "confirm"
                match.reviewed_at = datetime.now()
                st.success("Match confirmed")
                st.rerun()
        
        with col2:
            if st.button("❌ Reject Match", key=f"reject_{match_id}"):
                match.user_decision = "reject"
                match.reviewed_at = datetime.now()
                st.success("Match rejected")
                st.rerun()
        
        with col3:
            if st.button("⏭️ Defer Decision", key=f"defer_{match_id}"):
                match.user_decision = "defer"
                match.reviewed_at = datetime.now()
                st.success("Decision deferred")
                st.rerun()
    
    def _display_matches_table(self, matches: List, table_id: str):
        """Display matches in a table format"""
        if not matches:
            return
        
        # Prepare table data
        table_data = []
        for match in matches:
            table_data.append({
                'Entity 1': match.entity1_data.get('name', 'N/A'),
                'Entity 2': match.entity2_data.get('name', 'N/A'),
                'Confidence': f"{match.confidence_score:.3f}",
                'Match Type': match.match_type.replace('_', ' ').title(),
                'Decision': match.user_decision or 'Pending',
                'Reviewed': match.reviewed_at.strftime('%Y-%m-%d %H:%M') if match.reviewed_at else 'Not reviewed'
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export to CSV", key=f"export_csv_{table_id}"):
                csv_data = enhanced_resolver.export_matches("csv")
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"entity_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📥 Export to JSON", key=f"export_json_{table_id}"):
                json_data = enhanced_resolver.export_matches("json")
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"entity_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    def _render_statistics_tab(self):
        """Render resolution statistics"""
        st.subheader("📊 Resolution Statistics")
        
        if not self.current_matches:
            st.info("No resolution data available.")
            return
        
        stats = enhanced_resolver.get_match_statistics()
        
        if not stats:
            return
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Candidates", stats['total_candidates'])
        
        with col2:
            st.metric("Confirmed", stats['confirmed'])
        
        with col3:
            st.metric("Rejected", stats['rejected'])
        
        with col4:
            st.metric("Pending", stats['pending'])
        
        # Confirmation rate
        st.subheader("📈 Performance Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Confirmation Rate", f"{stats['confirmation_rate']:.1%}")
            st.metric("Avg Confidence", f"{stats['average_confidence']:.3f}")
        
        with col2:
            st.metric("Median Confidence", f"{stats['median_confidence']:.3f}")
            
            # Calculate quality metrics
            high_quality = len([m for m in self.current_matches if m.confidence_score >= 0.8])
            st.metric("High Quality Matches", f"{high_quality} ({high_quality/len(self.current_matches)*100:.1f}%)")
        
        # Confidence distribution chart
        st.subheader("📊 Confidence Distribution")
        
        conf_dist = stats['confidence_distribution']
        
        fig = go.Figure(data=[
            go.Bar(
                x=['High Confidence', 'Medium Confidence', 'Low Confidence'],
                y=[conf_dist['high'], conf_dist['medium'], conf_dist['low']],
                marker_color=['#2ecc71', '#f39c12', '#e74c3c']
            )
        ])
        
        fig.update_layout(
            title="Match Confidence Distribution",
            xaxis_title="Confidence Level",
            yaxis_title="Number of Matches"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Match type timeline
        if self.current_matches:
            st.subheader("⏰ Review Timeline")
            
            # Create timeline data
            timeline_data = []
            for match in self.current_matches:
                if match.reviewed_at:
                    timeline_data.append({
                        'time': match.reviewed_at,
                        'confidence': match.confidence_score,
                        'decision': match.user_decision or 'Pending',
                        'entity1': match.entity1_data.get('name', 'Unknown'),
                        'entity2': match.entity2_data.get('name', 'Unknown')
                    })
            
            if timeline_data:
                df_timeline = pd.DataFrame(timeline_data)
                
                fig = px.scatter(
                    df_timeline,
                    x='time',
                    y='confidence',
                    color='decision',
                    title="Review Timeline",
                    labels={
                        'time': 'Review Time',
                        'confidence': 'Confidence Score',
                        'decision': 'Decision'
                    },
                    hover_data=['entity1', 'entity2']
                )
                
                st.plotly_chart(fig, use_container_width=True)

# Create enhanced resolution UI instance
enhanced_resolution_ui = EnhancedResolutionUI()
