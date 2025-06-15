# Football Simulation 11v11 with Mesa 3.x

A comprehensive football (soccer) simulation built with Mesa 3.x agent-based modeling framework. The simulation models 22 players (11 vs 11) with realistic behaviors and generates detailed event logs in both CSV and XES formats for process mining analysis.

## Features

### Core Simulation
- **11v11 Football Match**: Complete simulation with 22 individual player agents
- **Realistic Player Behavior**: Position-specific attributes and decision-making
- **Dynamic Formations**: Home team (4-4-2) vs Away team (4-3-3)
- **Game Mechanics**: Passing, dribbling, shooting, tackling, possessions
- **Match Events**: Goals, fouls, tackles, interceptions, clearances

### Event Logging
- **Comprehensive Event Tracking**: Every action is logged with full context
- **CSV Export**: Standard format for data analysis
- **XES Export**: Process mining format compatible with PM4Py, ProM, Disco
- **Process Mining Ready**: Designed for tactical analysis and pattern discovery

### Mesa 3.x Compatibility
- Built with the latest Mesa 3.x framework
- Uses new AgentSet functionality instead of deprecated schedulers
- Proper agent initialization and management
- Modern Mesa architecture patterns

## Installation

1. Clone or download the project files
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Run the Demo
```python
python demo.py
```

This will run:
1. A quick 10-minute demo match
2. Event pattern analysis
3. Option to run full 90-minute match
4. Option to run custom match

### Run Individual Match
```python
from football_simulation import run_match

# Run a 90-minute match
model = run_match(duration=90, seed=123, export_logs=True)

# Get match statistics
stats = model.get_match_stats()
print(f"Final Score: Home {stats['home_score']} - {stats['away_score']} Away")
```

### Custom Match Setup
```python
from football_simulation import FootballModel

# Create custom match
model = FootballModel(match_duration=45, seed=456)

# Run simulation
while model.running:
    model.step()

# Export logs
csv_path, xes_path = model.export_logs()
```

## Event Schema

Each event contains the following information:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| possession_id | str | Unique possession identifier | "M1234-P045" |
| timestamp | str | ISO-8601 timestamp | "2025-06-15T10:33:45.231Z" |
| team | str | Team name | "Home" / "Away" |
| player_id | int | Player jersey number | 17 |
| action | str | Action performed | "Pass", "Shot", "Tackle" |
| zone | str | Field zone (A1-D5) | "C3" |
| pressure | int | Pressure indicator (0/1) | 1 |
| team_status | str | Score situation | "Tied", "Home Leading" |
| outcome | str | Action result | "Success" / "Failure" |
| xg_change | float | Expected goals change | 0.05 |

## Actions Logged

### On-ball Actions (Mandatory)
- **Pass**: Player passes the ball to a teammate
- **Dribble**: Player moves with the ball
- **Shot**: Player attempts to score
- **Tackle**: Player attempts to win the ball
- **Clearance**: Defensive clearance
- **Interception**: Player intercepts opponent's pass
- **BallRecovery**: Player gains possession
- **Save**: Goalkeeper saves a shot
- **Foul**: Player commits a foul

### Contextual Events
- **PossessionStart**: New possession begins
- **PossessionEnd**: Possession ends
- **SupportRequest**: Player requests support
- **FormationChange**: Team changes formation
- **Goal**: Goal scored

## Field Zones

The field is divided into a 4x5 grid:
- **Rows**: A (defensive) to D (attacking)
- **Columns**: 1 (left) to 5 (right)
- **Example**: "C3" = center field, middle column

```
   1   2   3   4   5
A [A1][A2][A3][A4][A5]  <- Defensive zone
B [B1][B2][B3][B4][B5]
C [C1][C2][C3][C4][C5]
D [D1][D2][D3][D4][D5]  <- Attacking zone
```

## Player Agents

### Positions
- **Goalkeeper (GK)**: Specialized for shot stopping
- **Defender (DEF)**: Focus on defensive actions
- **Midfielder (MID)**: Balanced, good passing
- **Forward (FWD)**: Specialized for scoring

### Attributes
Each player has attributes (0-100 scale):
- **Speed**: Movement speed
- **Passing**: Passing accuracy and vision
- **Shooting**: Goal scoring ability
- **Defending**: Defensive skills
- **Dribbling**: Ball control and movement
- **Positioning**: Tactical awareness

### Decision Making
Players make decisions based on:
- Their attributes
- Current pressure from opponents
- Field position
- Team situation
- Stamina level

## Process Mining Applications

The generated event logs can be used for:

### Tactical Analysis
- Identify successful attacking patterns
- Analyze possession sequences
- Discover defensive weaknesses
- Compare team strategies

### Performance Analysis
- Player performance metrics
- Zone-based activity analysis
- Success rate analysis by action type
- Pressure impact on performance

### Pattern Discovery
- Common possession flows
- Goal-scoring sequences
- Turnover patterns
- Formation effectiveness

### Tools Compatibility
- **PM4Py**: Python process mining library
- **ProM**: Process mining toolkit
- **Disco**: Commercial process mining tool
- **Celonis**: Process mining platform
- **Any CSV-compatible tool**: Excel, R, Python pandas

## File Structure

```
football_simulation/
├── football_simulation.py    # Main simulation model
├── player_agent.py          # Player agent implementation
├── utils_logger.py          # Event logging utilities
├── demo.py                  # Example usage and demos
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Extending the Simulation

### Adding New Actions
1. Add action to player decision logic in `player_agent.py`
2. Implement action execution method
3. Update event logging

### Modifying Formations
1. Edit team creation in `FootballModel._create_teams()`
2. Adjust player starting positions
3. Update tactical behaviors

### Custom Analysis
1. Access event data via `model.event_logger.events`
2. Use pandas for data analysis
3. Create custom visualization

## Example Analysis

```python
import pandas as pd
from football_simulation import run_match

# Run match
model = run_match(duration=90)

# Load events into DataFrame
df = pd.DataFrame(model.event_logger.events)

# Analyze passing success by zone
passing_stats = df[df['action'] == 'Pass'].groupby('zone')['outcome'].value_counts()

# Calculate xG by team
team_xg = df.groupby('team')['xg_change'].sum()

# Find most active players
player_activity = df.groupby(['team', 'player_id']).size().sort_values(ascending=False)
```

## Future Enhancements

- **Variable formations**: Dynamic formation changes during match
- **Weather conditions**: Impact on player performance
- **Injury system**: Players can get injured
- **Substitutions**: Tactical substitutions
- **Advanced tactics**: Set pieces, offside trap
- **Machine learning**: AI-based tactical decisions
- **3D visualization**: Mesa-based match visualization

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## License

This project is open source. Feel free to use, modify, and distribute.

## Requirements

- Python 3.8+
- Mesa 3.x
- PM4Py 2.7+
- Pandas 2.0+
- NumPy 1.24+

## Support

For questions or issues:
1. Check the demo.py file for usage examples
2. Review the event logs for data structure
3. Consult Mesa 3.x documentation for framework details
