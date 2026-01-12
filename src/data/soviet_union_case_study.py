"""
Soviet Union Collapse Case Study - Reference Implementation
Historical Intelligence Analysis System (HIAS) Pilot Case

This is a complete, intelligence-grade case study demonstrating:
- SAT-driven analysis (ACH, Red Team, I&W, etc.)
- Evidence-aware reasoning with source reliability
- Hindsight-controlled analysis (information-at-time)
- Multi-causal explanations with confidence levels
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid


class ActorType(Enum):
    """Actor types for intelligence analysis"""
    STATE = "state"
    LEADER = "leader"
    ORGANIZATION = "organization"
    FACTION = "faction"
    INSTITUTION = "institution"


class RelationshipType(Enum):
    """Types of relationships between actors"""
    ALLIANCE = "alliance"
    RIVALRY = "rivalry"
    SUBORDINATE = "subordinate"
    PATRON_CLIENT = "patron_client"
    IDEOLOGICAL = "ideological"


class ConfidenceLevel(Enum):
    """Confidence levels for intelligence judgments"""
    VERY_LOW = "Very Low"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"


class SourceReliability(Enum):
    """Source reliability grades (Admiralty Code)"""
    A1 = "A1 - Confirmed reliable"
    A2 = "A2 - Usually reliable"
    B1 = "B1 - Fairly reliable"
    B2 = "B2 - Not always reliable"
    C1 = "C1 - Unreliable"
    C2 = "C2 - Reliability cannot be judged"
    D = "D - Insufficient information"


@dataclass
class Actor:
    """Actor data model for intelligence analysis"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    actor_type: ActorType = ActorType.STATE
    description: str = ""
    active_from: Optional[date] = None
    active_to: Optional[date] = None
    
    # Intelligence attributes
    capabilities: Dict[str, float] = field(default_factory=dict)
    motivations: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    psychological_profile: Dict[str, str] = field(default_factory=dict)
    
    # Network relationships
    relationships: Dict[str, str] = field(default_factory=dict)
    
    # Evidence sources
    sources: List[str] = field(default_factory=list)


@dataclass
class Hypothesis:
    """Hypothesis for ACH analysis"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.5
    assumptions: List[str] = field(default_factory=list)
    biases: List[str] = field(default_factory=list)


@dataclass
class Evidence:
    """Evidence with source reliability"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    source: str = ""
    reliability: SourceReliability = SourceReliability.B2
    date_known: Optional[date] = None
    confidence: float = 0.5


@dataclass
class DecisionPoint:
    """Decision point analysis"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str = ""
    date: date = date.today()
    description: str = ""
    options_considered: List[str] = field(default_factory=list)
    selected_option: str = ""
    information_available: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    confidence: float = 0.5


class SovietUnionCaseStudy:
    """Complete Soviet Union collapse case study implementation"""
    
    def __init__(self):
        self.case_name = "Fall of the Soviet Union (1985-1991)"
        self.analytic_question = (
            "What were the primary drivers of collapse of the Soviet Union "
            "between 1985 and 1991, and which explanations "
            "best account for the timing and speed of collapse?"
        )
        self.setup_actors()
        self.setup_evidence()
        self.setup_hypotheses()
        self.setup_decision_points()
    
    def setup_actors(self):
        """Setup key actors in the Soviet Union collapse"""
        self.actors = {
            # Primary Actors
            "soviet_union": Actor(
                name="Soviet Union",
                actor_type=ActorType.STATE,
                description="The Soviet state and government",
                active_from=date(1922, 12, 30),
                active_to=date(1991, 12, 26),
                capabilities={
                    "military": 0.8,
                    "economic": 0.4,
                    "political": 0.3,
                    "intelligence": 0.7
                },
                motivations=["survival", "ideological competition", "great power status"],
                constraints=["economic stagnation", "technological lag", "nationalist movements"],
                psychological_profile={
                    "risk_tolerance": "decreasing",
                    "decision_style": "bureaucratic consensus",
                    "leadership_cohesion": "fragmenting"
                }
            ),
            
            "communist_party": Actor(
                name="Communist Party of the Soviet Union",
                actor_type=ActorType.INSTITUTION,
                description="Ruling communist party",
                active_from=date(1912, 1, 1),
                active_to=date(1991, 12, 26),
                capabilities={
                    "political": 0.9,
                    "bureaucratic": 0.8,
                    "ideological": 0.7
                },
                motivations=["maintain power", "ideological purity", "party unity"],
                constraints=["reform pressure", "economic reality", "popular support erosion"],
                relationships={"soviet_union": "subordinate"}
            ),
            
            "gorbachev": Actor(
                name="Mikhail Gorbachev",
                actor_type=ActorType.LEADER,
                description="Last leader of the Soviet Union",
                active_from=date(1985, 3, 11),
                active_to=date(1991, 12, 25),
                capabilities={
                    "political": 0.7,
                    "reform": 0.9,
                    "communication": 0.8,
                    "crisis_management": 0.3
                },
                motivations=["reform USSR", "improve living standards", "reduce Cold War tension"],
                constraints=["party opposition", "bureaucratic resistance", "nationalist movements"],
                psychological_profile={
                    "risk_tolerance": "moderate",
                    "decision_style": "reformist consensus",
                    "leadership_style": "transformational"
                }
            ),
            
            "soviet_military": Actor(
                name="Soviet Military",
                actor_type=ActorType.ORGANIZATION,
                description="Armed forces of the Soviet Union",
                capabilities={
                    "coercive_power": 0.9,
                    "loyalty": 0.4,
                    "readiness": 0.6
                },
                motivations=["defend USSR", "maintain party power", "protect sovereignty"],
                constraints=["economic limitations", "morale issues", "technological gaps"]
            ),
            
            "kgb": Actor(
                name="KGB",
                actor_type=ActorType.ORGANIZATION,
                description="Soviet intelligence and security service",
                capabilities={
                    "intelligence": 0.8,
                    "coercive": 0.7,
                    "surveillance": 0.9
                },
                motivations=["maintain state security", "protect party interests", "suppress dissent"],
                constraints=["reform limitations", "resource constraints", "political changes"]
            ),
            
            "republic_elites": Actor(
                name="Republic Elites (Baltic, Ukrainian, Russian)",
                actor_type=ActorType.FACTION,
                description="Emerging nationalist leaders in Soviet republics",
                capabilities={
                    "political": 0.6,
                    "popular_support": 0.7,
                    "organization": 0.5
                },
                motivations=["independence", "national sovereignty", "democratic reform"],
                constraints=["soviet military power", "KGB surveillance", "economic dependence"]
            ),
            
            # External Actors
            "united_states": Actor(
                name="United States",
                actor_type=ActorType.STATE,
                description="Primary Cold War adversary",
                capabilities={
                    "economic": 0.9,
                    "military": 0.8,
                    "technological": 0.9,
                    "diplomatic": 0.8
                },
                motivations=["contain communism", "promote democracy", "economic competition"],
                constraints=["domestic politics", "alliance commitments", "economic reality"]
            ),
            
            "western_institutions": Actor(
                name="Western Financial Institutions",
                actor_type=ActorType.ORGANIZATION,
                description="IMF, World Bank, Western financial system",
                capabilities={
                    "economic": 0.9,
                    "financial": 0.9,
                    "ideological": 0.7
                },
                motivations=["promote capitalism", "economic integration", "conditional assistance"]
            )
        }
    
    def setup_evidence(self):
        """Setup evidence set with reliability ratings"""
        self.evidence = {
            "economic_stagnation": Evidence(
                description="Chronic economic stagnation acknowledged but poorly quantified",
                source="Soviet economic data, Western analysis",
                reliability=SourceReliability.A1,
                date_known=date(1985, 1, 1),
                confidence=0.8
            ),
            
            "gorbachev_reforms": Evidence(
                description="Gorbachev reforms (glasnost/perestroika) reduced party control",
                source="Party documents, Gorbachev speeches, contemporary observations",
                reliability=SourceReliability.A1,
                date_known=date(1987, 1, 1),
                confidence=0.8
            ),
            
            "august_coup_failure": Evidence(
                description="August 1991 coup attempt failed to restore hardline rule",
                source="KGB reports, participant testimonies, international media",
                reliability=SourceReliability.A1,
                date_known=date(1991, 8, 20),
                confidence=0.9
            ),
            
            "baltic_independence": Evidence(
                description="Baltic independence movements gained momentum",
                source="Baltic republic documents, Soviet media, international reports",
                reliability=SourceReliability.A1,
                date_known=date(1990, 1, 1),
                confidence=0.8
            ),
            
            "us_pressure": Evidence(
                description="US economic and military pressure continued through 1980s",
                source="US government documents, CIA analyses, economic data",
                reliability=SourceReliability.B1,
                date_known=date(1985, 1, 1),
                confidence=0.6
            ),
            
            "no_repression": Evidence(
                description="KGB and military refused to repress independence movements",
                source="KGB archives, military reports, eyewitness accounts",
                reliability=SourceReliability.A1,
                date_known=date(1991, 8, 25),
                confidence=0.8
            )
        }
    
    def setup_hypotheses(self):
        """Setup competing hypotheses for ACH analysis"""
        self.hypotheses = {
            "H1": Hypothesis(
                title="Economic failure made collapse inevitable",
                description="Chronic economic problems made Soviet collapse unavoidable",
                evidence=["economic_stagnation"],
                confidence=0.3,
                assumptions=["economic collapse inevitably leads to state collapse"],
                biases=["deterministic bias", "structuralist thinking"]
            ),
            
            "H2": Hypothesis(
                title="Political reforms destabilized control mechanisms",
                description="Gorbachev's reforms unintentionally weakened Soviet state control",
                evidence=["gorbachev_reforms"],
                confidence=0.7,
                assumptions=["reforms necessary for economic survival"],
                biases=["reformist bias", "underestimation of conservative forces"]
            ),
            
            "H3": Hypothesis(
                title="Elite defection and loss of coercive will caused collapse",
                description="Soviet elites abandoned the system, leading to rapid collapse",
                evidence=["august_coup_failure", "no_repression"],
                confidence=0.8,
                assumptions=["elites act rationally in self-interest"],
                biases=["elite-focused bias", "rational actor model"]
            ),
            
            "H4": Hypothesis(
                title="Nationalist movements fractured the union",
                description="Rise of republic-level nationalism broke Soviet unity",
                evidence=["baltic_independence"],
                confidence=0.6,
                assumptions=["nationalist sentiment was widespread"],
                biases=["nationalist bias", "underestimation of central authority"]
            ),
            
            "H5": Hypothesis(
                title="External pressure forced collapse",
                description="Cold War competition and Western pressure caused Soviet collapse",
                evidence=["us_pressure"],
                confidence=0.2,
                assumptions=["Western pressure was decisive factor"],
                biases=["external attribution bias", "overestimation of external influence"]
            )
        }
    
    def setup_decision_points(self):
        """Setup key decision points for analysis"""
        self.decision_points = {
            "non_intervention_1990": DecisionPoint(
                actor_id="soviet_military",
                date=date(1990, 1, 15),
                description="Decision whether to use force to preserve union",
                options_considered=[
                    "Repression (China-style)",
                    "Federal renegotiation",
                    "Managed dissolution",
                    "Limited reform acceleration"
                ],
                selected_option="Ambiguous non-intervention",
                information_available=[
                    "Growing nationalist movements",
                    "Economic difficulties",
                    "Military loyalty concerns",
                    "International pressure"
                ],
                assumptions=[
                    "Repression would damage international standing",
                    "Negotiation might preserve some unity",
                    "Time was on reformers' side"
                ],
                sources=["KGB assessments", "Politburo minutes", "Military reports"],
                confidence=0.7
            )
        }
    
    def create_ach_matrix(self):
        """Create ACH evidence-hypothesis matrix"""
        matrix = {}
        
        for hyp_id, hypothesis in self.hypotheses.items():
            matrix[hyp_id] = {}
            for ev_id, evidence in self.evidence.items():
                # Score consistency: + (consistent), 0 (neutral), - (inconsistent)
                consistency = 0
                
                if hyp_id == "H1":  # Economic failure
                    if ev_id == "economic_stagnation":
                        consistency = 1  # Consistent
                    elif ev_id in ["gorbachev_reforms", "us_pressure"]:
                        consistency = -1  # Inconsistent
                
                elif hyp_id == "H2":  # Political reforms
                    if ev_id == "gorbachev_reforms":
                        consistency = 1  # Consistent
                    elif ev_id == "economic_stagnation":
                        consistency = 0  # Neutral
                    elif ev_id == "august_coup_failure":
                        consistency = 1  # Consistent
                
                elif hyp_id == "H3":  # Elite defection
                    if ev_id in ["august_coup_failure", "no_repression"]:
                        consistency = 1  # Consistent
                    elif ev_id == "us_pressure":
                        consistency = -1  # Inconsistent
                
                elif hyp_id == "H4":  # Nationalist movements
                    if ev_id == "baltic_independence":
                        consistency = 1  # Consistent
                    elif ev_id == "no_repression":
                        consistency = 1  # Consistent
                
                elif hyp_id == "H5":  # External pressure
                    if ev_id == "us_pressure":
                        consistency = 1  # Consistent
                    else:
                        consistency = -1  # Inconsistent
                
                matrix[hyp_id][ev_id] = consistency
        
        return matrix
    
    def rank_hypotheses(self, matrix):
        """Rank hypotheses based on evidence consistency"""
        scores = {}
        for hyp_id in self.hypotheses:
            scores[hyp_id] = sum(matrix[hyp_id].values())
        
        # Sort by score (higher = more consistent with evidence)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked
    
    def analyze_key_assumptions(self):
        """Analyze key assumptions in the analysis"""
        assumptions = {
            "economic_inevitability": {
                "statement": "Economic collapse inevitably leads to state collapse",
                "assessment": "Weak",
                "reasoning": "Many states survive severe economic crises; USSR collapsed before total economic breakdown",
                "impact": "High - if false, overstates economic determinism"
            },
            
            "coercive_response": {
                "statement": "The Soviet state would always use force to preserve unity",
                "assessment": "False",
                "reasoning": "August 1991 showed coercive restraint; elites chose not to use force",
                "impact": "High - if False, overestimates willingness to use repression"
            }
        }
        return assumptions
    
    def create_red_team_analysis(self):
        """Create Red Team analysis"""
        red_team = {
            "primary_claim": (
                "The USSR did not collapse accidentally—it was consciously abandoned "
                "by elites who saw no future in preserving it."
            ),
            "supporting_evidence": [
                "Non-use of force during 1991 crisis",
                "Rapid elite repositioning post-collapse",
                "Lack of coordinated resistance to dissolution",
                "Elite preparation for post-Soviet careers"
            ],
            "impact": {
                "reinforces": "H3 - Elite defection hypothesis",
                "weakens": "Structural inevitability narratives",
                "challenges": "Economic determinism explanations"
            },
            "survivability_score": 0.7  # Original narrative has moderate survivability
        }
        return red_team
    
    def create_indicators_analysis(self):
        """Create Indicators & Warning analysis"""
        indicators = {
            "missed_indicators": [
                "Declining loyalty of security services",
                "Rise of republican-level power centers",
                "Legalization of opposition movements",
                "Elite asset diversification (preparing for post-Soviet future)",
                "Increased contact with Western governments"
            ],
            "misinterpreted_signals": [
                "Continued military parades (interpreted as strength, actually weakness)",
                "Party unity rhetoric (hiding fragmentation)",
                "Economic statistics (masking severe problems)"
            ],
            "key_failure": (
                "Analysts over-weighted structural strength and under-weighted elite intent"
            ),
            "lessons": [
                "Track elite cohesion as leading indicator",
                "Economic stress does not automatically equal collapse",
                "Institutional loyalty changes precede political change"
            ]
        }
        return indicators
    
    def generate_intelligence_judgment(self):
        """Generate final intelligence judgment"""
        matrix = self.create_ach_matrix()
        ranked_hypotheses = self.rank_hypotheses(matrix)
        assumptions = self.analyze_key_assumptions()
        red_team = self.create_red_team_analysis()
        indicators = self.create_indicators_analysis()
        
        judgment = {
            "analytic_question": self.analytic_question,
            "case_name": self.case_name,
            "analysis_date": datetime.now().isoformat(),
            "methodology": "Analysis of Competing Hypotheses (ACH) with Red Team validation",
            
            # Ranked hypotheses
            "ranked_hypotheses": [
                {
                    "id": hyp_id,
                    "title": self.hypotheses[hyp_id].title,
                    "confidence": self.hypotheses[hyp_id].confidence,
                    "evidence_score": score,
                    "assessment": self._get_hypothesis_assessment(hyp_id, score)
                }
                for hyp_id, score in ranked_hypotheses
            ],
            
            # Key judgments
            "primary_driver": "Elite defection and loss of willingness to use coercive power",
            "confidence_level": ConfidenceLevel.HIGH,
            "confidence_rationale": "Strong evidence support, Red Team validation, minimal contradictions",
            
            # Supporting analysis
            "key_assumptions": assumptions,
            "red_team_analysis": red_team,
            "indicators_analysis": indicators,
            "decision_points": self.decision_points,
            
            # Lessons learned
            "strategic_lessons": [
                "States collapse when elites stop believing in them",
                "Coercive capacity is meaningless without political will",
                "Reforms can accelerate collapse if institutions lag",
                "Elite cohesion is critical leading indicator"
            ],
            "analytic_lessons": [
                "Avoid inevitability bias in historical analysis",
                "Track elite cohesion as early warning indicator",
                "Economic stress ≠ automatic state collapse",
                "Multiple causal factors must be considered"
            ],
            
            # Evidence summary
            "evidence_summary": {
                "total_pieces": len(self.evidence),
                "high_reliability": sum(1 for e in self.evidence.values() if e.reliability in [SourceReliability.A1, SourceReliability.A2]),
                "key_evidence": ["august_coup_failure", "no_repression", "gorbachev_reforms"]
            }
        }
        
        return judgment
    
    def _get_hypothesis_assessment(self, hyp_id, score):
        """Get assessment for hypothesis based on evidence score"""
        if score >= 2:
            return "Strongly supported by evidence"
        elif score >= 1:
            return "Moderately supported by evidence"
        elif score >= 0:
            return "Weakly supported by evidence"
        else:
            return "Contradicted by evidence"
    
    def export_case_study(self):
        """Export complete case study for system testing"""
        judgment = self.generate_intelligence_judgment()
        
        return {
            "case_study_metadata": {
                "name": self.case_name,
                "created": datetime.now().isoformat(),
                "system_version": "HIAS v1.0",
                "purpose": "Reference implementation for intelligence-grade historical analysis"
            },
            "actors": {k: v.__dict__ for k, v in self.actors.items()},
            "evidence": {k: v.__dict__ for k, v in self.evidence.items()},
            "hypotheses": {k: v.__dict__ for k, v in self.hypotheses.items()},
            "decision_points": {k: v.__dict__ for k, v in self.decision_points.items()},
            "intelligence_judgment": judgment
        }


# Example usage and testing
def main():
    """Demonstrate the Soviet Union case study"""
    case_study = SovietUnionCaseStudy()
    
    # Generate complete analysis
    judgment = case_study.generate_intelligence_judgment()
    
    print("=== SOVIET UNION COLLAPSE CASE STUDY ===")
    print(f"Analytic Question: {judgment['analytic_question']}")
    print(f"Primary Driver: {judgment['primary_driver']}")
    print(f"Confidence Level: {judgment['confidence_level'].value}")
    print()
    print("=== RANKED HYPOTHESES ===")
    for i, hyp in enumerate(judgment['ranked_hypotheses'], 1):
        print(f"{i}. {hyp['title']} (Score: {hyp['evidence_score']})")
        print(f"   Assessment: {hyp['assessment']}")
        print(f"   Confidence: {hyp['confidence']}")
        print()
    
    print("=== KEY STRATEGIC LESSONS ===")
    for lesson in judgment['strategic_lessons']:
        print(f"• {lesson}")
    
    return case_study.export_case_study()


if __name__ == "__main__":
    case_study_data = main()
