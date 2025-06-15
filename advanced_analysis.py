"""
Advanced Football Simulation Analysis
Demonstrates advanced usage and analysis capabilities
"""

import pandas as pd
import numpy as np
from football_simulation import run_match, FootballModel
from utils_logger import EventLogger


def analyze_match_performance():
    """Run a match and perform detailed performance analysis"""
    print("="*60)
    print("ADVANCED FOOTBALL SIMULATION ANALYSIS")
    print("="*60)
    
    # Run a medium-length match
    model = run_match(duration=30, seed=999, export_logs=False)
    
    # Convert events to DataFrame for analysis
    df = pd.DataFrame(model.event_logger.events)
    
    print(f"\n{'='*20} ADVANCED STATISTICS {'='*20}")
    
    # 1. Zone-based heat map analysis
    print("\n1. Zone Activity Heatmap:")
    if not df.empty:
        zone_activity = df['zone'].value_counts()
        
        # Create a grid representation
        zones = ['A1', 'A2', 'A3', 'A4', 'A5',
                'B1', 'B2', 'B3', 'B4', 'B5', 
                'C1', 'C2', 'C3', 'C4', 'C5',
                'D1', 'D2', 'D3', 'D4', 'D5']
        
        print("   1    2    3    4    5")
        for row in ['A', 'B', 'C', 'D']:
            line = f"{row} "
            for col in ['1', '2', '3', '4', '5']:
                zone = row + col
                count = zone_activity.get(zone, 0)
                line += f"{count:4d} "
            print(line)
    
    # 2. Player performance analysis
    print(f"\n2. Top Performers:")
    if not df.empty:
        player_stats = df.groupby(['team', 'player_id']).agg({
            'action': 'count',
            'outcome': lambda x: (x == 'Success').sum(),
            'xg_change': 'sum'
        }).round(3)
        player_stats['success_rate'] = (player_stats['outcome'] / player_stats['action'] * 100).round(1)
        player_stats = player_stats.sort_values('action', ascending=False)
        
        print("Top 10 Most Active Players:")
        print("Team Player Actions Success% xG_Total")
        for idx, row in player_stats.head(10).iterrows():
            team, player = idx
            print(f"{team:4} #{player:2d}    {row['action']:4d}    {row['success_rate']:5.1f}%   {row['xg_change']:+7.3f}")
    
    # 3. Tactical analysis
    print(f"\n3. Tactical Analysis:")
    if not df.empty:
        # Action effectiveness by pressure
        pressure_analysis = df.groupby(['action', 'pressure'])['outcome'].apply(
            lambda x: (x == 'Success').mean() * 100
        ).round(1)
        
        print("Action Success Rates by Pressure:")
        actions_under_analysis = ['Pass', 'Dribble', 'Shot']
        for action in actions_under_analysis:
            if action in df['action'].values:
                no_pressure = pressure_analysis.get((action, 0), 0)
                with_pressure = pressure_analysis.get((action, 1), 0)
                print(f"{action:10}: No Pressure {no_pressure:5.1f}%, With Pressure {with_pressure:5.1f}%")
    
    # 4. Possession analysis
    print(f"\n4. Possession Analysis:")
    if not df.empty:
        possession_events = df[df['action'].isin(['PossessionStart', 'PossessionEnd'])]
        possession_lengths = []
        
        current_possession = None
        possession_count = 0
        
        for _, event in possession_events.iterrows():
            if event['action'] == 'PossessionStart':
                current_possession = event['possession_id']
                possession_count = 0
            elif event['action'] == 'PossessionEnd' and current_possession:
                # Count events in this possession
                possession_events_count = len(df[df['possession_id'] == current_possession])
                possession_lengths.append(possession_events_count)
        
        if possession_lengths:
            avg_possession = np.mean(possession_lengths)
            print(f"Average possession length: {avg_possession:.1f} events")
            print(f"Shortest possession: {min(possession_lengths)} events")
            print(f"Longest possession: {max(possession_lengths)} events")
    
    # 5. Expected Goals analysis
    print(f"\n5. Expected Goals (xG) Analysis:")
    if not df.empty:
        home_xg = df[df['team'] == 'Home']['xg_change'].sum()
        away_xg = df[df['team'] == 'Away']['xg_change'].sum()
        
        shots_home = len(df[(df['team'] == 'Home') & (df['action'] == 'Shot')])
        shots_away = len(df[(df['team'] == 'Away') & (df['action'] == 'Shot')])
        
        goals_home = model.home_score
        goals_away = model.away_score
        
        print(f"Home Team: {goals_home} goals from {shots_home} shots (xG: {home_xg:+.3f})")
        print(f"Away Team: {goals_away} goals from {shots_away} shots (xG: {away_xg:+.3f})")
        
        if shots_home > 0:
            print(f"Home conversion rate: {goals_home/shots_home*100:.1f}%")
        if shots_away > 0:
            print(f"Away conversion rate: {goals_away/shots_away*100:.1f}%")
    
    return model, df


def demonstrate_process_mining_analysis():
    """Demonstrate how to use the data for process mining"""
    print(f"\n{'='*20} PROCESS MINING DEMONSTRATION {'='*20}")
    
    # Create a short match for demonstration
    model = FootballModel(match_duration=5, seed=123)
    
    # Run simulation
    while model.running and model.current_minute < 5:
        model.step()
    
    df = pd.DataFrame(model.event_logger.events)
    
    if df.empty:
        print("No events generated for analysis")
        return
    
    print("\n1. Process Discovery - Most Common Sequences:")
    
    # Find sequences of actions within possessions
    sequences = {}
    for possession_id in df['possession_id'].unique():
        possession_events = df[df['possession_id'] == possession_id].sort_values('timestamp')
        actions = possession_events['action'].tolist()
        
        # Create 2-grams (sequences of 2 actions)
        for i in range(len(actions) - 1):
            seq = f"{actions[i]} → {actions[i+1]}"
            sequences[seq] = sequences.get(seq, 0) + 1
    
    # Show top sequences
    sorted_sequences = sorted(sequences.items(), key=lambda x: x[1], reverse=True)
    print("Top action sequences:")
    for seq, count in sorted_sequences[:10]:
        print(f"  {seq}: {count} times")
    
    print("\n2. Goal-Scoring Process Analysis:")
    
    # Find possessions that led to goals
    goal_possessions = df[df['action'] == 'Goal']['possession_id'].unique()
    
    print(f"Found {len(goal_possessions)} goal-scoring possessions")
    
    for goal_poss in goal_possessions[:3]:  # Show first 3
        goal_sequence = df[df['possession_id'] == goal_poss].sort_values('timestamp')
        print(f"\nGoal in {goal_poss}:")
        for _, event in goal_sequence.iterrows():
            if event['action'] != 'Goal':
                outcome_symbol = "✓" if event['outcome'] == 'Success' else "✗"
                print(f"  {event['team']} #{event['player_id']:2d}: {event['action']:12} in {event['zone']} {outcome_symbol}")
            else:
                print(f"  ⚽ GOAL by {event['team']} #{event['player_id']} in {event['zone']}")
    
    print("\n3. Performance Bottlenecks:")
    
    # Find actions with low success rates
    action_success = df.groupby('action').agg({
        'outcome': [lambda x: (x == 'Success').mean(), 'count']
    }).round(3)
    action_success.columns = ['success_rate', 'total_attempts']
    action_success = action_success[action_success['total_attempts'] >= 3]  # Min 3 attempts
    action_success = action_success.sort_values('success_rate')
    
    print("Actions with lowest success rates:")
    for action, row in action_success.head(5).iterrows():
        print(f"  {action:15}: {row['success_rate']*100:5.1f}% ({row['total_attempts']} attempts)")


def compare_formations_simulation():
    """Simulate different scenarios for comparison"""
    print(f"\n{'='*20} FORMATION COMPARISON SIMULATION {'='*20}")
    
    print("Running multiple short matches to compare performance...")
    
    results = []
    
    for i in range(5):
        model = FootballModel(match_duration=10, seed=i*100)
        
        while model.running:
            model.step()
        
        stats = model.get_match_stats()
        results.append({
            'match': i+1,
            'home_score': stats['home_score'],
            'away_score': stats['away_score'],
            'total_events': stats['total_events'],
            'possessions': stats['possessions']
        })
    
    print("\nMatch Results Summary:")
    print("Match | Score | Events | Possessions")
    print("------|-------|--------|------------")
    
    total_home = 0
    total_away = 0
    
    for result in results:
        total_home += result['home_score']
        total_away += result['away_score']
        print(f"  {result['match']:2d}  | {result['home_score']:2d}-{result['away_score']:<2d} | {result['total_events']:6d} | {result['possessions']:8d}")
    
    print("------|-------|--------|------------")
    print(f"Total | {total_home:2d}-{total_away:<2d} |        |")
    print(f"\nHome team won {sum(1 for r in results if r['home_score'] > r['away_score'])} matches")
    print(f"Away team won {sum(1 for r in results if r['away_score'] > r['home_score'])} matches")
    print(f"Draws: {sum(1 for r in results if r['home_score'] == r['away_score'])} matches")


if __name__ == "__main__":
    try:
        # 1. Advanced performance analysis
        model, df = analyze_match_performance()
        
        # 2. Process mining demonstration
        demonstrate_process_mining_analysis()
        
        # 3. Formation comparison
        compare_formations_simulation()
        
        print("\n" + "="*60)
        print("ADVANCED ANALYSIS COMPLETE")
        print("="*60)
        print("The simulation provides rich data for:")
        print("- Tactical analysis")
        print("- Player performance evaluation") 
        print("- Process mining studies")
        print("- Formation comparison")
        print("- Expected goals (xG) analysis")
        print("- Zone-based activity analysis")
        
    except Exception as e:
        print(f"Error in advanced analysis: {e}")
        import traceback
        traceback.print_exc()
