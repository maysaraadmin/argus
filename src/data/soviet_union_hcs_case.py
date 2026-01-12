"""
Soviet Union Case Study - Historical Case Schema (HCS) Implementation
Intelligence-grade analysis of Soviet Union collapse (1985-1991)

This case demonstrates complete HCS framework with anti-hindsight analysis,
structured analytic techniques, and professional intelligence standards.
"""

import sys
import os
from datetime import datetime, date

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.historical_case_schema import (
    HistoricalCase, create_historical_case, EvidenceItem, Hypothesis, 
    CaseDecision, SATRun, Assessment, LessonLearned,
    EvidenceType, SourceReliability, SATType, LessonType, Transferability,
    validate_historical_case
)

def create_soviet_union_case() -> HistoricalCase:
    """Create complete Soviet Union case study using HCS framework"""
    
    # Create base case
    case = create_historical_case(
        case_id="USSR-1991",
        title="Collapse of the Soviet Union (1985-1991)",
        primary_question="What best explains the timing and speed of the USSR collapse?",
        geographic_scope="Soviet Union and Eastern Europe",
        historical_period="1985-1991",
        start_date=date(1985, 3, 11),  # Gorbachev comes to power
        end_date=date(1991, 12, 26)    # USSR officially dissolved
    )
    
    # Add exclusions to prevent hindsight bias
    case.analytic_question.exclusions = [
        "Post-1991 economic performance of successor states",
        "Current geopolitical situation in Eastern Europe",
        "Long-term outcomes of transition",
        "Modern Russia's foreign policy"
    ]
    
    # Add key decision points
    case.temporal_scope.key_decision_points = [
        date(1986, 4, 26),   # Chernobyl disaster
        date(1989, 11, 9),   # Fall of Berlin Wall
        date(1990, 3, 15),   # Lithuania declares independence
        date(1991, 8, 19),   # August Coup attempt
        date(1991, 12, 8),   # Belavezha Accords
    ]
    
    # Information environment (what was known at the time)
    case.information_environment.known_facts_at_time = [
        "Soviet economy experiencing stagnation since 1970s",
        "Gorbachev implementing Glasnost and Perestroika",
        "Eastern Bloc countries experiencing unrest",
        "Nationalist movements growing in republics",
        "Military and security services facing budget pressures"
    ]
    
    case.information_environment.unknowns_at_time = [
        "True loyalty of security services to central government",
        "Extent of elite preparation for post-Soviet future",
        "Willingness to use force against republics",
        "International response to dissolution"
    ]
    
    case.information_environment.contested_information = [
        "Actual economic performance indicators",
        "Popular support for independence movements",
        "Military readiness and reliability"
    ]
    
    case.information_environment.intelligence_capabilities = {
        "HUMINT": True,   # Human intelligence available
        "SIGINT": True,   # Signals intelligence limited
        "OSINT": True,    # Open source increasing
        "IMINT": False    # Imagery intelligence limited
    }
    
    # Actors
    case.actors.primary_actors = [
        "mikhail_gorbachev",
        "soviet_communist_party",
        "soviet_military",
        "kgb"
    ]
    
    case.actors.secondary_actors = [
        "boris_yeltsin",
        "republican_leaders",
        "economic_reformers",
        "conservative_hardliners"
    ]
    
    case.actors.external_actors = [
        "united_states",
        "nato",
        "china",
        "european_communities"
    ]
    
    # Evidence items
    case.evidence = [
        EvidenceItem(
            evidence_id="E001",
            description="August 1991 coup attempt fails to gain military support",
            evidence_type=EvidenceType.DOCUMENT,
            date=date(1991, 8, 21),
            related_actors=["soviet_military", "kgb", "conservative_hardliners"],
            related_events=["august_coup"],
            source_reliability=SourceReliability.RELIABLE,
            credibility_score=0.9,
            source_details="Contemporary Western intelligence reports",
            access_level="direct"
        ),
        EvidenceItem(
            evidence_id="E002",
            description="Soviet GDP growth negative for 3 consecutive years (1989-1991)",
            evidence_type=EvidenceType.STATISTIC,
            date=date(1991, 6, 30),
            related_actors=["soviet_communist_party"],
            source_reliability=SourceReliability.USUALLY_RELIABLE,
            credibility_score=0.8,
            source_details="Official Soviet statistics",
            access_level="second_hand"
        ),
        EvidenceItem(
            evidence_id="E003",
            description="Gorbachev refuses to use force against Baltic independence",
            evidence_type=EvidenceType.TESTIMONY,
            date=date(1991, 1, 13),
            related_actors=["mikhail_gorbachev"],
            related_events=["lithuania_independence"],
            source_reliability=SourceReliability.FAIRLY_RELIABLE,
            credibility_score=0.7,
            source_details="Kremlin insider testimony",
            access_level="second_hand",
            motivation="Political justification"
        ),
        EvidenceItem(
            evidence_id="E004",
            description="Elite asset diversification to foreign banks detected",
            evidence_type=EvidenceType.INTELLIGENCE_REPORT,
            date=date(1991, 7, 15),
            related_actors=["republican_leaders", "economic_reformers"],
            source_reliability=SourceReliability.USUALLY_RELIABLE,
            credibility_score=0.8,
            source_details="Western financial intelligence",
            access_level="direct"
        ),
        EvidenceItem(
            evidence_id="E005",
            description="Military units refuse orders to suppress protests",
            evidence_type=EvidenceType.TESTIMONY,
            date=date(1991, 8, 20),
            related_actors=["soviet_military"],
            related_events=["august_coup"],
            source_reliability=SourceReliability.RELIABLE,
            credibility_score=0.9,
            source_details="Multiple officer testimonies",
            access_level="direct"
        ),
        EvidenceItem(
            evidence_id="E006",
            description="Republic leaders coordinate dissolution strategy",
            evidence_type=EvidenceType.DOCUMENT,
            date=date(1991, 12, 8),
            related_actors=["republican_leaders"],
            related_events=["belavezha_accords"],
            source_reliability=SourceReliability.RELIABLE,
            credibility_score=0.95,
            source_details="Belavezha Accords document",
            access_level="direct"
        )
    ]
    
    # Hypotheses (pre-ACH)
    case.hypotheses = [
        Hypothesis(
            hypothesis_id="H1",
            statement="Economic collapse made USSR unsustainable",
            scope="structural",
            assumptions=[
                "Economic problems were irreversible",
                "Political systems depend on economic performance",
                "No alternative economic models available"
            ],
            confidence_prior=0.6
        ),
        Hypothesis(
            hypothesis_id="H2",
            statement="Gorbachev's reforms unintentionally caused collapse",
            scope="political",
            assumptions=[
                "Reforms were primary causal factor",
                "System was stable before reforms",
                "Reform outcomes were unintended"
            ],
            confidence_prior=0.5
        ),
        Hypothesis(
            hypothesis_id="H3",
            statement="Elite defection and loss of coercive will caused collapse",
            scope="elite",
            assumptions=[
                "Elites had choice to preserve USSR",
                "Coercive capacity existed without willingness to use",
                "Elite self-interest drove decisions"
            ],
            confidence_prior=0.7
        ),
        Hypothesis(
            hypothesis_id="H4",
            statement="Nationalist movements overwhelmed central authority",
            scope="political",
            assumptions=[
                "Nationalism was primary driver",
                "Central authority was weak",
                "Republics had unified goals"
            ],
            confidence_prior=0.4
        ),
        Hypothesis(
            hypothesis_id="H5",
            statement="External pressure and containment strategy succeeded",
            scope="external",
            assumptions=[
                "Western policies were decisive",
                "Cold War pressure was effective",
                "External factors outweighed internal"
            ],
            confidence_prior=0.3
        )
    ]
    
    # Decision records
    case.decisions = [
        CaseDecision(
            decision_id="D001",
            actor_id="mikhail_gorbachev",
            decision_date=date(1991, 1, 13),
            options_considered=["Use force", "Negotiate", "Allow independence"],
            option_selected="Negotiate",
            information_available=["E002", "E003"],
            assumptions=["Force would backfire", "Negotiation could preserve union"],
            outcome="Failed to preserve union"
        ),
        CaseDecision(
            decision_id="D002",
            actor_id="soviet_military",
            decision_date=date(1991, 8, 19),
            options_considered=["Support coup", "Remain neutral", "Support Gorbachev"],
            option_selected="Remain neutral",
            information_available=["E001", "E005"],
            assumptions=["Coup likely to fail", "Neutrality preserves institution"],
            outcome="Coup failed, military remained intact"
        )
    ]
    
    # Add ACH run
    ach_outputs = {
        'evidence_matrix': {
            'H1': {'E001': -1, 'E002': 1, 'E003': 0, 'E004': 1, 'E005': 0, 'E006': 0},
            'H2': {'E001': 0, 'E002': 1, 'E003': 1, 'E004': -1, 'E005': 0, 'E006': 0},
            'H3': {'E001': 1, 'E002': 0, 'E003': 1, 'E004': 1, 'E005': 1, 'E006': 1},
            'H4': {'E001': 0, 'E002': 0, 'E003': 0, 'E004': 0, 'E005': 0, 'E006': 1},
            'H5': {'E001': 0, 'E002': 0, 'E003': 0, 'E004': 0, 'E005': 0, 'E006': 0}
        },
        'likelihood_scores': {'H1': 0.2, 'H2': 0.3, 'H3': 0.8, 'H4': 0.4, 'H5': 0.1},
        'diagnostic_evidence': ['E001', 'E003', 'E005'],
        'ranked_hypotheses': ['H3', 'H2', 'H4', 'H1', 'H5']
    }
    
    case.add_sat_run(
        sat_type=SATType.ACH,
        inputs={'hypotheses': [h.hypothesis_id for h in case.hypotheses],
                'evidence': [e.evidence_id for e in case.evidence]},
        outputs=ach_outputs,
        confidence=0.8,
        notes="Elite defection hypothesis (H3) strongly supported by evidence"
    )
    
    # Add Red Team run
    red_team_outputs = {
        'challenge': "H3 understates structural constraints on elite choices",
        'alternative_narrative': "Elites had no viable option but to abandon USSR",
        'stress_test_results': {
            'H3_survivability': 0.7,
            'key_vulnerabilities': ['Overstates elite agency', 'Ignores economic constraints'],
            'recommendations': ['Incorporate structural factors', 'Consider constraint analysis']
        }
    }
    
    case.add_sat_run(
        sat_type=SATType.RED_TEAM,
        inputs={'primary_hypothesis': 'H3', 'evidence': ['E001', 'E003', 'E005']},
        outputs=red_team_outputs,
        confidence=0.6,
        notes="Red Team challenge partially successful - H3 robust but needs refinement"
    )
    
    # Add Key Assumptions Check
    kac_outputs = {
        'critical_assumptions': [
            {
                'assumption': 'Elites had choice to preserve USSR',
                'validity': 'Partially Valid',
                'impact': 'High',
                'reasoning': 'Choice existed but constrained by structural factors'
            },
            {
                'assumption': 'Coercive capacity existed without willingness to use',
                'validity': 'Valid',
                'impact': 'Critical',
                'reasoning': 'Military capacity remained but political will absent'
            }
        ],
        'assumption_risk_score': 0.3
    }
    
    case.add_sat_run(
        sat_type=SATType.KAC,
        inputs={'hypothesis': 'H3', 'assumptions': case.hypotheses[2].assumptions},
        outputs=kac_outputs,
        confidence=0.7,
        notes="Key assumptions largely valid, some refinement needed"
    )
    
    # Final assessment
    assessment = Assessment(
        assessment_id="A001",
        key_judgments=[
            "Elite defection was primary driver of Soviet collapse timing",
            "Economic problems were necessary but not sufficient condition",
            "Coercive capacity existed without political will to use force",
            "Gorbachev's reforms accelerated but did not cause collapse"
        ],
        supporting_evidence=['E001', 'E003', 'E005', 'E006'],
        alternative_explanations=[
            "Structural economic determinism",
            "Reform backlash",
            "External pressure success"
        ],
        confidence_level=0.8,
        dissenting_views=[
            "Economic factors remain primary despite elite choices",
            "Reform timeline suggests causation"
        ]
    )
    
    case.assessments.append(assessment)
    
    # Lessons learned
    case.lessons_learned = [
        LessonLearned(
            lesson_id="L001",
            lesson_type=LessonType.STRATEGIC,
            statement="State collapse occurs when elites abandon system preservation",
            transferability=Transferability.HIGH,
            supporting_evidence=['E001', 'E005', 'E006'],
            applicability_context="Authoritarian systems facing economic stress"
        ),
        LessonLearned(
            lesson_id="L002",
            lesson_type=LessonType.ANALYTIC,
            statement="Coercive capacity meaningless without political will to use force",
            transferability=Transferability.HIGH,
            supporting_evidence=['E001', 'E003', 'E005'],
            applicability_context="Regime stability analysis"
        ),
        LessonLearned(
            lesson_id="L003",
            lesson_type=LessonType.ANALYTIC,
            statement="Elite cohesion is critical early warning indicator for regime stability",
            transferability=Transferability.MEDIUM,
            supporting_evidence=['E004', 'E006'],
            applicability_context="Intelligence monitoring of authoritarian systems"
        ),
        LessonLearned(
            lesson_id="L004",
            lesson_type=LessonType.POLITICAL,
            statement="Economic stress creates opportunities but not determinism for political change",
            transferability=Transferability.HIGH,
            supporting_evidence=['E002', 'E003'],
            applicability_context="Political transition analysis"
        )
    ]
    
    return case

def main():
    """Create and validate Soviet Union case study"""
    print("🇷🇺 Creating Soviet Union Case Study using Historical Case Schema...")
    
    # Create case
    ussr_case = create_soviet_union_case()
    
    # Validate schema integrity
    validation = validate_historical_case(ussr_case)
    
    print(f"✅ Case Created: {ussr_case.case_metadata.title}")
    print(f"📊 Case ID: {ussr_case.case_metadata.case_id}")
    print(f"🔍 Evidence Items: {len(ussr_case.evidence)}")
    print(f"🧠 Hypotheses: {len(ussr_case.hypotheses)}")
    print(f"🔬 SAT Runs: {len(ussr_case.sat_runs)}")
    print(f"📋 Assessments: {len(ussr_case.assessments)}")
    print(f"💡 Lessons Learned: {len(ussr_case.lessons_learned)}")
    
    if validation['is_valid']:
        print("✅ Schema validation passed!")
    else:
        print("❌ Schema validation issues:")
        for violation in validation['violations']:
            print(f"  - {violation}")
    
    # Export to JSON
    json_export = ussr_case.export_to_json()
    
    # Save to file
    with open('d:/argus/src/data/ussr_case_hcs.json', 'w', encoding='utf-8') as f:
        f.write(json_export)
    
    print("📄 Case exported to: src/data/ussr_case_hcs.json")
    
    return ussr_case

if __name__ == "__main__":
    ussr_case = main()
