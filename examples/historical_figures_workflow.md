# Historical Figures Network Analysis Workflow

## 📋 Overview
This workflow demonstrates how to use Argus MVP to study connections between historical figures using biographical data.

## 🎯 Use Case
Study relationships between historical figures (politicians, scientists, artists, etc.) to uncover hidden networks and influence patterns.

## 📊 Step-by-Step Workflow

### Step 1: Prepare Biographical Data

#### Required CSV Format
Create a CSV file with the following structure:

```csv
id,name,type,birth_year,death_year,profession,country,description,source
person_001,Albert Einstein,Scientist,1879,1955,Germany,Theoretical physicist,Biography.com
person_002,Marie Curie,Scientist,1867,1934,Poland,Physicist and chemist,Nobel.org
person_003,Nikola Tesla,Inventor,1856,1943,Serbia-American,Electrical engineer,Tesla Museum
person_004,Thomas Edison,Inventor,1847,1931,American,Businessman and inventor,Edison Museum
person_005,Leonardo da Vinci,Artist,1452,1519,Italian,Polymath,Renaissance Archives
```

#### Sample Data Fields
- **id**: Unique identifier
- **name**: Full name of the historical figure
- **type**: Entity type (person, organization, location, event)
- **birth_year**: Year of birth
- **death_year**: Year of death
- **profession**: Primary profession/field
- **country**: Country of origin/primary work
- **description**: Brief biographical description
- **source**: Source of the information

### Step 2: Import Data into Argus

1. **Start Argus MVP**:
   ```bash
   python start_all.py
   ```

2. **Navigate to Data Import**:
   - Open http://localhost:8501
   - Click "Data Import" in the sidebar

3. **Upload Your CSV**:
   - Click "Choose File" and select your biographical CSV
   - Review the data preview
   - Click "Import Data"

4. **Verify Import**:
   - Check the import summary
   - Navigate to "Dashboard" to see entity counts

### Step 3: Create Relationships Manually

#### Relationship Types to Consider
- **collaborated_with**: Worked together on projects
- **influenced_by**: Mentored or inspired
- **contemporary_of**: Lived during same time period
- **worked_in**: Same organization or location
- **competed_with**: Rivals or competitors
- **married_to**: Family relationships
- **student_of**: Teacher-student relationships

#### Manual Relationship Creation
1. **Navigate to Graph Explorer**:
   - Go to http://localhost:8501
   - Select "Graph Explorer" from sidebar

2. **Add Relationships**:
   - Use the "Add Relationship" feature
   - Select source entity (historical figure)
   - Select target entity (another historical figure)
   - Choose relationship type
   - Add relationship attributes (years, context, source)

3. **Example Relationships**:
   ```
   Einstein → collaborated_with → Curie
   Tesla → competed_with → Edison
   da Vinci → influenced_by → Renaissance Masters
   Curie → contemporary_of → Einstein
   ```

### Step 4: Visualize Network Connections

#### Advanced Graph Explorer
1. **Navigate to "Advanced Graph Explorer"**:
   - Use the enhanced visualization tools
   - Apply layout algorithms (force-directed, circular)

2. **Filter and Analyze**:
   - Filter by profession (scientists, artists, politicians)
   - Filter by time period (century, decade)
   - Filter by country or region

3. **Network Analysis**:
   - Identify central figures (high betweenness centrality)
   - Find clusters (profession-based groups)
   - Discover shortest paths between figures

#### Visualization Options
- **Plotly Interactive**: 2D/3D network with zoom/pan
- **PyVis Network**: Force-directed with physics simulation
- **Statistical Charts**: Distribution by profession, time period

### Step 5: Export Graph for External Analysis

#### Export Options
1. **Navigate to Network Metrics**:
   - Go to http://localhost:8501
   - Select "Network Metrics" from sidebar

2. **Export Formats**:
   - **GraphML**: For Gephi or NetworkX analysis
   - **JSON**: For custom processing
   - **CSV**: For spreadsheet analysis
   - **PNG/SVG**: For presentations

3. **Export Process**:
   - Click "Export Graph Data"
   - Choose format
   - Download file

#### External Analysis Tools
- **Gephi**: Advanced network visualization and analysis
- **Cytoscape**: Complex network analysis
- **R/Python**: Custom statistical analysis
- **Palladio**: Historical network analysis

## 🔍 Analysis Techniques

### Centrality Analysis
- **Degree Centrality**: Most connected figures
- **Betweenness Centrality**: Bridge figures between groups
- **Closeness Centrality**: Figures closest to all others
- **Eigenvector Centrality**: Influential figures in networks

### Community Detection
- **Profession-based clusters**: Scientists, artists, politicians
- **Time-based clusters**: Historical periods
- **Geographic clusters**: Regional networks
- **Influence networks**: Mentor-student chains

### Temporal Analysis
- **Timeline Visualization**: When relationships formed
- **Generational Analysis**: Influence across time periods
- **Historical Context**: Major events and their impact

## 📈 Advanced Features

### Enhanced Entity Resolution
- **Duplicate Detection**: Find same person with different names
- **Name Variations**: "Albert Einstein" vs "A. Einstein"
- **Attribute Matching**: Same birth year, profession, location

### Collaboration Workspaces
- **Shared Case Files**: Multiple analysts working together
- **Annotations**: Add notes and evidence to relationships
- **Hypothesis Testing**: Propose and test network theories

### Source Traceability
- **Document Linking**: Connect relationships to historical sources
- **Confidence Scoring**: Rate reliability of connections
- **Audit Trail**: Track who added what and when

## 🎯 Sample Research Questions

### Network Structure
1. Who are the most influential scientists in the network?
2. Are there distinct clusters by profession or nationality?
3. Which figures serve as bridges between different communities?

### Historical Patterns
1. How did scientific collaboration evolve over time?
2. Are there patterns of mentorship across generations?
3. How do political networks differ from scientific networks?

### Individual Analysis
1. What is the "six degrees of separation" between any two figures?
2. Who were the key influencers in specific historical periods?
3. Are there previously unknown connections between famous figures?

## 🚀 Getting Started

### Quick Start Template
```bash
# 1. Start Argus
python start_all.py

# 2. Open browser to localhost:8501
# 3. Upload your historical figures CSV
# 4. Manually add known relationships
# 5. Visualize and analyze
# 6. Export for external tools
```

### Sample CSV Template
Download the template file: `examples/historical_figures_template.csv`

```csv
id,name,type,birth_year,death_year,profession,country,description,source
template_1,Example Person,person,1900,2000,Scientist,Example Country,Example description,Example source
```

## 📚 Resources

### Historical Data Sources
- **Wikipedia**: Biographical information and relationships
- **Biography.com**: Professional biographies
- **Academic Databases**: Citation networks and collaborations
- **Government Archives**: Political and diplomatic records
- **Museum Collections**: Artist and inventor information

### Network Analysis References
- **"Networks, Crowds, and Markets"**: Network theory fundamentals
- **Historical Network Analysis**: Academic methodologies
- **Social Network Analysis**: Techniques and tools
- **Digital Humanities**: Computational approaches to history

---

## 🎉 Success Metrics

Your historical figures network analysis is successful when you can:

✅ **Import biographical data** without errors  
✅ **Create meaningful relationships** between figures  
✅ **Visualize network structure** clearly  
✅ **Identify key influencers** and bridges  
✅ **Discover hidden patterns** and connections  
✅ **Export data** for further analysis  
✅ **Document findings** with source references  

This workflow transforms static biographical data into dynamic, analyzable networks that reveal hidden historical connections and influence patterns.
