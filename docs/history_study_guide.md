# History Study Module - User Guide

## Overview

The History Study module transforms Argus into a powerful historical research and analysis platform. It leverages Argus's entity resolution, knowledge graph, and visualization capabilities to provide comprehensive tools for studying history.

## Features

### 📚 Core Capabilities

- **Historical Entity Management**: Track people, organizations, events, and periods
- **Timeline Visualization**: Interactive timelines with filtering and exploration
- **Relationship Analysis**: Discover connections between historical entities
- **Causal Chain Analysis**: Trace cause-and-effect relationships between events
- **Comparative Analysis**: Compare historical figures, events, and periods
- **Source Management**: Track and evaluate historical sources
- **Geospatial Analysis**: Map historical events and movements
- **Research Tools**: Advanced search and analysis capabilities

### 🎯 Use Cases

- **Academic Research**: Support historical research projects
- **Education**: Interactive learning tools for history students
- **Genealogy**: Track family histories and connections
- **Historical Consulting**: Professional historical analysis
- **Personal Study**: Organize personal historical interests

## Getting Started

### 1. Access the History Module

1. Start Argus: `streamlit run src/ui/app.py`
2. Navigate to **History Study** in the sidebar
3. Choose your starting page from the dropdown menu

### 2. Load Sample Data

To explore the features immediately, load the sample dataset:

```bash
python scripts/import_history_data.py sample
```

This will populate the system with:
- 3 historical periods (Ancient Egypt, Classical Greece, Industrial Revolution)
- 3 historical figures (Cleopatra, Socrates, James Watt)
- 3 historical events (Battle of Actium, Peloponnesian War, Steam Engine Patent)

## Module Pages

### 📊 History Dashboard

The main overview page providing:
- **Statistics**: Total counts of events, figures, organizations, and periods
- **Quick Actions**: Fast access to create timelines, add figures, and add events
- **Event Distribution**: Visual breakdown of events by type
- **Recent Events**: Latest historical entries in the system

### 📅 Timeline Viewer

Interactive timeline exploration:
- **Timeline Selection**: Choose from available timelines
- **Visual Timeline**: Plotly-based interactive timeline visualization
- **Event Details**: Click events to view comprehensive information
- **Filtering**: Filter by date ranges and event types

### 👤 Figure Explorer

Historical figures database:
- **Search & Filter**: Find figures by name, era, or occupation
- **Detailed Profiles**: Comprehensive biographical information
- **Contemporaries**: Discover figures who lived during the same time
- **Influence Analysis**: Measure historical impact and connections

### ⚔️ Event Analyzer

Deep dive into historical events:
- **Event Browser**: Filter events by type, location, or time period
- **Causal Analysis**: Trace chains of cause and effect
- **Related Events**: Find connected events by participants or location
- **Significance Assessment**: Evaluate historical importance

### 🏛️ Period Browser

Historical periods overview:
- **Period Information**: Key characteristics and timeframes
- **Events in Period**: All events occurring within specific periods
- **Regional Focus**: Geographic and cultural contexts
- **Period Connections**: Relationships between different historical periods

### 🔍 Research Tools

Advanced analysis capabilities:

#### Keyword Search
Search across all historical entities:
- Cross-entity search functionality
- Relevance-ranked results
- Multiple entity type support

#### Temporal Network Analysis
Analyze relationships within time periods:
- Network visualization
- Connection strength metrics
- Component analysis

#### Comparative Analysis
Compare historical entities:
- Side-by-side figure comparisons
- Event relationship analysis
- Period characteristic comparison

#### Source Management
Track historical sources:
- Source reliability scoring
- Citation management
- Primary/secondary source classification

## Data Models

### Historical Events
- **Title & Description**: Event details
- **Date Range**: Start and end dates
- **Location**: Geographic information with coordinates
- **Participants**: People and organizations involved
- **Causal Links**: Causes and consequences
- **Sources**: Historical references
- **Tags**: Categorization and search terms

### Historical Figures
- **Biographical Information**: Birth, death, locations
- **Occupations & Roles**: Professional and social positions
- **Achievements**: Major accomplishments
- **Relationships**: Connections to other figures
- **Affiliations**: Organizational memberships
- **Era Classification**: Historical time periods

### Historical Organizations
- **Organizational Type**: Kingdoms, empires, institutions
- **Temporal Information**: Founding and dissolution dates
- **Geographic Scope**: Territories and regions
- **Leadership**: Key figures and succession
- **Conflicts & Achievements**: Major historical impacts

### Historical Periods
- **Temporal Boundaries**: Start and end dates
- **Period Classification**: Ancient, classical, medieval, etc.
- **Regional Focus**: Geographic areas
- **Key Characteristics**: Defining features
- **Related Periods**: Preceding and succeeding periods

## Importing Data

### CSV Import

Create CSV files with appropriate headers:

#### Events CSV
```csv
title,description,event_type,date,end_date,location,participants,significance,tags
Battle of Actium,Final war of the Roman Republic,military,-0031-09-02,,Ionian Sea,"Augustus;Cleopatra",End of Roman Republic,"roman;civil war"
```

#### Figures CSV
```csv
name,birth_date,death_date,occupation,era,biography
Cleopatra VII,-0069-01-01,-0030-01-01,"Pharaoh;Queen",Ancient Egypt,Last ruler of Ptolemaic Egypt
```

#### Organizations CSV
```csv
name,organization_type,founded_date,dissolved_date,headquarters,leaders
Roman Empire,empire,-0027-01-01,0476-01-01,Rome,"Augustus;Constantine"
```

#### Periods CSV
```csv
name,description,start_date,end_date,period_type,region,key_characteristics
Ancient Egypt,Period of ancient Egyptian civilization,-3100-01-01,0030-01-01,ancient,North Africa,"Pyramids;Hieroglyphs"
```

Import using:
```bash
python scripts/import_history_data.py csv --file events.csv --type events
```

### JSON Import

Structured JSON format:
```json
{
  "events": [
    {
      "title": "Battle of Actium",
      "description": "Final war of the Roman Republic",
      "event_type": "military",
      "date": "-0031-09-02",
      "location": "Ionian Sea",
      "significance": "End of Roman Republic",
      "tags": ["roman", "civil war"]
    }
  ],
  "figures": [
    {
      "name": "Cleopatra VII",
      "birth_date": "-0069-01-01",
      "death_date": "-0030-01-01",
      "occupation": ["Pharaoh", "Queen"],
      "era": "Ancient Egypt",
      "biography": "Last ruler of Ptolemaic Egypt"
    }
  ]
}
```

Import using:
```bash
python scripts/import_history_data.py json --file history_data.json
```

## API Usage

The history module provides REST API endpoints for programmatic access:

### Events
- `POST /api/history/events` - Create event
- `GET /api/history/events` - List events
- `GET /api/history/events/{id}` - Get specific event
- `GET /api/history/events/{id}/causal-chains` - Get causal chains

### Figures
- `POST /api/history/figures` - Create figure
- `GET /api/history/figures` - List figures
- `GET /api/history/figures/{id}` - Get specific figure
- `GET /api/history/figures/{id}/contemporaries` - Get contemporaries
- `GET /api/history/figures/{id}/influence` - Get influence analysis

### Organizations
- `POST /api/history/organizations` - Create organization
- `GET /api/history/organizations` - List organizations
- `GET /api/history/organizations/{id}` - Get specific organization

### Periods
- `POST /api/history/periods` - Create period
- `GET /api/history/periods/{id}/events` - Get events in period

### Timelines
- `POST /api/history/timelines` - Create timeline
- `GET /api/history/timelines/{id}/events` - Get timeline events

### Analysis
- `GET /api/history/search?keyword={term}` - Search entities
- `POST /api/history/temporal-network` - Create temporal network
- `GET /api/history/statistics` - Get database statistics

## Best Practices

### Data Entry
1. **Consistent Dating**: Use ISO format (YYYY-MM-DD) for all dates
2. **Standardized Naming**: Use consistent naming conventions
3. **Source Attribution**: Always include source information
4. **Tagging Strategy**: Develop consistent tagging system
5. **Relationship Accuracy**: Verify causal connections carefully

### Research Workflow
1. **Start Broad**: Begin with period or timeline exploration
2. **Focus Down**: Use filters to narrow to specific interests
3. **Follow Connections**: Explore related entities and events
4. **Verify Sources**: Cross-reference information with multiple sources
5. **Document Findings**: Use notes and annotations extensively

### Analysis Techniques
1. **Temporal Analysis**: Look for patterns across time periods
2. **Geographic Analysis**: Map events to understand spatial relationships
3. **Network Analysis**: Identify key figures and their connections
4. **Comparative Studies**: Compare similar events or figures
5. **Causal Mapping**: Trace chains of cause and effect

## Troubleshooting

### Common Issues

**Date Format Errors**
- Ensure all dates use ISO format (YYYY-MM-DD)
- For BCE dates, use negative years (e.g., -0470 for 470 BCE)

**Missing Relationships**
- Verify entity IDs when creating connections
- Use the search function to find correct entity references

**Import Failures**
- Check CSV headers match expected format
- Validate JSON structure before importing
- Ensure required fields are present

**Performance Issues**
- Use date range filters for large datasets
- Limit search results with specific keywords
- Clear browser cache if interface becomes slow

### Getting Help

1. **Check Documentation**: Review this guide and API documentation
2. **Validate Data**: Ensure data formats are correct
3. **Use Sample Data**: Test with sample dataset first
4. **Check Logs**: Review error messages for specific issues
5. **Community Support**: Reach out through project channels

## Advanced Features

### Custom Analysis

Create custom analysis scripts using the HistoryEngine:

```python
from src.core.history_engine import HistoryEngine

engine = HistoryEngine()

# Find all military events in a period
military_events = engine.find_events_by_type(EventType.MILITARY)

# Analyze influence networks
for figure_id in engine.figures:
    influence = engine.analyze_influence_network(figure_id)
    print(f"Figure {figure_id}: Influence score {influence['influence_score']}")
```

### Integration with Other Modules

The history module integrates with Argus's core features:
- **Entity Resolution**: Identify duplicate historical figures
- **Graph Visualization**: Visualize complex historical networks
- **Geospatial Analysis**: Map historical events and movements
- **Temporal Analysis**: Analyze patterns over time

## Future Enhancements

Planned improvements include:
- **Machine Learning**: Automated pattern recognition
- **Natural Language Processing**: Text analysis of historical documents
- **Collaborative Features**: Multi-user research support
- **Advanced Visualization**: 3D timelines and interactive maps
- **Integration APIs**: Connect to external historical databases

---

This guide provides comprehensive coverage of the History Study module. For specific technical questions or API documentation, refer to the source code and inline documentation.
