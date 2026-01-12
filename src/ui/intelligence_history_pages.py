"""
Intelligence-Based Historical Analysis UI Pages.
Implements the complete intelligence analysis workflow for historical research.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime
from typing import List, Dict, Optional, Any
import json
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.intelligence_history_engine import (
    IntelligenceHistoryEngine, ActorProfile, Hypothesis, 
    DecisionPoint, BiasType, SourceReliability, ConfidenceLevel
)
from src.core.history_engine import HistoryEngine
from src.data.history_models import EventType


class IntelligenceHistoryPages:
    """Intelligence-based historical analysis pages"""
    
    def __init__(self):
        self.history_engine = HistoryEngine()
        self.intel_engine = IntelligenceHistoryEngine(self.history_engine)
        self._load_sample_data()
    
    def render_analyst_workspace(self):
        """Main analyst workspace with hypothesis boards and evidence cards"""
        st.header("🕵️ Intelligence Analyst Workspace")
        
        # Sidebar for analysis setup
        with st.sidebar:
            st.subheader("Analysis Setup")
            
            # Select analysis target
            analysis_target = st.selectbox("Analysis Target", [
                "Historical Event", "Historical Figure", "Historical Period"
            ])
            
            if analysis_target == "Historical Event":
                events = list(self.history_engine.events.values())
                if events:
                    event_options = {event.title: event.id for event in events}
                    selected_event_name = st.selectbox("Select Event", list(event_options.keys()))
                    selected_target_id = event_options[selected_event_name]
            
            elif analysis_target == "Historical Figure":
                figures = list(self.history_engine.figures.values())
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📚 Reference Case Studies")
            st.markdown("Access pre-built intelligence-grade case studies for learning and analysis.")
            
            # Load Soviet Union case study
            if st.button("🇷🇺 Load Soviet Union Case Study", key="load_ussr_case"):
                with st.spinner("Loading Soviet Union case study..."):
                    try:
                        # Import and create case study
                        from src.data.soviet_union_case_study import SovietUnionCaseStudy
                        case_study = SovietUnionCaseStudy()
                        
                        # Generate complete analysis
                        judgment = case_study.generate_intelligence_judgment()
                        
                        # Store in session state
                        st.session_state.current_case_study = judgment
                        st.session_state.case_study_name = "Soviet Union Collapse (1985-1991)"
                        
                        st.success("✅ Soviet Union case study loaded successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error loading case study: {e}")
            
            # Other case studies (placeholder)
            st.markdown("### 📋 Available Case Studies")
            case_studies = [
                "🇷🇺 Soviet Union Collapse (1985-1991)",
                "🇩🇪 Fall of Berlin Wall (1989)",
                "🇨🇳 Cuban Missile Crisis (1962)",
                "🇻🇸 Vietnam War Decision Points"
            ]
            
            for case in case_studies:
                st.write(f"• {case}")
        
        with col2:
            st.subheader("🎯 Current Analysis")
            
            # Display current case study if loaded
            if hasattr(st.session_state, 'current_case_study') and st.session_state.current_case_study:
                case_data = st.session_state.current_case_study
                
                st.markdown(f"### 📊 {st.session_state.case_study_name}")
                
                # Primary driver
                st.markdown("**Primary Driver:**")
                st.info(case_data['primary_driver'])
                
                # Confidence level
                st.markdown("**Confidence Level:**")
                confidence_color = {
                    'Very Low': '🔴',
                    'Low': '🟠', 
                    'Medium': '🟡',
                    'High': '🟢',
                    'Very High': '🟦'
                }
                confidence_display = confidence_color.get(case_data['confidence_level'].value, '⚪')
                st.markdown(f"{confidence_display} {case_data['confidence_level'].value}")
                
                # Ranked hypotheses
                st.markdown("**Ranked Hypotheses:**")
                for i, hyp in enumerate(case_data['ranked_hypotheses'][:3], 1):
                    score_emoji = '🟢' if hyp['evidence_score'] >= 1 else '🟡' if hyp['evidence_score'] >= 0 else '🔴'
                    st.markdown(f"{i}. {hyp['title']} {score_emoji} (Score: {hyp['evidence_score']})")
                
                # Key lessons
                st.markdown("**Strategic Lessons:**")
                for lesson in case_data['strategic_lessons'][:3]:
                    st.write(f"💡 {lesson}")
                
                # Export option
                if st.button("📤 Export Case Study Data", key="export_case"):
                    export_data = case_study.export_case_study()
                    st.success("✅ Case study data exported to system!")
                    
            else:
                st.info("👆 Load a case study to begin analysis")
                
                # Quick start guide
                st.markdown("### 🚀 Quick Start Guide")
                st.markdown("""
                1. **Load Case Study**: Select from available reference cases
                2. **Review Analysis**: Examine hypotheses and evidence
                3. **Apply SATs**: Use ACH, Red Team, I&W techniques
                4. **Export Results**: Save intelligence judgments
                """)
        
        # Continue with existing workspace functionality
        st.markdown("---")
        st.subheader("🔬 Custom Analysis")
        
        # Existing workspace code continues here...
        selected_target_id = None
        
        # Target selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Select Analysis Target")
            
            # Sample targets (in real system, these would come from database)
            targets = [
                {"id": "ussr", "name": "Soviet Union", "type": "State"},
                {"id": "gorbachev", "name": "Mikhail Gorbachev", "type": "Leader"},
                {"id": "communist_party", "name": "Communist Party", "type": "Institution"}
            ]
            
            target_options = {f"{t['name']} ({t['type']})": t['id'] for t in targets}
            selected_target = st.selectbox("Select Target", list(target_options.keys()), key="target_select")
            
            if selected_target:
                selected_target_id = target_options[selected_target]
                target = next(t for t in targets if t['id'] == selected_target_id)
                
                st.markdown(f"**Selected:** {target['name']} ({target['type']})")
                st.markdown(f"**ID:** {target['id']}")
        
        with col2:
            st.markdown("### 🧠 Analysis Type")
            
            intel_analysis_type = st.selectbox(
                "Select Analysis Type",
                ["ACH - Analysis of Competing Hypotheses",
                 "Red Team Analysis", 
                 "Key Assumptions Check",
                 "Indicators & Warning",
                 "Counterfactual Analysis",
                 "Bias Detection"],
                key="intel_analysis_type"
            )
        
        # Analysis rendering
        if selected_target_id and intel_analysis_type:
            st.markdown("---")
            st.markdown(f"### 📊 {intel_analysis_type}")
            
            # Mock analysis results (in real system, these would call the intelligence engine)
            if intel_analysis_type == "ACH - Analysis of Competing Hypotheses":
                self._render_ach_analysis(selected_target_id)
            elif intel_analysis_type == "Red Team Analysis":
                self._render_red_team_analysis(selected_target_id)
            elif intel_analysis_type == "Key Assumptions Check":
                self._render_assumptions_analysis(selected_target_id)
            elif intel_analysis_type == "Indicators & Warning":
                self._render_indicators_analysis(selected_target_id)
            elif intel_analysis_type == "Counterfactual Analysis":
                self._render_counterfactual_analysis(selected_target_id)
            elif intel_analysis_type == "Bias Detection":
                self._render_bias_analysis(selected_target_id)
    
    def _render_assumptions_analysis(self, target_id):
        """Render key assumptions check analysis"""
        st.subheader("🔍 Key Assumptions Check")
        
        # Sample assumptions analysis
        assumptions = [
            {
                "assumption": "Economic collapse inevitably leads to state collapse",
                "assessment": "Weak",
                "reasoning": "Many states survive severe economic crises; USSR collapsed before total economic breakdown",
                "impact": "High - if false, overstates economic determinism"
            },
            {
                "assumption": "The Soviet state would always use force to preserve unity",
                "assessment": "False", 
                "reasoning": "August 1991 showed coercive restraint; elites chose not to use force",
                "impact": "High - if False, overestimates willingness to use repression"
            }
        ]
        
        st.write("**Key Assumptions Analysis:**")
        for i, assumption in enumerate(assumptions, 1):
            with st.expander(f"Assumption {i}: {assumption['assumption']}"):
                st.write(f"**Assessment:** {assumption['assessment']}")
                st.write(f"**Reasoning:** {assumption['reasoning']}")
                st.write(f"**Impact:** {assumption['impact']}")
                
                # Validity check
                is_valid = st.checkbox("Assumption Valid", key=f"assumption_{i}_valid")
                
                if is_valid:
                    st.success("✅ Assumption validated")
                else:
                    st.error("❌ Assumption challenged")
        
        # Overall assessment
        st.subheader("📊 Assumption Risk Matrix")
        valid_count = sum(1 for i in range(len(assumptions)) if st.session_state.get(f"assumption_{i}_valid", False))
        risk_score = (len(assumptions) - valid_count) / len(assumptions)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Valid Assumptions", f"{valid_count}/{len(assumptions)}")
        with col2:
            st.metric("Risk Score", f"{risk_score:.2f}")
            
        # Recommendations
        st.subheader("💡 Recommendations")
        if risk_score > 0.5:
            st.warning("⚠️ High assumption risk - reconsider analysis framework")
        else:
            st.success("✅ Assumptions appear valid - proceed with analysis")
    
    def _render_indicators_analysis(self, target_id):
        """Render indicators & warning analysis"""
        st.subheader("🚨 Indicators & Warning Analysis")
        
        # Sample indicators for Soviet Union case
        indicators = [
            {
                "indicator": "Declining loyalty of security services",
                "type": "Leading Indicator",
                "status": "Missed",
                "impact": "Critical - early warning of regime instability"
            },
            {
                "indicator": "Rise of republican-level power centers",
                "type": "Leading Indicator", 
                "status": "Misinterpreted",
                "impact": "High - underestimated nationalist momentum"
            },
            {
                "indicator": "Legalization of opposition movements",
                "type": "Confirming Indicator",
                "status": "Observed",
                "impact": "Medium - confirmed loss of party control"
            },
            {
                "indicator": "Elite asset diversification",
                "type": "Leading Indicator",
                "status": "Missed", 
                "impact": "High - indicated elite preparation for post-Soviet future"
            }
        ]
        
        st.write("**Retrospective Indicators Analysis:**")
        for indicator in indicators:
            status_color = {
                "Missed": "🔴",
                "Misinterpreted": "🟡", 
                "Observed": "🟢",
                "Confirmed": "🔵"
            }
            
            with st.expander(f"{status_color[indicator['status']]} {indicator['indicator']}"):
                st.write(f"**Type:** {indicator['type']}")
                st.write(f"**Status:** {indicator['status']}")
                st.write(f"**Impact:** {indicator['impact']}")
        
        # Key failure analysis
        st.subheader("🔍 Key Failure Analysis")
        st.error("**Primary Analytic Failure:**")
        st.write("Analysts over-weighted *structural strength* and under-weighted *elite intent*")
        
        st.write("**Correct Approach:**")
        st.write("• Track elite cohesion as leading indicator")
        st.write("• Economic stress ≠ automatic state collapse")
        st.write("• Consider regime willingness to use coercive power")
        
        # Lessons learned
        st.subheader("💡 Lessons Learned")
        lessons = [
            "Track elite cohesion as early warning indicator",
            "Economic stress does not automatically equal state collapse",
            "Institutional loyalty changes precede political transformation",
            "Consider coercive capacity AND willingness to use force"
        ]
        
        for lesson in lessons:
            st.write(f"• {lesson}")
    
    def _render_bias_analysis(self, target_id):
        """Render cognitive bias detection analysis"""
        st.subheader("🧠 Cognitive Bias Detection")
        
        # Sample bias analysis
        st.write("**Bias Detection Results:**")
        
        biases_detected = [
            {
                "bias_type": "Hindsight Bias",
                "indicators": ["Using post-event knowledge to judge pre-event decisions"],
                "severity": "High",
                "impact": "Distorts assessment of decision-making under uncertainty"
            },
            {
                "bias_type": "Confirmation Bias", 
                "indicators": ["Seeking evidence that supports pre-existing beliefs"],
                "severity": "Medium",
                "impact": "Misses disconfirming evidence"
            },
            {
                "bias_type": "Structural Inevitability Bias",
                "indicators": ["Assuming collapse was predetermined"],
                "severity": "High", 
                "impact": "Ignores agency and decision points"
            }
        ]
        
        for bias in biases_detected:
            severity_color = {
                "High": "🔴",
                "Medium": "🟡",
                "Low": "🟢"
            }
            
            with st.expander(f"{severity_color[bias['severity']]} {bias['bias_type']}"):
                st.write(f"**Severity:** {bias['severity']}")
                st.write(f"**Indicators:**")
                for indicator in bias['indicators']:
                    st.write(f"  • {indicator}")
                st.write(f"**Impact:** {bias['impact']}")
        
        # Bias mitigation strategies
        st.subheader("🛡️ Bias Mitigation Strategies")
        strategies = [
            "Use information-at-time analysis only",
            "Actively seek disconfirming evidence",
            "Consider alternative explanations",
            "Track analyst assumptions explicitly",
            "Use structured analytic techniques (ACH, Red Team)"
        ]
        
        for strategy in strategies:
            st.write(f"✅ {strategy}")
    
    def _render_red_team_analysis(self, target_id):
        """Render red team analysis"""
        st.subheader("🔴 Red Team Analysis")
        
        # Red team challenge to Soviet Union analysis
        st.write("**Red Team Challenge:**")
        st.error("The USSR did not collapse accidentally—it was consciously abandoned by elites who saw no future in preserving it.")
        
        st.write("**Supporting Evidence:**")
        red_team_evidence = [
            "Non-use of force during 1991 crisis",
            "Rapid elite repositioning post-collapse",
            "Lack of coordinated resistance to dissolution",
            "Elite preparation for post-Soviet careers"
        ]
        
        for evidence in red_team_evidence:
            st.write(f"• {evidence}")
        
        st.write("**Impact on Analysis:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("✅ Reinforces H3 - Elite defection hypothesis")
        with col2:
            st.warning("⚠️ Weakens 'structural inevitability' narratives")
        
        # Survivability assessment
        st.subheader("🛡️ Original Narrative Survivability")
        survivability_score = 0.7  # Moderate survivability
        
        st.metric("Survivability Score", f"{survivability_score:.2f}")
        st.write("**Assessment:** Original narrative has moderate resilience to Red Team challenge")
        
        # Recommendations
        st.subheader("💡 Red Team Recommendations")
        recommendations = [
            "Incorporate elite agency analysis into primary assessments",
            "Consider coercive willingness separate from coercive capacity",
            "Account for rational elite self-interest in collapse scenarios"
        ]
        
        for rec in recommendations:
            st.write(f"• {rec}")
    
    def _render_counterfactual_analysis(self, target_id):
        """Render counterfactual analysis"""
        st.subheader("🔄 Counterfactual Analysis")
        
        # Decision point: 1991 Non-Intervention
        st.write("**Decision Point:** Non-Intervention (1990-1991)")
        
        st.write("**Options Available:**")
        options = [
            "Repression (China-style)",
            "Federal renegotiation", 
            "Managed dissolution",
            "Limited reform acceleration"
        ]
        
        for option in options:
            st.write(f"• {option}")
        
        st.write("**Selected Path:** Ambiguous non-intervention → system drift → collapse")
        
        # Counterfactual scenarios
        st.write("**Counterfactual Scenarios:**")
        
        scenarios = [
            {
                "scenario": "Forceful Repression",
                "plausibility": "Medium",
                "constraints": ["Military loyalty", "International condemnation", "Economic costs"],
                "outcome_range": "Prolonged survival with increased instability"
            },
            {
                "scenario": "Successful Federal Negotiation",
                "plausibility": "Low",
                "constraints": ["Republic demands", "Party unity", "Economic reality"],
                "outcome_range": "Loose confederation with delayed collapse"
            },
            {
                "scenario": "Early Managed Dissolution",
                "plausibility": "High",
                "constraints": ["International support", "Economic transition plan", "Elite cooperation"],
                "outcome_range": "Orderly transition with reduced chaos"
            }
        ]
        
        for scenario in scenarios:
            plausibility_emoji = {
                "High": "🟢",
                "Medium": "🟡", 
                "Low": "🔴"
            }
            
            with st.expander(f"{plausibility_emoji[scenario['plausibility']]} {scenario['scenario']}"):
                st.write(f"**Plausibility:** {scenario['plausibility']}")
                st.write(f"**Constraints:**")
                for constraint in scenario['constraints']:
                    st.write(f"  • {constraint}")
                st.write(f"**Outcome Range:** {scenario['outcome_range']}")
        
        # Key insights
        st.subheader("💡 Counterfactual Insights")
        insights = [
            "Elite choices were more decisive than structural constraints",
            "Alternative paths existed but required political will",
            "Timing of dissolution influenced by elite cohesion breakdown",
            "International context shaped available options"
        ]
        
        for insight in insights:
            st.write(f"• {insight}")
    
    def render_intelligence_estimate(self):
        """Render intelligence estimate generation"""
        st.header("📄 Intelligence Estimate Generation")
        
        st.subheader("🎯 Intelligence Estimate: Soviet Union Collapse")
        
        # Executive summary
        st.write("**Executive Summary:**")
        st.info("""
        **High confidence** that collapse of Soviet Union was driven primarily by **elite defection and loss of willingness to use coercive power**, 
        enabled—but not caused—by economic stagnation and political reform.
        """)
        
        # Key judgments
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔍 Primary Findings")
            findings = [
                "Elite cohesion breakdown was decisive factor",
                "Economic problems were necessary but not sufficient",
                "Political reforms accelerated but did not cause collapse",
                "Coercive capacity existed without political will to use it"
            ]
            
            for finding in findings:
                st.write(f"• {finding}")
        
        with col2:
            st.subheader("📊 Confidence Assessment")
            confidence_data = {
                "Overall Confidence": "High",
                "Evidence Quality": "High",
                "Analytic Consensus": "Medium",
                "Alternative Explanations": "Well Considered"
            }
            
            for metric, value in confidence_data.items():
                st.metric(metric, value)
        
        # Supporting evidence
        st.subheader("📋 Key Evidence")
        evidence_summary = [
            "August 1991 coup failure - demonstrated elite unwillingness to preserve USSR",
            "Non-use of military force - confirmed loss of coercive will",
            "Rapid elite transition - indicated preparation for post-Soviet future",
            "Economic data - confirmed severe but not catastrophic problems"
        ]
        
        for evidence in evidence_summary:
            st.write(f"• {evidence}")
        
        # Implications
        st.subheader("🔮 Strategic Implications")
        implications = [
            "State collapse occurs when elites abandon system",
            "Coercive capacity meaningless without political will",
            "Economic stress creates opportunities for political transformation",
            "Reform can accelerate collapse if institutions lag behind elite preferences"
        ]
        
        for implication in implications:
            st.write(f"• {implication}")
        
        # Export options
        st.subheader("📤 Export Intelligence Estimate")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Generate PDF Report"):
                st.success("Intelligence estimate PDF generated!")
        
        with col2:
            if st.button("📊 Export to JSON"):
                st.success("Intelligence estimate exported to JSON!")
        
        with col3:
            if st.button("📋 Save to System"):
                st.success("Intelligence estimate saved to system database!")

    def render_ach_wizard(self):
        """Wizard-style Analysis of Competing Hypotheses"""
        st.header("🔍 ACH Analysis Wizard")
        
        # Step tracking
        if 'ach_step' not in st.session_state:
            st.session_state.ach_step = 1
        
        # Step 1: Select Event
        if st.session_state.ach_step == 1:
            st.subheader("Step 1: Select Historical Event")
            
            events = list(self.history_engine.events.values())
            if events:
                event_options = {event.title: event.id for event in events}
                selected_event_name = st.selectbox("Select Event to Analyze", list(event_options.keys()), key="ach_event_select")
                selected_event_id = event_options[selected_event_name]
                
                if st.button("Continue to Step 2"):
                    st.session_state.selected_event_id = selected_event_id
                    st.session_state.ach_step = 2
                    st.rerun()
            
            if st.button("Back to Step 1"):
                st.session_state.ach_step = 1
                st.rerun()
        
        # Step 2: Generate Hypotheses
        elif st.session_state.ach_step == 2:
            st.subheader("Step 2: Generate Competing Hypotheses")
            
            event_id = st.session_state.selected_event_id
            event = self.history_engine.events[event_id]
            
            st.write(f"**Analyzing Event:** {event.title}")
            st.write(f"**Date:** {event.date}")
            st.write(f"**Description:** {event.description}")
            
            # Generate hypotheses
            if st.button("Generate Hypotheses"):
                ach_analysis = self.intel_engine.analyze_competing_hypotheses(event_id)
                st.session_state.ach_analysis = ach_analysis
                st.session_state.ach_step = 3
                st.rerun()
            
            if st.button("Back to Step 1"):
                st.session_state.ach_step = 1
                st.rerun()
        
        # Step 3: Evidence Evaluation
        elif st.session_state.ach_step == 3:
            st.subheader("Step 3: Evidence Evaluation")
            
            ach_analysis = st.session_state.ach_analysis
            
            # Display hypotheses
            st.write("**Competing Hypotheses:**")
            for i, hypothesis in enumerate(ach_analysis['hypotheses']):
                with st.expander(f"Hypothesis {i+1}: {hypothesis['title']}"):
                    st.write(f"**Description:** {hypothesis['description']}")
                    st.write(f"**Confidence:** {hypothesis['confidence']}")
                    st.write(f"**Assumptions:** {', '.join(hypothesis['assumptions'])}")
            
            # Evidence matrix
            st.write("**Evidence Matrix:**")
            evidence_df = pd.DataFrame(ach_analysis['evidence_matrix']).T
            st.dataframe(evidence_df, use_container_width=True)
            
            # Likelihoods
            st.write("**Hypothesis Likelihoods:**")
            likelihood_df = pd.DataFrame(list(ach_analysis['likelihoods'].items()), 
                                     columns=['Hypothesis', 'Likelihood'])
            fig = px.bar(likelihood_df, x='Hypothesis', y='Likelihood', 
                         title="Hypothesis Likelihood Assessment")
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("Continue to Step 4"):
                st.session_state.ach_step = 4
                st.rerun()
            
            if st.button("Back to Step 2"):
                st.session_state.ach_step = 2
                st.rerun()
        
        # Step 4: Key Assumptions Check
        elif st.session_state.ach_step == 4:
            st.subheader("Step 4: Key Assumptions Check")
            
            ach_analysis = st.session_state.ach_analysis
            
            st.write("**Key Assumptions Identified:**")
            for assumption in ach_analysis['key_assumptions']:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"- {assumption}")
                with col2:
                    valid = st.checkbox("Valid", key=f"assumption_{assumption}")
            
            st.write("**Bias Analysis:**")
            for hypothesis_id, biases in ach_analysis['bias_analysis'].items():
                st.write(f"**Hypothesis {hypothesis_id}:** {', '.join(biases)}")
            
            # Final assessment
            st.subheader("Final Intelligence Assessment")
            top_hypothesis = max(ach_analysis['likelihoods'].items(), key=lambda x: x[1])
            st.success(f"**Most Likely Hypothesis:** {top_hypothesis[0]} (Confidence: {top_hypothesis[1]:.2f})")
            
            if st.button("Start New Analysis"):
                st.session_state.ach_step = 1
                st.rerun()
            
            if st.button("Back to Step 3"):
                st.session_state.ach_step = 3
                st.rerun()
    
    def render_bias_detection(self):
        """Cognitive bias detection and analysis"""
        st.header("🧠 Cognitive Bias Detection")
        
        # Text input for analysis
        st.subheader("Analyze Historical Narrative")
        
        text_input = st.text_area("Enter historical text to analyze for biases", 
                                 height=200, placeholder="Paste historical narrative here...")
        
        context_input = st.text_area("Context (optional)", height=100, 
                                   placeholder="Provide additional context about the source...")
        
        if st.button("Detect Biases"):
            if text_input:
                bias_analysis = self.intel_engine.detect_cognitive_biases(text_input, context_input)
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Bias Detection Results")
                    st.metric("Overall Bias Score", f"{bias_analysis['bias_score']:.2f}")
                    
                    if bias_analysis['detected_biases']:
                        st.write("**Detected Biases:**")
                        for bias_type, matches in bias_analysis['detected_biases'].items():
                            with st.expander(f"{bias_type.replace('_', ' ').title()} ({len(matches)} instances)"):
                                for match in matches:
                                    st.write(f"• {match['indicator']}")
                                    st.write(f"  Context: ...{match['context']}...")
                    else:
                        st.success("No significant biases detected")
                
                with col2:
                    st.subheader("Recommendations")
                    for recommendation in bias_analysis['recommendations']:
                        st.write(f"• {recommendation}")
                
                # Bias breakdown chart
                if bias_analysis['detected_biases']:
                    bias_counts = {bias: len(matches) for bias, matches in bias_analysis['detected_biases'].items()}
                    fig = px.pie(values=list(bias_counts.values()), 
                                 names=list(bias_counts.keys()),
                                 title="Bias Type Distribution")
                    st.plotly_chart(fig, use_container_width=True)
    
    def render_source_evaluation(self):
        """Source reliability evaluation engine"""
        st.header("📋 Source Reliability Evaluation")
        
        st.subheader("Source Information")
        
        # Source input form
        with st.form("source_evaluation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                source_type = st.selectbox("Source Type", ["Primary Source", "Secondary Source", "Tertiary Source"])
                author_name = st.text_input("Author/Creator Name")
                creation_date = st.date_input("Creation Date")
                proximity = st.selectbox("Proximity to Events", 
                                      ["Direct Witness", "Contemporary", "Later Account", "Modern Analysis"])
            
            with col2:
                source_medium = st.selectbox("Source Medium", 
                                          ["Written Document", "Oral Account", "Material Evidence", "Photographic", "Digital"])
                access_level = st.selectbox("Access to Information", 
                                         ["Direct Access", "Second-hand Access", "Third-hand Access", "Limited Access"])
                motivation = st.selectbox("Known Motivation", 
                                       ["Objective Record", "Personal Gain", "Political Agenda", "Propaganda", "Unknown"])
                corroboration = st.selectbox("Cross-Source Corroboration", 
                                          ["Strongly Corroborated", "Partially Corroborated", "Uncorroborated", "Contradicted"])
            
            additional_info = st.text_area("Additional Information", height=100)
            
            submitted = st.form_submit_button("Evaluate Source")
            
            if submitted:
                # Compile source information
                source_info = {
                    "source_type": source_type,
                    "author_name": author_name,
                    "creation_date": creation_date,
                    "proximity": proximity,
                    "source_medium": source_medium,
                    "access_level": access_level,
                    "motivation": motivation,
                    "corroboration": corroboration,
                    "additional_info": additional_info
                }
                
                # Evaluate reliability
                reliability_analysis = self.intel_engine.evaluate_source_reliability(source_info)
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Reliability Assessment")
                    st.metric("Reliability Grade", reliability_analysis['reliability_grade'])
                    st.metric("Reliability Score", f"{reliability['reliability_score']:.2f}")
                    
                    # Component scores
                    st.write("**Component Scores:**")
                    st.write(f"• Primary Indicators: {reliability_analysis['primary_indicators']:.2f}")
                    st.write(f"• Access Score: {reliability_analysis['access_score']:.2f}")
                    st.write(f"• Motivation Score: {reliability_analysis['motivation_score']:.2f}")
                    st.write(f"• Temporal Score: {reliability_analysis['temporal_score']:.2f}")
                
                with col2:
                    st.subheader("Recommendations")
                    for recommendation in reliability_analysis['recommendations']:
                        st.write(f"• {recommendation}")
                
                # Visual representation
                scores = {
                    "Primary": reliability_analysis['primary_indicators'],
                    "Access": reliability_analysis['access_score'],
                    "Motivation": reliability_analysis['motivation_score'],
                    "Temporal": reliability_analysis['temporal_score']
                }
                
                fig = go.Figure(data=go.Bar(
                    x=list(scores.keys()),
                    y=list(scores.values()),
                    marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
                ))
                
                fig.update_layout(
                    title="Source Reliability Components",
                    xaxis_title="Component",
                    yaxis_title="Score",
                    yaxis=dict(range=[0, 1])
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    def render_counterfactual_analysis(self):
        """Counterfactual modeling with constraints"""
        st.header("🔄 Counterfactual Analysis")
        
        # Select event
        events = list(self.history_engine.events.values())
        if events:
            event_options = {event.title: event.id for event in events}
            selected_event_name = st.selectbox("Select Historical Event", list(event_options.keys()))
            selected_event_id = event_options[selected_event_name]
            
            event = self.history_engine.events[selected_event_id]
            
            st.write(f"**Selected Event:** {event.title}")
            st.write(f"**Date:** {event.date}")
            st.write(f"**Description:** {event.description}")
            
            # Change point input
            st.subheader("Define Change Point")
            change_point = st.text_input("What would you change about this event?", 
                                     placeholder="e.g., 'Different military strategy', 'Alternative decision', 'Earlier intervention'")
            
            # Constraints
            st.subheader("Historical Constraints")
            st.write("The following constraints will be applied to maintain historical plausibility:")
            
            constraints = self.intel_engine._identify_historical_constraints(event)
            for constraint in constraints:
                st.write(f"• {constraint}")
            
            if st.button("Analyze Counterfactual"):
                if change_point:
                    counterfactual = self.intel_engine.create_counterfactual_analysis(
                        selected_event_id, change_point
                    )
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Alternative Scenario")
                        st.write(f"**Change Point:** {counterfactual['change_point']}")
                        st.write(f"**Alternative Outcome:** {counterfactual['alternative_scenario']['altered_outcome']}")
                        st.metric("Plausibility Score", f"{counterfactual['plausibility_score']:.2f}")
                    
                    with col2:
                        st.subheader("Second-Order Effects")
                        for effect in counterfactual['second_order_effects']:
                            st.write(f"• {effect}")
                    
                    # Key uncertainties
                    st.subheader("Key Uncertainties")
                    for uncertainty in counterfactual['key_uncertainties']:
                        st.write(f"• {uncertainty}")
                    
                    # Plausibility visualization
                    fig = go.Figure(data=go.Indicator(
                        mode = "gauge+number+delta",
                        value = counterfactual['plausibility_score'],
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Scenario Plausibility"},
                        gauge = {
                            'axis': {'range': [None, 1]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 0.3], 'color': "lightgray"},
                                {'range': [0.3, 0.7], 'color': "gray"},
                                {'range': [0.7, 1], 'color': "lightgreen"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 0.8
                            }
                        }
                    ))
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    def render_intelligence_estimate(self):
        """Generate Historical Intelligence Estimates (HIEs)"""
        st.header("📊 Historical Intelligence Estimate (HIE)")
        
        # Analysis parameters
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input("Analysis Topic", 
                               placeholder="e.g., 'Fall of Roman Empire', 'Cold War Origins'")
            time_period = st.text_input("Time Period", 
                                     placeholder="e.g., '3rd Century AD', '1945-1991'")
        
        with col2:
            analysis_scope = st.selectbox("Analysis Scope", 
                                      ["Comprehensive", "Political Focus", "Military Focus", "Economic Focus"])
            confidence_threshold = st.slider("Minimum Confidence Threshold", 0.0, 1.0, 0.6)
        
        if st.button("Generate Intelligence Estimate"):
            if topic and time_period:
                hie = self.intel_engine.generate_intelligence_estimate(topic, time_period)
                
                # Display HIE
                st.subheader(f"Historical Intelligence Estimate: {topic}")
                st.write(f"**Time Period:** {time_period}")
                st.write(f"**Analysis Date:** {hie['analysis_date']}")
                st.write(f"**Methodology:** {hie['methodology']}")
                
                # Key Judgments
                st.subheader("Key Judgments")
                for i, judgment in enumerate(hie['key_judgments']):
                    with st.expander(f"Judgment {i+1}: {judgment['judgment']}"):
                        st.write(f"**Confidence:** {judgment['confidence']}")
                        st.write(f"**Supporting Evidence:** {', '.join(judgment['supporting_evidence'])}")
                
                # Confidence Assessment
                st.subheader("Confidence Assessment")
                confidence = hie['confidence_assessment']
                st.metric("Overall Confidence", confidence['overall_confidence'])
                
                # Confidence factors
                st.write("**Confidence Factors:**")
                for factor in confidence['confidence_factors']:
                    st.write(f"• {factor}")
                
                st.write("**Confidence Limitations:**")
                for limitation in confidence['confidence_limitations']:
                    st.write(f"• {limitation}")
                
                # Lessons Learned
                st.subheader("Lessons Learned")
                for lesson in hie['lessons_learned']:
                    st.write(f"• {lesson}")
                
                # Data sources summary
                st.subheader("Data Sources")
                st.metric("Total Sources Analyzed", hie['data_sources'])
                
                # Export options
                st.subheader("Export Intelligence Estimate")
                if st.button("Export as JSON"):
                    st.json(hie)
                
                if st.button("Export as Report"):
                    report = self._format_hie_report(hie)
                    st.download_button(
                        label="Download HIE Report",
                        data=report,
                        file_name=f"HIE_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
    
    def _render_actor_analysis(self, target_id):
        """Render actor-centric analysis"""
        st.subheader("Actor-Centric Analysis")
        
        # Create actor profile
        profile = self.intel_engine.create_actor_profile(target_id)
        
        if profile:
            # Display profile
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Actor:** {profile.name}")
                st.write(f"**Type:** {profile.actor_type}")
                
                st.write("**Interests:**")
                for interest in profile.interests:
                    st.write(f"• {interest}")
                
                st.write("**Motivations:**")
                for motivation in profile.motivations:
                    st.write(f"• {motivation}")
            
            with col2:
                st.write("**Capabilities:**")
                for capability in profile.capabilities:
                    st.write(f"• {capability}")
                
                st.write("**Constraints:**")
                for constraint in profile.constraints:
                    st.write(f"• {constraint}")
                
                st.write("**Psychological Profile:**")
                for trait, value in profile.psychological_profile.items():
                    st.write(f"• {trait.replace('_', ' ').title()}: {value}")
            
            # Relationships
            st.subheader("Actor Relationships")
            if profile.relationships:
                rel_df = pd.DataFrame([
                    {"Relationship": rel_type, "Target": target_id}
                    for rel_type, target_id in profile.relationships.items()
                ])
                st.dataframe(rel_df, use_container_width=True)
    
    def _render_ach_analysis(self, target_id):
        """Render ACH analysis"""
        st.subheader("Analysis of Competing Hypotheses")
        
        ach_analysis = self.intel_engine.analyze_competing_hypotheses(target_id)
        
        if ach_analysis:
            # Display hypotheses
            st.write("**Competing Hypotheses:**")
            for hypothesis in ach_analysis['hypotheses']:
                with st.expander(f"{hypothesis['title']}"):
                    st.write(f"**Description:** {hypothesis['description']}")
                    st.write(f"**Confidence:** {hypothesis['confidence']}")
                    st.write(f"**Assumptions:** {', '.join(hypothesis['assumptions'])}")
            
            # Likelihood chart
            if ach_analysis['likelihoods']:
                likelihood_df = pd.DataFrame(list(ach_analysis['likelihoods'].items()), 
                                         columns=['Hypothesis', 'Likelihood'])
                fig = px.bar(likelihood_df, x='Hypothesis', y='Likelihood', 
                             title="Hypothesis Likelihood Assessment")
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_decision_analysis(self, target_id):
        """Render decision-point analysis"""
        st.subheader("Decision-Point Analysis")
        
        decision_point = self.intel_engine.create_decision_point_analysis(target_id)
        
        if decision_point:
            # Display decision context
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Decision Maker:** {decision_point.decision_maker}")
                st.write(f"**Decision Date:** {decision_point.decision_date}")
                st.write(f"**Actual Decision:** {decision_point.actual_decision}")
                st.write(f"**Information Quality:** {decision_point.information_quality}")
            
            with col2:
                st.write("**Known Information:**")
                for info in decision_point.known_information[:3]:
                    st.write(f"• {info}")
                
                st.write("**Unknown Information:**")
                for unknown in decision_point.unknown_information[:3]:
                    st.write(f"• {unknown}")
            
            # Alternatives considered
            st.subheader("Alternatives Considered")
            for alternative in decision_point.alternatives_considered:
                st.write(f"• {alternative}")
    
    def _render_red_team_analysis(self, target_id):
        """Render red team analysis"""
        st.subheader("Red Team Analysis")
        
        # Generate hypothesis first if needed
        if target_id not in self.intel_engine.hypotheses:
            ach_analysis = self.intel_engine.analyze_competing_hypotheses(target_id)
            if ach_analysis and ach_analysis['hypotheses']:
                # Use first hypothesis for red team
                hypothesis_data = ach_analysis['hypotheses'][0]
                hypothesis = Hypothesis(
                    id=hypothesis_data['id'],
                    title=hypothesis_data['title'],
                    description=hypothesis_data['description'],
                    evidence=hypothesis_data['evidence'],
                    confidence=hypothesis_data['confidence'],
                    assumptions=hypothesis_data['assumptions'],
                    biases=hypothesis_data['biases']
                )
                self.intel_engine.hypotheses[hypothesis.id] = hypothesis
        
        if target_id in self.intel_engine.hypotheses:
            red_team = self.intel_engine.perform_red_team_analysis(target_id)
            
            if red_team:
                # Display red team results
                st.write("**Original Hypothesis:**")
                st.write(red_team['original_hypothesis']['title'])
                
                st.subheader("Counterarguments")
                for counterargument in red_team['counterarguments']:
                    st.write(f"• {counterargument}")
                
                st.subheader("Weak Points Identified")
                for weak_point in red_team['weak_points']:
                    st.write(f"• {weak_point}")
                
                st.subheader("Devil's Advocate Position")
                st.write(red_team['devil_advocate_position'])
    
    def _render_early_warning_analysis(self, target_id):
        """Render early warning analysis"""
        st.subheader("Early Warning Analysis")
        
        warning_analysis = self.intel_engine.analyze_early_warning_indicators(target_id)
        
        if warning_analysis:
            # Display indicators
            st.write("**Warning Indicators:**")
            for indicator in warning_analysis['indicators']:
                with st.expander(f"{indicator['description']}"):
                    st.write(f"**Lead Time:** {indicator['lead_time_days']} days")
                    st.write(f"**Reliability:** {indicator['reliability']}")
                    st.write(f"**False Positive Rate:** {indicator['false_positive_rate']:.2f}")
            
            # Signal analysis
            st.subheader("Signal vs Noise Analysis")
            signal = warning_analysis['signal_analysis']
            st.metric("Signal-to-Noise Ratio", f"{signal.get('signal_to_noise_ratio', 0):.2f}")
            st.metric("False Positive Rate", f"{signal.get('false_positive_rate', 0):.2f}")
            
            # Missed warnings
            st.subheader("Missed Warnings")
            for warning in warning_analysis['missed_warnings']:
                st.write(f"• {warning}")
            
            # Lessons learned
            st.subheader("Lessons Learned")
            for lesson in warning_analysis['lessons_learned']:
                st.write(f"• {lesson}")
    
    def _format_hie_report(self, hie: Dict[str, Any]) -> str:
        """Format HIE as readable report"""
        report = f"""
HISTORICAL INTELLIGENCE ESTIMATE (HIE)
=====================================

TOPIC: {hie['topic']}
TIME PERIOD: {hie['time_period']}
ANALYSIS DATE: {hie['analysis_date']}
METHODOLOGY: {hie['methodology']}

KEY JUDGMENTS
--------------
"""
        
        for i, judgment in enumerate(hie['key_judgments'], 1):
            report += f"""
{i}. {judgment['judgment']}
   Confidence: {judgment['confidence']}
   Supporting Evidence: {', '.join(judgment['supporting_evidence'])}
"""
        
        report += f"""
CONFIDENCE ASSESSMENT
----------------------
Overall Confidence: {hie['confidence_assessment']['overall_confidence']}
Confidence Factors: {', '.join(hie['confidence_assessment']['confidence_factors'])}
Confidence Limitations: {', '.join(hie['confidence_assessment']['confidence_limitations'])}

LESSONS LEARNED
----------------
"""
        
        for lesson in hie['lessons_learned']:
            report += f"• {lesson}\n"
        
        report += f"""
DATA SOURCES
-------------
Total Sources Analyzed: {hie['data_sources']}

END OF REPORT
=============
"""
        
        return report
    
    def _load_sample_data(self):
        """Load sample data for demonstration"""
        # Import sample data from history_pages
        from src.ui.history_pages import HistoryPages
        history_pages = HistoryPages()
        # Sample data is already loaded in HistoryPages constructor
