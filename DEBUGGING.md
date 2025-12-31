# Debugging Guide for popLing QGIS Plugin

## Where to Find Logs

### 1. QGIS Message Log (In QGIS UI)
**Location**: View → Panels → Log Messages Panel (or press `Ctrl+Alt+M`)

This shows real-time log messages from the plugin. Messages appear with the tag "popLing".

**How to view:**
1. Open QGIS
2. Go to **View → Panels → Log Messages Panel** (or press `Ctrl+Alt+M`)
3. In the Log Messages panel, filter by "popLing" to see only plugin messages
4. Messages are color-coded: Info (blue), Warning (yellow), Critical (red)

### 2. Debug Log File (NDJSON Format)
**Location**: `c:\Users\{UserName}\Documents\GitHub\popLing\.cursor\debug.log`

This file contains detailed debug information in NDJSON format (one JSON object per line). Each log entry includes:
- `timestamp`: When the log was created
- `location`: File and function where the log was written
- `message`: Description of what happened
- `data`: Additional context (parameters, values, etc.)
- `hypothesisId`: Which debugging hypothesis this log relates to
- `runId`: Which run this log is from

**How to view:**
- Open the file in any text editor
- Each line is a JSON object - you can format it for readability
- Use a JSON viewer or NDJSON parser for better visualization

### 3. QGIS Python Console
**Location**: Plugins → Python Console (or press `Ctrl+Alt+P`)

You can also add custom logging here:
```python
from qgis.core import QgsMessageLog
QgsMessageLog.logMessage("Your message", "popLing", QgsMessageLog.INFO)
```

## How Logging Works

The plugin uses a `debug_log()` function that writes to **both** locations:
1. **QGIS Message Log** - for immediate visibility in QGIS
2. **debug.log file** - for detailed analysis and debugging

## What Gets Logged

The plugin logs:
- **Function entry/exit**: When functions start and end
- **Parameters**: Input values to functions
- **Intermediate values**: Important calculations and state changes
- **Error conditions**: Exceptions and edge cases
- **Progress**: Steps in the point generation process

## Step-by-Step Debugging

### 1. Clear Previous Logs
Before each test run, delete the debug.log file:
- Manually delete: `c:\Users\ZAALANYODER\Documents\GitHub\popLing\.cursor\debug.log`
- Or it will be cleared automatically before each run

### 2. Run the Plugin
1. Open QGIS
2. Load a polygon layer and a raster layer
3. Run the popLing plugin
4. Complete the operation (or let it fail)

### 3. Check Logs
1. **In QGIS**: Open Log Messages Panel (Ctrl+Alt+M) and filter by "popLing"
2. **In file**: Open `debug.log` and review the JSON entries

### 4. Analyze the Flow
Look for these key events in the logs:
- `popLing.run` - Plugin execution started
- `popLing.generate_points_in_polygon` - Point generation started
- `popLing.get_raster_value_at_point` - Raster value retrieval
- Function exits with return values
- Error messages with stack traces

## Reading NDJSON Logs

Each line in `debug.log` is a JSON object. Example:
```json
{"timestamp":1733456789000,"location":"popLing.run","message":"Function entry","data":{"polygon_count":2},"sessionId":"debug-session","runId":"run1","plugin":"popLing"}
```

You can:
- Read line by line to follow execution flow
- Search for specific locations or messages
- Parse with Python:
```python
import json
with open('.cursor/debug.log', 'r') as f:
    for line in f:
        log = json.loads(line)
        print(f"{log['location']}: {log['message']}")
```

## Common Debugging Scenarios

### No Points Generated
Check logs for:
- `generate_points_in_polygon` - Did it find sample points?
- `get_raster_value_at_point` - Are raster values being retrieved?
- Early exit conditions

### Plugin Not Appearing
Check:
- Plugin is in correct directory
- `__init__.py` is correct
- QGIS was restarted after installation

### Errors During Execution
Check:
- Exception logs with full tracebacks
- Parameter values before operations
- Layer validity checks

## Adding Your Own Logs

To add custom logging, use the `debug_log()` function:

```python
from popLing import debug_log

debug_log("your_function", "Your message", {"key": value}, hypothesis_id="X")
```

This will write to both QGIS Message Log and debug.log file.

## Tips

1. **Filter by hypothesisId**: Logs are tagged with hypothesis IDs (A, B, C) to track different debugging hypotheses
2. **Use runId**: Tag different test runs with different runIds to compare behavior
3. **Check timestamps**: Logs are timestamped to see execution timing
4. **Follow the flow**: Start from function entry logs and follow the execution path

