"""
Football Simulation Model
11v11 football simulation using Mesa 3.x with event logging for process mining
"""

import mesa
import random
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from player_agent import PlayerAgent, Position
from utils_logger import EventLogger


class FootballModel(mesa.Model):
    """
    Football simulation model with 11v11 players
    """
    
    def __init__(self, match_duration: int = 90, seed: Optional[int] = None):
        super().__init__(seed=seed)
        
        # Match settings
        self.match_duration = match_duration  # minutes
        self.current_minute = 0
        self.home_score = 0
        self.away_score = 0
        self.match_id = random.randint(1000, 9999)
        
        # Game state
        self.possession_team = "Home"  # Team currently in possession
        self.possession_counter = 1
        self.ball_carrier = None  # PlayerAgent who has the ball
        
        # Event logging
        self.event_logger = EventLogger()
        
        # Initialize teams
        self._create_teams()
        
        # Start first possession
        self._start_possession()
        
        print(f"Football match {self.match_id} initialized: {len(self.agents)} players")
    
    def _create_teams(self):
        """Create both teams with 11 players each"""
        
        # Home team formation (4-4-2)
        home_formation = [
            (Position.GOALKEEPER, 1),
            (Position.DEFENDER, 2), (Position.DEFENDER, 3), 
            (Position.DEFENDER, 4), (Position.DEFENDER, 5),
            (Position.MIDFIELDER, 6), (Position.MIDFIELDER, 7),
            (Position.MIDFIELDER, 8), (Position.MIDFIELDER, 9),
            (Position.FORWARD, 10), (Position.FORWARD, 11)
        ]
        
        # Away team formation (4-3-3)
        away_formation = [
            (Position.GOALKEEPER, 1),
            (Position.DEFENDER, 2), (Position.DEFENDER, 3),
            (Position.DEFENDER, 4), (Position.DEFENDER, 5),
            (Position.MIDFIELDER, 6), (Position.MIDFIELDER, 7), (Position.MIDFIELDER, 8),
            (Position.FORWARD, 9), (Position.FORWARD, 10), (Position.FORWARD, 11)
        ]
        
        # Create home team
        for position, jersey_num in home_formation:
            player = PlayerAgent(self, "Home", position, jersey_num)
            # Players are automatically added to self.agents in Mesa 3.x
        
        # Create away team  
        for position, jersey_num in away_formation:
            player = PlayerAgent(self, "Away", position, jersey_num)
            # Players are automatically added to self.agents in Mesa 3.x
    
    def _start_possession(self):
        """Start a new possession sequence"""
        self.possession_counter += 1
        
        # Choose a random player from the possessing team to start with ball
        team_players = [agent for agent in self.agents 
                       if isinstance(agent, PlayerAgent) and agent.team == self.possession_team]
        
        if team_players:
            # Prefer midfielders for possession start
            midfielders = [p for p in team_players if p.position == Position.MIDFIELDER]
            if midfielders:
                self.ball_carrier = random.choice(midfielders)
            else:
                self.ball_carrier = random.choice(team_players)
            
            # Reset all players' ball possession
            for agent in self.agents:
                if isinstance(agent, PlayerAgent):
                    agent.has_ball = False
            
            # Give ball to chosen player
            self.ball_carrier.has_ball = True
            self.ball_carrier.receive_ball()
            
            # Log possession start
            self._log_possession_event('PossessionStart')
    
    def change_possession(self):
        """Change possession to the other team"""
        # Log possession end
        self._log_possession_event('PossessionEnd')
        
        # Switch possession
        self.possession_team = "Away" if self.possession_team == "Home" else "Home"
        self.ball_carrier = None
        
        # Clear ball from all players
        for agent in self.agents:
            if isinstance(agent, PlayerAgent):
                agent.has_ball = False
        
        # Start new possession after a brief delay
        self._start_possession()
    
    def score_goal(self, scoring_team: str):
        """Handle goal scoring"""
        if scoring_team == "Home":
            self.home_score += 1
        else:
            self.away_score += 1
        
        print(f"GOAL! {scoring_team} scores! Score: Home {self.home_score} - {self.away_score} Away")
        
        # Log goal
        event = {
            'possession_id': f"M{self.match_id}-GOAL{self.home_score + self.away_score:02d}",
            'team': scoring_team,
            'player_id': self.ball_carrier.jersey_number if self.ball_carrier else 0,
            'action': 'Goal',
            'zone': self.ball_carrier.zone if self.ball_carrier else 'Unknown',
            'pressure': 0,
            'team_status': self.get_team_status(),
            'outcome': 'Success',
            'xg_change': 1.0
        }
        self.event_logger.add(event)
        
        # Restart with kickoff (opposite team gets possession)
        self.possession_team = "Away" if scoring_team == "Home" else "Home"
        self._start_possession()
    
    def get_team_status(self) -> str:
        """Get current team status (winning/losing/tied)"""
        if self.home_score > self.away_score:
            return "Home Leading"
        elif self.away_score > self.home_score:
            return "Away Leading"
        else:
            return "Tied"
    
    def _log_possession_event(self, action: str):
        """Log possession-related events"""
        event = {
            'possession_id': f"M{self.match_id}-P{self.possession_counter:03d}",
            'team': self.possession_team,
            'player_id': 0,  # Team-level event
            'action': action,
            'zone': 'C3',  # Center of field
            'pressure': 0,
            'team_status': self.get_team_status(),
            'outcome': 'Success',
            'xg_change': 0.0
        }
        self.event_logger.add(event)
    
    def step(self):
        """Execute one step of the simulation"""
        if not self.running:
            return
        
        # Advance time (each step = ~0.1 minutes)
        self.current_minute += 0.1
        
        # Check if match is over
        if self.current_minute >= self.match_duration:
            self._end_match()
            return
        
        # Execute player actions
        self.agents.shuffle_do("step")
        
        # Random events
        self._handle_random_events()
        
        # Update ball carrier reference
        self._update_ball_carrier()
    
    def _update_ball_carrier(self):
        """Update who has the ball"""
        ball_carriers = [agent for agent in self.agents 
                        if isinstance(agent, PlayerAgent) and agent.has_ball]
        
        if len(ball_carriers) == 1:
            self.ball_carrier = ball_carriers[0]
        elif len(ball_carriers) > 1:
            # Multiple players think they have ball - fix this
            for agent in ball_carriers[1:]:
                agent.has_ball = False
            self.ball_carrier = ball_carriers[0]
        elif len(ball_carriers) == 0:
            # No one has ball - start new possession
            self.ball_carrier = None
            if random.random() < 0.3:  # 30% chance to change possession
                self.change_possession()
    
    def _handle_random_events(self):
        """Handle random match events"""
        # Small chance of random events
        if random.random() < 0.01:  # 1% chance per step
            event_type = random.choice(['Foul', 'Tackle', 'Interception'])
            
            # Choose random players
            all_players = [agent for agent in self.agents if isinstance(agent, PlayerAgent)]
            if all_players:
                player = random.choice(all_players)
                
                event = {
                    'possession_id': f"M{self.match_id}-P{self.possession_counter:03d}",
                    'team': player.team,
                    'player_id': player.jersey_number,
                    'action': event_type,
                    'zone': player.zone,
                    'pressure': random.randint(0, 1),
                    'team_status': self.get_team_status(),
                    'outcome': random.choice(['Success', 'Failure']),
                    'xg_change': random.uniform(-0.05, 0.05)
                }
                self.event_logger.add(event)
                
                # Handle specific events
                if event_type in ['Tackle', 'Interception'] and event['outcome'] == 'Success':
                    self.change_possession()
    
    def _end_match(self):
        """End the match and generate final statistics"""
        self.running = False
        
        print(f"\n=== MATCH {self.match_id} FINAL ===")
        print(f"Final Score: Home {self.home_score} - {self.away_score} Away")
        print(f"Total Events: {self.event_logger.get_event_count()}")
        print(f"Possessions: {self.possession_counter}")
        
        # Show event summary
        summary = self.event_logger.get_summary()
        print(f"\nEvent Summary:")
        for action, count in summary.get('actions', {}).items():
            print(f"  {action}: {count}")
    
    def export_logs(self, base_filename: str = None):
        """Export event logs to CSV and XES files"""
        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"football_match_{self.match_id}_{timestamp}"
        
        csv_path = f"{base_filename}.csv"
        xes_path = f"{base_filename}.xes"
        
        self.event_logger.dump_csv(csv_path)
        self.event_logger.dump_xes(xes_path)
        
        return csv_path, xes_path
    
    def get_match_stats(self) -> Dict:
        """Get comprehensive match statistics"""
        stats = {
            'match_id': self.match_id,
            'duration_minutes': self.current_minute,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'total_events': self.event_logger.get_event_count(),
            'possessions': self.possession_counter,
            'event_summary': self.event_logger.get_summary()
        }
        
        return stats


def run_match(duration: int = 90, seed: Optional[int] = None, export_logs: bool = True) -> FootballModel:
    """
    Run a complete football match simulation
    
    Args:
        duration: Match duration in minutes
        seed: Random seed for reproducibility
        export_logs: Whether to export event logs
    
    Returns:
        FootballModel: The completed match model
    """
    print(f"Starting football match simulation...")
    print(f"Duration: {duration} minutes")
    
    # Create and run model
    model = FootballModel(match_duration=duration, seed=seed)
    
    # Run simulation
    steps = 0
    max_steps = duration * 10  # ~0.1 minutes per step
    
    while model.running and steps < max_steps:
        model.step()
        steps += 1
        
        # Progress indicator
        if steps % 100 == 0:
            minute = int(model.current_minute)
            print(f"Minute {minute}: Home {model.home_score} - {model.away_score} Away")
    
    # Export logs if requested
    if export_logs:
        csv_path, xes_path = model.export_logs()
        print(f"\nLogs exported:")
        print(f"  CSV: {csv_path}")
        print(f"  XES: {xes_path}")
    
    return model


if __name__ == "__main__":
    # Run a sample match
    model = run_match(duration=5, seed=42)  # Short 5-minute match for testing
    
    # Display final statistics
    stats = model.get_match_stats()
    print(f"\n=== FINAL STATISTICS ===")
    for key, value in stats.items():
        if key != 'event_summary':
            print(f"{key}: {value}")
