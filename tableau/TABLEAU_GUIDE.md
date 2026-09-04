# Tableau Dashboard Design Guide — EarthScape Climate Agency

This guide explains how to connect and build interactive BI visualizations in **Tableau Desktop / Tableau Public** using the dataset exported from EarthScape Climate Agency.

---

## 1. Data Connection
1. Open **Tableau Desktop** or **Tableau Public**.
2. Select **Connect to Data** -> **Text File**.
3. Choose `d:/climate/tableau/earthscape_tableau_dataset.csv`.
4. Verify field data types:
   - `StartTime(UTC)`, `EndTime(UTC)`: **Date & Time**
   - `LocationLat`: **Geographic Role -> Latitude**
   - `LocationLng`: **Geographic Role -> Longitude**
   - `State`: **Geographic Role -> State/Province**
   - `Precipitation(in)`, `DurationHours`, `SeverityScore`: **Continuous Measure (Number)**
   - `Type`, `Severity`, `Season`: **Dimension (String)**

---

## 2. Dashboard Worksheets & Visualizations

### Sheet 1: Key Performance Metrics (KPI Cards)
- **Total Weather Events**: `COUNT([EventId])`
- **Severe Events Count**: `COUNT(IF [Severity] = 'Severe' OR [Severity] = 'Heavy' THEN [EventId] END)`
- **Average Precipitation**: `AVG([Precipitation(in)])`
- **Average Event Duration**: `AVG([DurationHours])`

### Sheet 2: Yearly Weather Event Trends
- **Columns**: `YEAR([StartTime(UTC)])`
- **Rows**: `COUNT([EventId])`
- **Color**: `[Severity]`
- **Mark Type**: Line Chart with Data Points

### Sheet 3: Event Type & Severity Matrix
- **Columns**: `[Type]`
- **Rows**: `COUNT([EventId])`
- **Color**: `[Severity]` (Palette: Green -> Amber -> Red)
- **Mark Type**: Stacked Bar Chart

### Sheet 4: Geographic Heatmap / Symbol Map
- **Columns**: `[LocationLng]` (Avg)
- **Rows**: `[LocationLat]` (Avg)
- **Detail**: `[State]`, `[City]`
- **Size**: `COUNT([EventId])`
- **Color**: `AVG([Precipitation(in)])` or `[Severity]`
- **Mark Type**: Density Heatmap or Circle Symbol Map

### Sheet 5: Monthly & Seasonal Heatmap
- **Columns**: `[Month]` (1 to 12)
- **Rows**: `[Type]`
- **Color**: `COUNT([EventId])` (Sequential Palette)
- **Mark Type**: Square / Heatmap

---

## 3. Interactive Filters & Dashboard Actions
1. **Interactive Global Filters**:
   - `State` (Dropdown List with Search)
   - `Year` (Slider / Range Filter)
   - `Weather Type` (Multi-select Checkboxes)
   - `Severity Level` (Buttons / Multi-select)
2. **Dashboard Filter Actions**:
   - Selecting a State on the Map filters the Event Type and Trend charts automatically.
