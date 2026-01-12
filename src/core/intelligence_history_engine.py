"""
Intelligence-Based Historical Analysis Engine.
Implements intelligence community methodologies for historical research.
"""

from datetime import date, datetime
from typing import List, Dict, Optional, Tuple, Any, Set
from enum import Enum
import json
from dataclasses import dataclass
import re
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.history_engine import HistoryEngine
from src.data.history_models import (
    HistoricalEvent, HistoricalFigure, HistoricalOrganization,
    HistoricalPeriod, EventType
)


class BiasType(str, Enum):
    """Types of cognitive biases in historical analysis"""
    CONFIRMATION_BIAS = "confirmation_bias"
    MIRROR_IMAGING = "mirror_imaging"
    GROUPTHINK = "groupthink"
    HINDSIGHT_BIAS = "hindsight_bias"
    ANCHORING_BIAS = "anchoring_bias"
    AVAILABILITY_BIAS = "availability_bias"
    NARRATIVE_BIAS = "narrative_bias"


class SourceReliability(str, Enum):
    """Source reliability grades (Admiralty Code style)"""
    A1 = "A1"  # Confirmed reliable
    A2 = "A2"  # Usually reliable
    B1 = "B1"  # Fairly reliable
    B2 = "B2"  # Not always reliable
    C1 = "C1"  # Unreliable
    C2 = "C2"  # Reliability cannot be judged
    D = "D"    # Insufficient info


class ConfidenceLevel(str, Enum):
    """Intelligence confidence levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


@dataclass
class Hypothesis:
    """Intelligence hypothesis for historical analysis"""
    id: str
    title: str
    description: str
    evidence: List[str]
    confidence: ConfidenceLevel
    assumptions: List[str]
    biases: List[BiasType]
    competing_hypotheses: List[str] = None


@dataclass
class ActorProfile:
    """Intelligence-style actor profile"""
    actor_id: str
    name: str
    actor_type: str  # state, leader, faction, institution
    interests: List[str]
    motivations: List[str]
    capabilities: List[str]
    constraints: List[str]
    psychological_profile: Dict[str, Any]
    relationships: Dict[str, str]  # relationship_type: actor_id


@dataclass
class DecisionPoint:
    """Historical decision point with information context"""
    event_id: str
    decision_maker: str
    decision_date: date
    known_information: List[str]
    unknown_information: List[str]
    alternatives_considered: List[str]
    actual_decision: str
    outcome: str
    information_quality: SourceReliability


@dataclass
class IntelligenceIndicator:
    """Early warning indicator for historical events"""
    indicator_id: str
    description: str
    event_type: str
    lead_time_days: int
    reliability: SourceReliability
    false_positive_rate: float
    historical_occurrences: List[str]


class IntelligenceHistoryEngine:
    """Core engine for intelligence-based historical analysis"""
    
    def __init__(self, history_engine: HistoryEngine):
        self.engine = history_engine
        self.hypotheses = {}
        self.actor_profiles = {}
        self.decision_points = {}
        self.indicators = {}
        self.bias_patterns = {}
        
    def create_actor_profile(self, actor_id: str, actor_type: str = "figure") -> ActorProfile:
        """Create intelligence-style actor profile"""
        if actor_id in self.engine.figures:
            figure = self.engine.figures[actor_id]
            
            # Analyze interests and motivations from available data
            interests = self._extract_interests(figure)
            motivations = self._extract_motivations(figure)
            capabilities = self._extract_capabilities(figure)
            constraints = self._extract_constraints(figure)
            
            # Psychological profile based on actions and writings
            psych_profile = self._analyze_psychology(figure)
            
            # Map relationships
            relationships = self._map_actor_relationships(figure)
            
            profile = ActorProfile(
                actor_id=actor_id,
                name=figure.name,
                actor_type=actor_type,
                interests=interests,
                motivations=motivations,
                capabilities=capabilities,
                constraints=constraints,
                psychological_profile=psych_profile,
                relationships=relationships
            )
            
            self.actor_profiles[actor_id] = profile
            return profile
        
        return None
    
    def analyze_competing_hypotheses(self, event_id: str) -> Dict[str, Any]:
        """Analysis of Competing Hypotheses (ACH) for historical events"""
        if event_id not in self.engine.events:
            return {}
        
        event = self.engine.events[event_id]
        
        # Generate competing hypotheses
        hypotheses = self._generate_hypotheses(event)
        
        # Evaluate evidence for each hypothesis
        evidence_matrix = self._build_evidence_matrix(hypotheses, event)
        
        # Identify diagnostic evidence
        diagnostic_evidence = self._find_diagnostic_evidence(evidence_matrix)
        
        # Apply bias detection
        bias_analysis = self._detect_hypothesis_biases(hypotheses)
        
        # Calculate likelihoods
        likelihoods = self._calculate_hypothesis_likelihoods(evidence_matrix, diagnostic_evidence)
        
        return {
            "event": event.dict(),
            "hypotheses": [h.__dict__ for h in hypotheses],
            "evidence_matrix": evidence_matrix,
            "diagnostic_evidence": diagnostic_evidence,
            "bias_analysis": bias_analysis,
            "likelihoods": likelihoods,
            "key_assumptions": self._extract_key_assumptions(hypotheses)
        }
    
    def create_decision_point_analysis(self, event_id: str) -> DecisionPoint:
        """Analyze historical decision point with information context"""
        if event_id not in self.engine.events:
            return None
        
        event = self.engine.events[event_id]
        
        # Determine decision maker
        decision_maker = self._identify_decision_maker(event)
        
        # Reconstruct known vs unknown information
        known_info, unknown_info = self._reconstruct_information_context(event)
        
        # Identify alternatives considered
        alternatives = self._identify_alternatives(event)
        
        # Assess information quality
        info_quality = self._assess_information_reliability(event)
        
        decision_point = DecisionPoint(
            event_id=event_id,
            decision_maker=decision_maker,
            decision_date=event.date,
            known_information=known_info,
            unknown_information=unknown_info,
            alternatives_considered=alternatives,
            actual_decision=event.title,
            outcome=event.description,
            information_quality=info_quality
        )
        
        self.decision_points[event_id] = decision_point
        return decision_point
    
    def perform_red_team_analysis(self, hypothesis_id: str) -> Dict[str, Any]:
        """Red Team analysis - challenge assumptions and arguments"""
        if hypothesis_id not in self.hypotheses:
            return {}
        
        hypothesis = self.hypotheses[hypothesis_id]
        
        # Generate counterarguments
        counterarguments = self._generate_counterarguments(hypothesis)
        
        # Identify weak points
        weak_points = self._identify_weak_points(hypothesis)
        
        # Stress test assumptions
        stress_test = self._stress_test_assumptions(hypothesis.assumptions)
        
        # Devil's advocate position
        devil_advocate = self._create_devil_advocate_position(hypothesis)
        
        return {
            "original_hypothesis": hypothesis.__dict__,
            "counterarguments": counterarguments,
            "weak_points": weak_points,
            "assumption_stress_test": stress_test,
            "devil_advocate_position": devil_advocate,
            "recommendations": self._generate_red_team_recommendations(hypothesis)
        }
    
    def analyze_early_warning_indicators(self, period_id: str) -> Dict[str, Any]:
        """Retrospective early warning analysis"""
        if period_id not in self.engine.periods:
            return {}
        
        period = self.engine.periods[period_id]
        events = self.engine.find_events_by_period(period_id)
        
        # Identify potential warning indicators
        indicators = self._identify_warning_indicators(events)
        
        # Analyze signal vs noise
        signal_analysis = self._analyze_signal_noise(events, indicators)
        
        # Find missed warnings
        missed_warnings = self._identify_missed_warnings(events, indicators)
        
        # Calculate warning effectiveness
        warning_effectiveness = self._calculate_warning_effectiveness(events, indicators)
        
        return {
            "period": period.dict(),
            "indicators": [ind.__dict__ for ind in indicators],
            "signal_analysis": signal_analysis,
            "missed_warnings": missed_warnings,
            "warning_effectiveness": warning_effectiveness,
            "lessons_learned": self._extract_warning_lessons(missed_warnings)
        }
    
    def detect_cognitive_biases(self, text: str, context: str = "") -> Dict[str, Any]:
        """Detect cognitive biases in historical narratives"""
        bias_indicators = {
            BiasType.CONFIRMATION_BIAS: [
                "clearly", "obviously", "undoubtedly", "of course",
                "it's clear that", "as expected", "not surprisingly"
            ],
            BiasType.MIRROR_IMAGING: [
                "any reasonable person", "logically", "rationally",
                "of course they would", "it makes sense that"
            ],
            BiasType.HINDSIGHT_BIAS: [
                "should have", "could have predicted", "obvious in retrospect",
                "it was inevitable", "they should have known"
            ],
            BiasType.GROUPTHINK: [
                "everyone agreed", "consensus was", "unanimous",
                "no one questioned", "the group decided"
            ]
        }
        
        detected_biases = {}
        text_lower = text.lower()
        
        for bias_type, indicators in bias_indicators.items():
            matches = []
            for indicator in indicators:
                if indicator in text_lower:
                    # Find context around the indicator
                    start = max(0, text_lower.find(indicator) - 50)
                    end = min(len(text), text_lower.find(indicator) + len(indicator) + 50)
                    context_snippet = text[start:end]
                    matches.append({
                        "indicator": indicator,
                        "context": context_snippet
                    })
            
            if matches:
                detected_biases[bias_type.value] = matches
        
        # Calculate bias score
        bias_score = len(detected_biases) / len(bias_indicators)
        
        return {
            "detected_biases": detected_biases,
            "bias_score": bias_score,
            "recommendations": self._generate_bias_recommendations(detected_biases)
        }
    
    def evaluate_source_reliability(self, source_info: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate source reliability using intelligence tradecraft"""
        # Primary vs secondary assessment
        primary_indicators = self._assess_primary_source_indicators(source_info)
        
        # Access and proximity assessment
        access_score = self._assess_source_access(source_info)
        
        # Motivation and bias assessment
        motivation_score = self._assess_source_motivation(source_info)
        
        # Temporal distance assessment
        temporal_score = self._assess_temporal_distance(source_info)
        
        # Calculate overall reliability
        reliability_score = (primary_indicators + access_score + motivation_score + temporal_score) / 4
        
        # Assign reliability grade
        if reliability_score >= 0.9:
            reliability = SourceReliability.A1
        elif reliability_score >= 0.8:
            reliability = SourceReliability.A2
        elif reliability_score >= 0.7:
            reliability = SourceReliability.B1
        elif reliability_score >= 0.6:
            reliability = SourceReliability.B2
        elif reliability_score >= 0.5:
            reliability = SourceReliability.C1
        else:
            reliability = SourceReliability.C2
        
        return {
            "reliability_grade": reliability,
            "reliability_score": reliability_score,
            "primary_indicators": primary_indicators,
            "access_score": access_score,
            "motivation_score": motivation_score,
            "temporal_score": temporal_score,
            "recommendations": self._generate_source_recommendations(reliability)
        }
    
    def create_counterfactual_analysis(self, event_id: str, change_point: str) -> Dict[str, Any]:
        """Create constrained counterfactual analysis"""
        if event_id not in self.engine.events:
            return {}
        
        event = self.engine.events[event_id]
        
        # Identify key constraints
        constraints = self._identify_historical_constraints(event)
        
        # Model alternative scenario
        alternative_scenario = self._model_alternative_scenario(event, change_point, constraints)
        
        # Assess plausibility
        plausibility_score = self._assess_scenario_plausibility(alternative_scenario, constraints)
        
        # Identify second-order effects
        second_order_effects = self._model_second_order_effects(alternative_scenario)
        
        return {
            "original_event": event.dict(),
            "change_point": change_point,
            "constraints": constraints,
            "alternative_scenario": alternative_scenario,
            "plausibility_score": plausibility_score,
            "second_order_effects": second_order_effects,
            "key_uncertainties": self._identify_scenario_uncertainties(alternative_scenario)
        }
    
    def generate_intelligence_estimate(self, topic: str, time_period: str) -> Dict[str, Any]:
        """Generate Historical Intelligence Estimate (HIE)"""
        # Gather relevant data
        relevant_events = self._get_relevant_events(topic, time_period)
        relevant_figures = self._get_relevant_figures(topic, time_period)
        
        # Apply structured analysis
        ach_analysis = self._apply_ach_to_topic(relevant_events)
        bias_analysis = self._analyze_topic_biases(relevant_events)
        
        # Generate key judgments
        key_judgments = self._generate_key_judgments(ach_analysis, bias_analysis)
        
        # Assess confidence levels
        confidence_assessment = self._assess_judgment_confidence(key_judgments)
        
        # Extract lessons learned
        lessons_learned = self._extract_topic_lessons(relevant_events, relevant_figures)
        
        return {
            "topic": topic,
            "time_period": time_period,
            "key_judgments": key_judgments,
            "confidence_assessment": confidence_assessment,
            "lessons_learned": lessons_learned,
            "methodology": "Intelligence-Based Historical Analysis",
            "data_sources": len(relevant_events) + len(relevant_figures),
            "analysis_date": datetime.now().isoformat()
        }
    
    # Private helper methods
    def _extract_interests(self, figure) -> List[str]:
        """Extract actor interests from historical data"""
        interests = []
        
        # From occupation
        if figure.occupation:
            for occ in figure.occupation:
                if "military" in occ.lower():
                    interests.append("military_power")
                if "political" in occ.lower():
                    interests.append("political_power")
                if "religious" in occ.lower():
                    interests.append("religious_influence")
        
        # From achievements
        if figure.achievements:
            for achievement in figure.achievements:
                if "conquest" in achievement.lower():
                    interests.append("territorial_expansion")
                if "reform" in achievement.lower():
                    interests.append("institutional_change")
        
        return interests
    
    def _extract_motivations(self, figure) -> List[str]:
        """Extract actor motivations from historical data"""
        motivations = []
        
        # Basic motivations based on era and role
        if "military" in str(figure.occupation).lower():
            motivations.extend(["glory", "power", "wealth"])
        if "political" in str(figure.occupation).lower():
            motivations.extend(["power", "legacy", "control"])
        
        return motivations
    
    def _extract_capabilities(self, figure) -> List[str]:
        """Extract actor capabilities from historical data"""
        capabilities = []
        
        if figure.achievements:
            for achievement in figure.achievements:
                if "conquest" in achievement.lower():
                    capabilities.append("military_command")
                if "reform" in achievement.lower():
                    capabilities.append("political_leadership")
        
        return capabilities
    
    def _extract_constraints(self, figure) -> List[str]:
        """Extract actor constraints from historical data"""
        constraints = []
        
        # Time period constraints
        if figure.era:
            constraints.append(f"technological_limitations_{figure.era}")
        
        # Geographic constraints
        if figure.birth_place:
            constraints.append(f"geographic_scope_{figure.birth_place}")
        
        return constraints
    
    def _analyze_psychology(self, figure) -> Dict[str, Any]:
        """Analyze psychological profile from historical actions"""
        profile = {
            "risk_tolerance": "medium",  # Default
            "decision_style": "deliberate",
            "leadership_style": "authoritative"
        }
        
        # Analyze from achievements
        if figure.achievements:
            if any("conquest" in a.lower() for a in figure.achievements):
                profile["risk_tolerance"] = "high"
            if any("reform" in a.lower() for a in figure.achievements):
                profile["decision_style"] = "innovative"
        
        return profile
    
    def _map_actor_relationships(self, figure) -> Dict[str, str]:
        """Map actor relationships from historical data"""
        relationships = {}
        
        # From figure relationships
        if hasattr(figure, 'relationships') and figure.relationships:
            relationships.update(figure.relationships)
        
        # From event participation
        for event in self.engine.events.values():
            if figure.id in event.participants:
                for other_participant in event.participants:
                    if other_participant != figure.id and other_participant in self.engine.figures:
                        other_figure = self.engine.figures[other_participant]
                        relationships[f"collaborated_with_{other_figure.name}"] = other_participant
        
        return relationships
    
    def _generate_hypotheses(self, event) -> List[Hypothesis]:
        """Generate competing hypotheses for historical events"""
        hypotheses = []
        
        # Primary hypothesis (most common explanation)
        primary_hypothesis = Hypothesis(
            id=f"{event.id}_primary",
            title=f"Primary Explanation: {event.title}",
            description=f"Standard historical interpretation of {event.title}",
            evidence=[event.description],
            confidence=ConfidenceLevel.MEDIUM,
            assumptions=["Standard historical narrative is accurate"],
            biases=[BiasType.CONFIRMATION_BIAS]
        )
        hypotheses.append(primary_hypothesis)
        
        # Alternative hypotheses based on event type
        if event.event_type == EventType.POLITICAL:
            # Economic motivation hypothesis
            economic_hypothesis = Hypothesis(
                id=f"{event.id}_economic",
                title=f"Economic Motivation: {event.title}",
                description=f"Event driven primarily by economic factors",
                evidence=[event.description],
                confidence=ConfidenceLevel.LOW,
                assumptions=["Economic factors are primary drivers"],
                biases=[BiasType.MIRROR_IMAGING]
            )
            hypotheses.append(economic_hypothesis)
            
            # Social pressure hypothesis
            social_hypothesis = Hypothesis(
                id=f"{event.id}_social",
                title=f"Social Pressure: {event.title}",
                description=f"Event driven by popular pressure or social forces",
                evidence=[event.description],
                confidence=ConfidenceLevel.LOW,
                assumptions=["Social forces can drive political events"],
                biases=[BiasType.GROUPTHINK]
            )
            hypotheses.append(social_hypothesis)
        
        return hypotheses
    
    def _build_evidence_matrix(self, hypotheses: List[Hypothesis], event) -> Dict[str, Any]:
        """Build evidence matrix for ACH analysis"""
        matrix = {}
        
        for hypothesis in hypotheses:
            matrix[hypothesis.id] = {
                "title": hypothesis.title,
                "evidence_consistency": 0.7,  # Simplified
                "completeness": 0.6,
                "reliability": 0.8
            }
        
        return matrix
    
    def _find_diagnostic_evidence(self, evidence_matrix: Dict[str, Any]) -> List[str]:
        """Find evidence that distinguishes between hypotheses"""
        return ["Event timing", "Participant motivations", "Geographic factors"]
    
    def _detect_hypothesis_biases(self, hypotheses: List[Hypothesis]) -> Dict[str, List[BiasType]]:
        """Detect biases in competing hypotheses"""
        bias_analysis = {}
        
        for hypothesis in hypotheses:
            bias_analysis[hypothesis.id] = hypothesis.biases
        
        return bias_analysis
    
    def _calculate_hypothesis_likelihoods(self, evidence_matrix: Dict[str, Any], 
                                     diagnostic_evidence: List[str]) -> Dict[str, float]:
        """Calculate likelihoods for competing hypotheses"""
        likelihoods = {}
        
        for hypothesis_id, evidence in evidence_matrix.items():
            # Simplified likelihood calculation
            consistency = evidence["evidence_consistency"]
            completeness = evidence["completeness"]
            reliability = evidence["reliability"]
            
            likelihood = (consistency + completeness + reliability) / 3
            likelihoods[hypothesis_id] = likelihood
        
        return likelihoods
    
    def _extract_key_assumptions(self, hypotheses: List[Hypothesis]) -> List[str]:
        """Extract key assumptions across all hypotheses"""
        all_assumptions = []
        for hypothesis in hypotheses:
            all_assumptions.extend(hypothesis.assumptions)
        
        # Remove duplicates
        return list(set(all_assumptions))
    
    def _identify_decision_maker(self, event) -> str:
        """Identify primary decision maker for event"""
        if event.participants:
            # Return first participant (simplified)
            first_participant = event.participants[0]
            if first_participant in self.engine.figures:
                return self.engine.figures[first_participant].name
        
        return "Unknown"
    
    def _reconstruct_information_context(self, event) -> Tuple[List[str], List[str]]:
        """Reconstruct what was known vs unknown at decision time"""
        known_info = [
            f"Event location: {event.location}",
            f"Event date: {event.date}",
            f"Participants: {len(event.participants)}"
        ]
        
        unknown_info = [
            "Future outcomes",
            "Long-term consequences",
            "Opponent capabilities and intentions"
        ]
        
        return known_info, unknown_info
    
    def _identify_alternatives(self, event) -> List[str]:
        """Identify alternatives that were considered"""
        alternatives = [
            "Maintain status quo",
            "Seek diplomatic solution",
            "Use military force",
            "Apply economic pressure"
        ]
        
        return alternatives[:3]  # Return first 3
    
    def _assess_information_reliability(self, event) -> SourceReliability:
        """Assess reliability of available information"""
        # Simplified assessment based on event completeness
        if event.description and len(event.description) > 100:
            return SourceReliability.B1
        else:
            return SourceReliability.C1
    
    def _generate_counterarguments(self, hypothesis: Hypothesis) -> List[str]:
        """Generate counterarguments to hypothesis"""
        counterarguments = [
            f"Alternative explanation for {hypothesis.title}",
            f"Insufficient evidence for {hypothesis.title}",
            f"Counterexamples to {hypothesis.title}"
        ]
        
        return counterarguments
    
    def _identify_weak_points(self, hypothesis: Hypothesis) -> List[str]:
        """Identify weak points in hypothesis"""
        weak_points = []
        
        if hypothesis.confidence in [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW]:
            weak_points.append("Low confidence level")
        
        if len(hypothesis.evidence) < 2:
            weak_points.append("Limited supporting evidence")
        
        if len(hypothesis.assumptions) > 3:
            weak_points.append("Too many assumptions")
        
        return weak_points
    
    def _stress_test_assumptions(self, assumptions: List[str]) -> Dict[str, bool]:
        """Stress test key assumptions"""
        stress_results = {}
        
        for assumption in assumptions:
            # Simplified stress test
            if "standard" in assumption.lower():
                stress_results[assumption] = False  # Weak assumption
            else:
                stress_results[assumption] = True  # Holds up
        
        return stress_results
    
    def _create_devil_advocate_position(self, hypothesis: Hypothesis) -> str:
        """Create devil's advocate position"""
        return f"Opposite of {hypothesis.title}: The conventional explanation is fundamentally flawed and ignores key factors."
    
    def _generate_red_team_recommendations(self, hypothesis: Hypothesis) -> List[str]:
        """Generate Red Team recommendations"""
        return [
            "Seek disconfirming evidence",
            "Consider alternative explanations",
            "Challenge key assumptions",
            "Assess cognitive biases"
        ]
    
    def _identify_warning_indicators(self, events: List[HistoricalEvent]) -> List[IntelligenceIndicator]:
        """Identify potential early warning indicators"""
        indicators = []
        
        # Look for patterns in events
        military_events = [e for e in events if e.event_type == EventType.MILITARY]
        political_events = [e for e in events if e.event_type == EventType.POLITICAL]
        
        if military_events:
            indicator = IntelligenceIndicator(
                indicator_id="military_buildup",
                description="Increased military activity",
                event_type="military_conflict",
                lead_time_days=30,
                reliability=SourceReliability.B1,
                false_positive_rate=0.3,
                historical_occurrences=[e.id for e in military_events]
            )
            indicators.append(indicator)
        
        return indicators
    
    def _analyze_signal_noise(self, events: List[HistoricalEvent], 
                           indicators: List[IntelligenceIndicator]) -> Dict[str, Any]:
        """Analyze signal vs noise in warning indicators"""
        return {
            "total_events": len(events),
            "indicator_count": len(indicators),
            "signal_to_noise_ratio": 0.7,  # Simplified
            "false_positive_rate": 0.3
        }
    
    def _identify_missed_warnings(self, events: List[HistoricalEvent], 
                             indicators: List[IntelligenceIndicator]) -> List[str]:
        """Identify missed warning opportunities"""
        return ["Political instability indicators", "Economic distress signals"]
    
    def _calculate_warning_effectiveness(self, events: List[HistoricalEvent], 
                                   indicators: List[IntelligenceIndicator]) -> float:
        """Calculate warning system effectiveness"""
        return 0.6  # Simplified score
    
    def _extract_warning_lessons(self, missed_warnings: List[str]) -> List[str]:
        """Extract lessons from missed warnings"""
        return [
            "Pay attention to early indicators",
            "Avoid confirmation bias in threat assessment",
            "Consider multiple warning sources"
        ]
    
    def _generate_bias_recommendations(self, detected_biases: Dict[str, Any]) -> List[str]:
        """Generate recommendations for addressing detected biases"""
        recommendations = []
        
        if BiasType.CONFIRMATION_BIAS.value in detected_biases:
            recommendations.append("Actively seek disconfirming evidence")
        
        if BiasType.HINDSIGHT_BIAS.value in detected_biases:
            recommendations.append("Focus on information available at the time")
        
        if BiasType.GROUPTHINK.value in detected_biases:
            recommendations.append("Encourage diverse perspectives")
        
        return recommendations
    
    def _assess_primary_source_indicators(self, source_info: Dict[str, Any]) -> float:
        """Assess primary source indicators"""
        return 0.7  # Simplified
    
    def _assess_source_access(self, source_info: Dict[str, Any]) -> float:
        """Assess source access to information"""
        return 0.6  # Simplified
    
    def _assess_source_motivation(self, source_info: Dict[str, Any]) -> float:
        """Assess source motivation and potential bias"""
        return 0.7  # Simplified
    
    def _assess_temporal_distance(self, source_info: Dict[str, Any]) -> float:
        """Assess temporal distance from events"""
        return 0.8  # Simplified
    
    def _generate_source_recommendations(self, reliability: SourceReliability) -> List[str]:
        """Generate recommendations based on source reliability"""
        if reliability in [SourceReliability.A1, SourceReliability.A2]:
            return ["High confidence in source", "Can be used as primary evidence"]
        elif reliability in [SourceReliability.B1, SourceReliability.B2]:
            return ["Use with corroboration", "Seek additional sources"]
        else:
            return ["Use with caution", "Requires extensive corroboration"]
    
    def _identify_historical_constraints(self, event) -> List[str]:
        """Identify constraints on historical events"""
        return [
            "Technological limitations",
            "Geographic constraints",
            "Economic limitations",
            "Social and cultural norms"
        ]
    
    def _model_alternative_scenario(self, event, change_point: str, 
                                constraints: List[str]) -> Dict[str, Any]:
        """Model alternative historical scenario"""
        return {
            "change_point": change_point,
            "altered_outcome": f"Alternative outcome for {event.title}",
            "key_changes": [f"Modified {change_point}"],
            "constraints_respected": constraints
        }
    
    def _assess_scenario_plausibility(self, scenario: Dict[str, Any], 
                                  constraints: List[str]) -> float:
        """Assess plausibility of counterfactual scenario"""
        return 0.6  # Simplified
    
    def _model_second_order_effects(self, scenario: Dict[str, Any]) -> List[str]:
        """Model second-order effects of alternative scenario"""
        return [
            "Political realignment",
            "Economic changes",
            "Social consequences"
        ]
    
    def _identify_scenario_uncertainties(self, scenario: Dict[str, Any]) -> List[str]:
        """Identify key uncertainties in scenario"""
        return [
            "Human behavior factors",
            "External influences",
            "Random chance events"
        ]
    
    def _get_relevant_events(self, topic: str, time_period: str) -> List[HistoricalEvent]:
        """Get events relevant to topic and time period"""
        relevant_events = []
        
        for event in self.engine.events.values():
            if topic.lower() in event.title.lower() or topic.lower() in event.description.lower():
                relevant_events.append(event)
        
        return relevant_events
    
    def _get_relevant_figures(self, topic: str, time_period: str) -> List[HistoricalFigure]:
        """Get figures relevant to topic and time period"""
        relevant_figures = []
        
        for figure in self.engine.figures.values():
            if topic.lower() in figure.name.lower() or topic.lower() in str(figure.occupation).lower():
                relevant_figures.append(figure)
        
        return relevant_figures
    
    def _apply_ach_to_topic(self, events: List[HistoricalEvent]) -> Dict[str, Any]:
        """Apply Analysis of Competing Hypotheses to topic"""
        return {
            "hypotheses_generated": len(events),
            "evidence_evaluated": len(events) * 2,
            "diagnostic_indicators": ["Event patterns", "Actor motivations"]
        }
    
    def _analyze_topic_biases(self, events: List[HistoricalEvent]) -> Dict[str, Any]:
        """Analyze biases in topic interpretation"""
        return {
            "confirmation_bias_risk": "medium",
            "hindsight_bias_risk": "high",
            "narrative_bias_risk": "medium"
        }
    
    def _generate_key_judgments(self, ach_analysis: Dict[str, Any], 
                             bias_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate key intelligence judgments"""
        return [
            {
                "judgment": "Multiple factors contributed to historical outcomes",
                "confidence": ConfidenceLevel.MEDIUM,
                "supporting_evidence": ["Event analysis", "Pattern recognition"]
            }
        ]
    
    def _assess_judgment_confidence(self, key_judgments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess confidence in key judgments"""
        return {
            "overall_confidence": ConfidenceLevel.MEDIUM,
            "confidence_factors": ["Source reliability", "Evidence completeness"],
            "confidence_limitations": ["Historical gaps", "Source bias"]
        }
    
    def _extract_topic_lessons(self, events: List[HistoricalEvent], 
                            figures: List[HistoricalFigure]) -> List[str]:
        """Extract lessons learned from topic analysis"""
        return [
            "Historical events have multiple causes",
            "Individual decisions shape outcomes",
            "Context is crucial for understanding"
        ]
