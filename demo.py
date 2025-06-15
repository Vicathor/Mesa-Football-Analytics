"""
Football Simulation Example
Demonstrates the 11v11 football simulation with comprehensive event logging
"""

import os
import sys
from datetime import datetime
from football_simulation import run_match, FootballModel
from utils_logger import EventLogger


def run_full_match_example():
    """Run a full 90-minute football match"""
    print("="*60)
    print("FOOTBALL SIMULATION - FULL MATCH")
    print("="*60)
    
    # Run full match
    model = run_match(duration=90, seed=123, export_logs=True)
    
    # Display comprehensive results
    stats = model.get_match_stats()
    
    print(f"\n{'='*20} MATCH RESULTS {'='*20}")
    print(f"Match ID: {stats['match_id']}")  
    print(f"Final Score: Home {stats['home_score']} - {stats['away_score']} Away")
    print(f"Match Duration: {stats['duration_minutes']:.1f} minutes")
    print(f"Total Events Logged: {stats['total_events']}")
    print(f"Total Possessions: {stats['possessions']}")
    
    # Event breakdown
    print(f"\n{'='*20} EVENT BREAKDOWN {'='*20}")
    event_summary = stats['event_summary']
    actions = event_summary.get('actions', {})
    
    # Sort actions by frequency
    sorted_actions = sorted(actions.items(), key=lambda x: x[1], reverse=True)
    
    for action, count in sorted_actions:
        percentage = (count / stats['total_events']) * 100
        print(f"{action:15}: {count:4d} ({percentage:5.1f}%)")
    
    # Team breakdown
    print(f"\n{'='*20} TEAM ACTIVITY {'='*20}")
    teams = event_summary.get('teams', {})
    for team, count in teams.items():
        percentage = (count / stats['total_events']) * 100
        print(f"{team:10}: {count:4d} events ({percentage:5.1f}%)")
    
    return model


def run_short_demo():
    """Run a short demo match for quick testing"""
    print("="*60)
    print("FOOTBALL SIMULATION - QUICK DEMO (10 minutes)")
    print("="*60)
    
    model = run_match(duration=10, seed=456, export_logs=True)
    
    # Show some detailed events
    if model.event_logger.events:
        print(f"\n{'='*20} SAMPLE EVENTS {'='*20}")
        sample_events = model.event_logger.events[:10]  # First 10 events
        
        for event in sample_events:
            print(f"T{event['team'][0]} #{event['player_id']:2d} {event['action']:12} "
                  f"in {event['zone']} -> {event['outcome']} "
                  f"(xG: {event['xg_change']:+.3f})")
    
    return model


def analyze_event_patterns(model: FootballModel):
    """Analyze patterns in the event data"""
    print(f"\n{'='*20} EVENT PATTERN ANALYSIS {'='*20}")
    
    events = model.event_logger.events
    if not events:
        print("No events to analyze")
        return
    
    # Analyze by zone
    zone_activity = {}
    for event in events:
        zone = event.get('zone', 'Unknown')
        if zone not in zone_activity:
            zone_activity[zone] = 0
        zone_activity[zone] += 1
    
    print("\nActivity by Zone:")
    sorted_zones = sorted(zone_activity.items(), key=lambda x: x[1], reverse=True)
    for zone, count in sorted_zones[:10]:  # Top 10 zones
        print(f"  {zone}: {count:3d} events")
    
    # Analyze success rates
    action_outcomes = {}
    for event in events:
        action = event.get('action', 'Unknown')
        outcome = event.get('outcome', 'Unknown')
        
        if action not in action_outcomes:
            action_outcomes[action] = {'Success': 0, 'Failure': 0, 'Total': 0}
        
        action_outcomes[action][outcome] = action_outcomes[action].get(outcome, 0) + 1
        action_outcomes[action]['Total'] += 1
    
    print("\nSuccess Rates by Action:")
    for action, outcomes in action_outcomes.items():
        total = outcomes['Total']
        success = outcomes.get('Success', 0)
        if total > 0:
            success_rate = (success / total) * 100
            print(f"  {action:15}: {success:3d}/{total:3d} ({success_rate:5.1f}%)")
    
    # Analyze xG accumulation
    home_xg = sum(event.get('xg_change', 0) for event in events if event.get('team') == 'Home')
    away_xg = sum(event.get('xg_change', 0) for event in events if event.get('team') == 'Away')
    
    print(f"\nExpected Goals (xG):")
    print(f"  Home: {home_xg:+.3f}")
    print(f"  Away: {away_xg:+.3f}")


def demonstrate_process_mining_setup():
    """Demonstrate how the logs can be used for process mining"""
    print(f"\n{'='*20} PROCESS MINING SETUP {'='*20}")
    
    print("The simulation generates event logs in two formats:")
    print("\n1. CSV Format:")
    print("   - Standard CSV with all event attributes")
    print("   - Can be imported into any data analysis tool")
    print("   - Columns: possession_id, timestamp, team, player_id, action, zone, pressure, team_status, outcome, xg_change")
    
    print("\n2. XES Format:")
    print("   - Standard format for process mining tools")
    print("   - Compatible with PM4Py, ProM, Disco, Celonis, etc.")
    print("   - Each possession is a 'case' with multiple events")
    print("   - Attributes include player, team, zone, outcome, xG change")
    
    print("\n3. Process Mining Applications:")
    print("   - Analyze possession patterns and sequences")
    print("   - Identify successful vs unsuccessful attack patterns")
    print("   - Discover tactical patterns by team/player")
    print("   - Performance analysis and bottleneck identification")
    print("   - Compare different formations or strategies")
    
    print("\n4. Example Analysis Questions:")
    print("   - What action sequences lead to goals?")
    print("   - Which zones are most important for scoring?")
    print("   - How does pressure affect player performance?")
    print("   - What are the most common possession patterns?")
    print("   - How do different formations affect gameplay?")


def create_custom_match():
    """Create a custom match with specific parameters"""
    print("="*60)
    print("CUSTOM FOOTBALL MATCH")
    print("="*60)
    
    # Create model with custom parameters
    model = FootballModel(match_duration=20, seed=789)
    
    print(f"Created custom match: {model.match_id}")
    print(f"Teams: {len([a for a in model.agents if a.team == 'Home'])} vs {len([a for a in model.agents if a.team == 'Away'])}")
    
    # Run for specific number of steps
    steps = 0
    max_steps = 200  # Run for 200 steps
    
    print(f"Running {max_steps} simulation steps...")
    
    while model.running and steps < max_steps:
        model.step()
        steps += 1
        
        # Show progress every 50 steps
        if steps % 50 == 0:
            print(f"Step {steps}: Minute {model.current_minute:.1f}, Score: {model.home_score}-{model.away_score}")
    
    # Export logs
    csv_path, xes_path = model.export_logs("custom_match")
    
    return model


if __name__ == "__main__":
    print("Football Simulation with Mesa 3.x")
    print("Generates event logs for Process Mining")
    print("="*60)
    
    try:
        # 1. Run quick demo
        print("\n1. Running quick demo...")
        demo_model = run_short_demo()
        
        # 2. Analyze patterns
        analyze_event_patterns(demo_model)
        
        # 3. Show process mining info
        demonstrate_process_mining_setup()
        
        # 4. Ask user if they want to run full match
        print("\n" + "="*60)
        response = input("Would you like to run a full 90-minute match? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            full_model = run_full_match_example()
            analyze_event_patterns(full_model)
        else:
            print("Skipping full match.")
        
        # 5. Custom match option
        print("\n" + "="*60)
        response = input("Would you like to run a custom match? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            custom_model = create_custom_match()
            analyze_event_patterns(custom_model)
        
        print("\n" + "="*60)
        print("Simulation complete!")
        print("Check the generated CSV and XES files for process mining analysis.")
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nError during simulation: {e}")
        import traceback
        traceback.print_exc()
