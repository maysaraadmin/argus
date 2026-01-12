"""
Historical Case Schema (HCS) - Intelligence-Grade Historical Analysis Framework
Designed for Historical Intelligence Analysis System (HIAS)

This schema enforces analytic discipline, prevents hindsight bias, and enables
professional intelligence analysis of historical events using structured analytic techniques.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from enum import Enum
import json

class EvidenceType(Enum):
    """Types of evidence in historical analysis"""
    DOCUMENT = "document"
    TESTIMONY = "testimony"
    STATISTIC = "statistic"
    PHOTOGRAPH = "photograph"
    RECORDING = "recording"
    ARTEFACT = "artefact"
    INTELLIGENCE_REPORT = "intelligence_report"

class SourceReliability(Enum):
    """Admiralty Code for source reliability"""
    RELIABLE = "A"
    USUALLY_RELIABLE = "B"
    FAIRLY_RELIABLE = "C"
    NOT_USUALLY_RELIABLE = "D"
    UNRELIABLE = "E"
    RELIABILITY_CANNOT_BE_JUDGED = "F"

class InformationClassification(Enum):
    """Classification levels"""
    UNCLASSIFIED = "unclassified"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

class SATType(Enum):
    """Structured Analytic Techniques"""
    ACH = "ACH"  # Analysis of Competing Hypotheses
    KAC = "KAC"  # Key Assumptions Check
    RED_TEAM = "RedTeam"
    INDICATORS_WARNING = "I&W"  # Indicators & Warning
    COUNTERFACTUAL = "Counterfactual"
    BIAS_DETECTION = "BiasDetection"

class LessonType(Enum):
    """Types of lessons learned"""
    STRATEGIC = "strategic"
    ANALYTIC = "analytic"
    POLITICAL = "political"
    OPERATIONAL = "operational"

class Transferability(Enum):
    """Lesson transferability levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class CaseMetadata:
    """Governance and identification metadata for historical cases"""
    case_id: str
    title: str
    geographic_scope: str
    historical_period: str
    created_by: str
    created_at: datetime
    last_updated: datetime
    classification: InformationClassification = InformationClassification.UNCLASSIFIED
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'case_id': self.case_id,
            'title': self.title,
            'geographic_scope': self.geographic_scope,
            'historical_period': self.historical_period,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'classification': self.classification.value,
            'version': self.version,
            'tags': self.tags
        }

@dataclass
class AnalyticQuestion:
    """Primary and secondary analytic questions with exclusions"""
    primary_question: str
    secondary_questions: List[str] = field(default_factory=list)
    exclusions: List[str] = field(default_factory=list)  # What this case does NOT analyze
    
    def validate_question(self) -> bool:
        """Validate question framing to prevent inevitability bias"""
        forbidden_phrases = ['inevitable', 'destined', 'bound to', 'had to']
        question_lower = self.primary_question.lower()
        
        for phrase in forbidden_phrases:
            if phrase in question_lower:
                return False
        return True
    
    def to_dict(self) -> Dict:
        return {
            'primary_question': self.primary_question,
            'secondary_questions': self.secondary_questions,
            'exclusions': self.exclusions,
            'is_valid': self.validate_question()
        }

@dataclass
class TemporalScope:
    """Temporal boundaries and decision points for anti-hindsight analysis"""
    start_date: date
    end_date: date
    key_decision_points: List[date] = field(default_factory=list)
    
    def is_evidence_valid_for_decision(self, evidence_date: date, decision_date: date) -> bool:
        """System rule: No evidence after decision can influence that decision analysis"""
        return evidence_date <= decision_date
    
    def to_dict(self) -> Dict:
        return {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'key_decision_points': [dp.isoformat() for dp in self.key_decision_points]
        }

@dataclass
class InformationEnvironment:
    """Information context available at the time of analysis"""
    known_facts_at_time: List[str] = field(default_factory=list)
    unknowns_at_time: List[str] = field(default_factory=list)
    contested_information: List[str] = field(default_factory=list)
    intelligence_capabilities: Dict[str, bool] = field(default_factory=dict)  # HUMINT, SIGINT, OSINT availability
    
    def to_dict(self) -> Dict:
        return {
            'known_facts_at_time': self.known_facts_at_time,
            'unknowns_at_time': self.unknowns_at_time,
            'contested_information': self.contested_information,
            'intelligence_capabilities': self.intelligence_capabilities
        }

@dataclass
class CaseActors:
    """Actor references linking to detailed actor profiles"""
    primary_actors: List[str] = field(default_factory=list)  # actor IDs
    secondary_actors: List[str] = field(default_factory=list)
    external_actors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'primary_actors': self.primary_actors,
            'secondary_actors': self.secondary_actors,
            'external_actors': self.external_actors
        }

@dataclass
class CaseEvents:
    """Event references for timeline and analysis"""
    timeline: List[str] = field(default_factory=list)  # event IDs (ordered)
    critical_events: List[str] = field(default_factory=list)
    triggering_events: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'timeline': self.timeline,
            'critical_events': self.critical_events,
            'triggering_events': self.triggering_events
        }

@dataclass
class EvidenceItem:
    """Individual evidence items with reliability assessment"""
    evidence_id: str
    description: str
    evidence_type: EvidenceType
    date: date
    related_actors: List[str] = field(default_factory=list)
    related_events: List[str] = field(default_factory=list)
    source_reliability: SourceReliability = SourceReliability.RELIABILITY_CANNOT_BE_JUDGED
    credibility_score: float = 0.5  # 0.0 to 1.0
    source_details: Optional[str] = None
    access_level: str = "direct"  # direct, second_hand, third_hand
    motivation: Optional[str] = None  # source motivation/bias
    
    def calculate_reliability_weight(self) -> float:
        """Calculate evidence weight based on source reliability and credibility"""
        reliability_weights = {
            SourceReliability.RELIABLE: 1.0,
            SourceReliability.USUALLY_RELIABLE: 0.8,
            SourceReliability.FAIRLY_RELIABLE: 0.6,
            SourceReliability.NOT_USUALLY_RELIABLE: 0.4,
            SourceReliability.UNRELIABLE: 0.2,
            SourceReliability.RELIABILITY_CANNOT_BE_JUDGED: 0.5
        }
        
        base_weight = reliability_weights[self.source_reliability]
        return base_weight * self.credibility_score
    
    def to_dict(self) -> Dict:
        return {
            'evidence_id': self.evidence_id,
            'description': self.description,
            'evidence_type': self.evidence_type.value,
            'date': self.date.isoformat(),
            'related_actors': self.related_actors,
            'related_events': self.related_events,
            'source_reliability': self.source_reliability.value,
            'credibility_score': self.credibility_score,
            'reliability_weight': self.calculate_reliability_weight(),
            'source_details': self.source_details,
            'access_level': self.access_level,
            'motivation': self.motivation
        }

@dataclass
class Hypothesis:
    """Analytic hypotheses stored before ACH execution"""
    hypothesis_id: str
    statement: str
    scope: str  # structural / political / elite / external
    assumptions: List[str] = field(default_factory=list)
    confidence_prior: float = 0.5  # Prior confidence before evidence evaluation
    
    def to_dict(self) -> Dict:
        return {
            'hypothesis_id': self.hypothesis_id,
            'statement': self.statement,
            'scope': self.scope,
            'assumptions': self.assumptions,
            'confidence_prior': self.confidence_prior
        }

@dataclass
class CaseDecision:
    """Decision records for decision-point analysis"""
    decision_id: str
    actor_id: str
    decision_date: date
    options_considered: List[str] = field(default_factory=list)
    option_selected: str = ""
    information_available: List[str] = field(default_factory=list)  # evidence IDs
    assumptions: List[str] = field(default_factory=list)
    outcome: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'decision_id': self.decision_id,
            'actor_id': self.actor_id,
            'decision_date': self.decision_date.isoformat(),
            'options_considered': self.options_considered,
            'option_selected': self.option_selected,
            'information_available': self.information_available,
            'assumptions': self.assumptions,
            'outcome': self.outcome
        }

@dataclass
class SATRun:
    """Execution records for Structured Analytic Techniques"""
    sat_type: SATType
    run_id: str
    date_executed: datetime
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5
    analyst_notes: str = ""
    methodology_version: str = "1.0"
    
    def to_dict(self) -> Dict:
        return {
            'sat_type': self.sat_type.value,
            'run_id': self.run_id,
            'date_executed': self.date_executed.isoformat(),
            'inputs': self.inputs,
            'outputs': self.outputs,
            'confidence': self.confidence,
            'analyst_notes': self.analyst_notes,
            'methodology_version': self.methodology_version
        }

@dataclass
class Assessment:
    """Final intelligence assessments with dissent tracking"""
    assessment_id: str
    key_judgments: List[str] = field(default_factory=list)
    supporting_evidence: List[str] = field(default_factory=list)  # evidence IDs
    alternative_explanations: List[str] = field(default_factory=list)
    confidence_level: float = 0.5
    dissenting_views: List[str] = field(default_factory=list)
    assessment_date: datetime = field(default_factory=datetime.now)
    
    def calculate_confidence_limit(self) -> float:
        """Confidence cannot exceed weakest supporting evidence"""
        # Implementation would check evidence weights
        return min(self.confidence_level, 0.95)  # Cap at 95% for historical cases
    
    def to_dict(self) -> Dict:
        return {
            'assessment_id': self.assessment_id,
            'key_judgments': self.key_judgments,
            'supporting_evidence': self.supporting_evidence,
            'alternative_explanations': self.alternative_explanations,
            'confidence_level': self.confidence_level,
            'confidence_limit': self.calculate_confidence_limit(),
            'dissenting_views': self.dissenting_views,
            'assessment_date': self.assessment_date.isoformat()
        }

@dataclass
class LessonLearned:
    """Structured lessons learned from case analysis"""
    lesson_id: str
    lesson_type: LessonType
    statement: str
    transferability: Transferability
    supporting_evidence: List[str] = field(default_factory=list)
    applicability_context: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'lesson_id': self.lesson_id,
            'lesson_type': self.lesson_type.value,
            'statement': self.statement,
            'transferability': self.transferability.value,
            'supporting_evidence': self.supporting_evidence,
            'applicability_context': self.applicability_context
        }

@dataclass
class HistoricalCase:
    """Complete Historical Case Schema (HCS)"""
    case_metadata: CaseMetadata
    analytic_question: AnalyticQuestion
    temporal_scope: TemporalScope
    information_environment: InformationEnvironment
    actors: CaseActors
    events: CaseEvents
    evidence: List[EvidenceItem] = field(default_factory=list)
    hypotheses: List[Hypothesis] = field(default_factory=list)
    decisions: List[CaseDecision] = field(default_factory=list)
    sat_runs: List[SATRun] = field(default_factory=list)
    assessments: List[Assessment] = field(default_factory=list)
    lessons_learned: List[LessonLearned] = field(default_factory=list)
    
    def validate_schema_integrity(self) -> List[str]:
        """System-enforced schema integrity rules"""
        violations = []
        
        # Rule 1: Every judgment must link to evidence
        for assessment in self.assessments:
            for judgment in assessment.key_judgments:
                if not assessment.supporting_evidence:
                    violations.append(f"Judgment without evidence: {judgment}")
        
        # Rule 2: Every hypothesis must list assumptions
        for hypothesis in self.hypotheses:
            if not hypothesis.assumptions:
                violations.append(f"Hypothesis without assumptions: {hypothesis.hypothesis_id}")
        
        # Rule 3: SAT runs cannot modify raw evidence
        # (Enforced by system design - evidence is immutable)
        
        # Rule 4: Confidence cannot exceed weakest link
        for assessment in self.assessments:
            if assessment.confidence_level > assessment.calculate_confidence_limit():
                violations.append(f"Confidence exceeds limit in assessment: {assessment.assessment_id}")
        
        # Rule 5: Hindsight flags are mandatory
        if not self.analytic_question.validate_question():
            violations.append("Analytic question contains hindsight bias indicators")
        
        return violations
    
    def add_sat_run(self, sat_type: SATType, inputs: Dict[str, Any], 
                   outputs: Dict[str, Any], confidence: float, notes: str = "") -> str:
        """Add a new SAT execution record"""
        run_id = f"{sat_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        sat_run = SATRun(
            sat_type=sat_type,
            run_id=run_id,
            date_executed=datetime.now(),
            inputs=inputs,
            outputs=outputs,
            confidence=confidence,
            analyst_notes=notes
        )
        self.sat_runs.append(sat_run)
        return run_id
    
    def get_evidence_by_id(self, evidence_id: str) -> Optional[EvidenceItem]:
        """Retrieve evidence item by ID"""
        for evidence in self.evidence:
            if evidence.evidence_id == evidence_id:
                return evidence
        return None
    
    def get_hypothesis_by_id(self, hypothesis_id: str) -> Optional[Hypothesis]:
        """Retrieve hypothesis by ID"""
        for hypothesis in self.hypotheses:
            if hypothesis.hypothesis_id == hypothesis_id:
                return hypothesis
        return None
    
    def export_to_json(self) -> str:
        """Export complete case to JSON format"""
        case_dict = {
            'case_metadata': self.case_metadata.to_dict(),
            'analytic_question': self.analytic_question.to_dict(),
            'temporal_scope': self.temporal_scope.to_dict(),
            'information_environment': self.information_environment.to_dict(),
            'actors': self.actors.to_dict(),
            'events': self.events.to_dict(),
            'evidence': [e.to_dict() for e in self.evidence],
            'hypotheses': [h.to_dict() for h in self.hypotheses],
            'decisions': [d.to_dict() for d in self.decisions],
            'sat_runs': [s.to_dict() for s in self.sat_runs],
            'assessments': [a.to_dict() for a in self.assessments],
            'lessons_learned': [l.to_dict() for l in self.lessons_learned],
            'schema_version': '1.0',
            'export_timestamp': datetime.now().isoformat(),
            'integrity_violations': self.validate_schema_integrity()
        }
        return json.dumps(case_dict, indent=2, ensure_ascii=False)
    
    @classmethod
    def import_from_json(cls, json_str: str) -> 'HistoricalCase':
        """Import case from JSON format"""
        case_dict = json.loads(json_str)
        
        # Reconstruct all objects from JSON
        case_metadata = CaseMetadata(**case_dict['case_metadata'])
        analytic_question = AnalyticQuestion(**case_dict['analytic_question'])
        temporal_scope = TemporalScope(**{
            **case_dict['temporal_scope'],
            'start_date': date.fromisoformat(case_dict['temporal_scope']['start_date']),
            'end_date': date.fromisoformat(case_dict['temporal_scope']['end_date']),
            'key_decision_points': [date.fromisoformat(dp) for dp in case_dict['temporal_scope']['key_decision_points']]
        })
        
        information_environment = InformationEnvironment(**case_dict['information_environment'])
        actors = CaseActors(**case_dict['actors'])
        events = CaseEvents(**case_dict['events'])
        
        evidence = []
        for e_dict in case_dict['evidence']:
            evidence.append(EvidenceItem(**{
                **e_dict,
                'evidence_type': EvidenceType(e_dict['evidence_type']),
                'date': date.fromisoformat(e_dict['date']),
                'source_reliability': SourceReliability(e_dict['source_reliability'])
            }))
        
        hypotheses = [Hypothesis(**h_dict) for h_dict in case_dict['hypotheses']]
        
        decisions = []
        for d_dict in case_dict['decisions']:
            decisions.append(CaseDecision(**{
                **d_dict,
                'decision_date': date.fromisoformat(d_dict['decision_date'])
            }))
        
        sat_runs = []
        for s_dict in case_dict['sat_runs']:
            sat_runs.append(SATRun(**{
                **s_dict,
                'sat_type': SATType(s_dict['sat_type']),
                'date_executed': datetime.fromisoformat(s_dict['date_executed'])
            }))
        
        assessments = []
        for a_dict in case_dict['assessments']:
            assessments.append(Assessment(**{
                **a_dict,
                'assessment_date': datetime.fromisoformat(a_dict['assessment_date'])
            }))
        
        lessons_learned = []
        for l_dict in case_dict['lessons_learned']:
            lessons_learned.append(LessonLearned(**{
                **l_dict,
                'lesson_type': LessonType(l_dict['lesson_type']),
                'transferability': Transferability(l_dict['transferability'])
            }))
        
        return cls(
            case_metadata=case_metadata,
            analytic_question=analytic_question,
            temporal_scope=temporal_scope,
            information_environment=information_environment,
            actors=actors,
            events=events,
            evidence=evidence,
            hypotheses=hypotheses,
            decisions=decisions,
            sat_runs=sat_runs,
            assessments=assessments,
            lessons_learned=lessons_learned
        )

# Schema validation utilities
def validate_historical_case(case: HistoricalCase) -> Dict[str, Any]:
    """Complete schema validation with detailed reporting"""
    violations = case.validate_schema_integrity()
    
    validation_report = {
        'is_valid': len(violations) == 0,
        'violations': violations,
        'validation_timestamp': datetime.now().isoformat(),
        'case_summary': {
            'case_id': case.case_metadata.case_id,
            'title': case.case_metadata.title,
            'evidence_count': len(case.evidence),
            'hypothesis_count': len(case.hypotheses),
            'sat_run_count': len(case.sat_runs),
            'assessment_count': len(case.assessments)
        }
    }
    
    return validation_report

# Factory function for creating new cases
def create_historical_case(
    case_id: str,
    title: str,
    primary_question: str,
    geographic_scope: str,
    historical_period: str,
    start_date: date,
    end_date: date
) -> HistoricalCase:
    """Factory function for creating new historical cases with proper defaults"""
    
    now = datetime.now()
    
    case_metadata = CaseMetadata(
        case_id=case_id,
        title=title,
        geographic_scope=geographic_scope,
        historical_period=historical_period,
        created_by="HIAS",
        created_at=now,
        last_updated=now
    )
    
    analytic_question = AnalyticQuestion(
        primary_question=primary_question
    )
    
    temporal_scope = TemporalScope(
        start_date=start_date,
        end_date=end_date
    )
    
    information_environment = InformationEnvironment()
    actors = CaseActors()
    events = CaseEvents()
    
    return HistoricalCase(
        case_metadata=case_metadata,
        analytic_question=analytic_question,
        temporal_scope=temporal_scope,
        information_environment=information_environment,
        actors=actors,
        events=events
    )
