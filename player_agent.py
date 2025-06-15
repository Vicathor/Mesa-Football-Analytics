"""
Football Player Agent
Represents individual football players with different positions and behaviors
"""

import mesa
import numpy as np
from typing import Dict, List, Tuple, Optional
from enum import Enum
import random


class Position(Enum):
    """Player positions"""
    GOALKEEPER = "GK"
    DEFENDER = "DEF"
    MIDFIELDER = "MID"
    FORWARD = "FWD"


class PlayerAgent(mesa.Agent):
    """
    A football player agent with position-specific behaviors
    """
    
    def __init__(self, model, team: str, position: Position, jersey_number: int):
        super().__init__(model)
        
        # Basic attributes
        self.team = team
        self.position = position
        self.jersey_number = jersey_number
        
        # Physical attributes (0-100 scale)
        self.speed = self._generate_attribute()
        self.passing = self._generate_attribute_by_position('passing')
        self.shooting = self._generate_attribute_by_position('shooting')
        self.defending = self._generate_attribute_by_position('defending')
        self.dribbling = self._generate_attribute_by_position('dribbling')
        self.positioning = self._generate_attribute_by_position('positioning')
        
        # Game state
        self.has_ball = False
        self.stamina = 100.0
        self.last_action = None
        self.zone = self._get_starting_zone()
        
        # Tactical attributes
        self.pressure_tolerance = random.uniform(0.3, 0.9)
        self.risk_taking = random.uniform(0.2, 0.8)
        
    def _generate_attribute(self, base: int = 50) -> int:
        """Generate a random attribute with normal distribution"""
        return max(10, min(99, int(np.random.normal(base, 15))))
    
    def _generate_attribute_by_position(self, attribute: str) -> int:
        """Generate attribute based on position"""
        position_bonuses = {
            Position.GOALKEEPER: {
                'passing': -10, 'shooting': -20, 'defending': 20, 
                'dribbling': -10, 'positioning': 15
            },
            Position.DEFENDER: {
                'passing': 5, 'shooting': -15, 'defending': 25, 
                'dribbling': -5, 'positioning': 10
            },
            Position.MIDFIELDER: {
                'passing': 20, 'shooting': 0, 'defending': 5, 
                'dribbling': 10, 'positioning': 5
            },
            Position.FORWARD: {
                'passing': 0, 'shooting': 25, 'defending': -15, 
                'dribbling': 15, 'positioning': 10
            }
        }
        
        base = 50
        bonus = position_bonuses.get(self.position, {}).get(attribute, 0)
        return self._generate_attribute(base + bonus)
    
    def _get_starting_zone(self) -> str:
        """Get starting zone based on position and team"""
        # Zones are A1-D5 (A=defense, D=attack, 1-5=left to right)
        if self.team == "Home":
            if self.position == Position.GOALKEEPER:
                return "A3"
            elif self.position == Position.DEFENDER:
                return random.choice(["A1", "A2", "A4", "A5", "B2", "B4"])
            elif self.position == Position.MIDFIELDER:
                return random.choice(["B1", "B3", "B5", "C1", "C3", "C5"])
            else:  # Forward
                return random.choice(["C2", "C4", "D1", "D3", "D5"])
        else:  # Away team (flipped)
            if self.position == Position.GOALKEEPER:
                return "D3"
            elif self.position == Position.DEFENDER:
                return random.choice(["D1", "D2", "D4", "D5", "C2", "C4"])
            elif self.position == Position.MIDFIELDER:
                return random.choice(["C1", "C3", "C5", "B1", "B3", "B5"])
            else:  # Forward
                return random.choice(["B2", "B4", "A1", "A3", "A5"])
    
    def step(self):
        """Execute one step of the agent's behavior"""
        if not self.model.running:
            return
        
        # Decrease stamina slightly
        self.stamina = max(0, self.stamina - 0.1)
        
        # If this player has the ball, make a decision
        if self.has_ball:
            self._decide_action_with_ball()
        else:
            self._decide_action_without_ball()
    
    def _decide_action_with_ball(self):
        """Decide what to do when having the ball"""
        pressure = self._calculate_pressure()
        
        # Get available actions based on position and situation
        actions = self._get_available_actions()
        
        # Weight actions based on player attributes and situation
        action_weights = self._calculate_action_weights(actions, pressure)
        
        # Select action
        if action_weights:
            action = self._weighted_choice(action_weights)
            self._execute_action(action, pressure)
    
    def _decide_action_without_ball(self):
        """Decide what to do when not having the ball"""
        # Move to better position, apply pressure, or support
        actions = ['Move', 'SupportRequest', 'Pressure']
        
        # Simple probability-based selection
        if random.random() < 0.1:  # 10% chance of support request
            self._log_event('SupportRequest', 'Success', 0.0)
        elif random.random() < 0.3:  # 30% chance of movement
            self._move_to_better_position()
    
    def _get_available_actions(self) -> List[str]:
        """Get list of available actions"""
        base_actions = ['Pass', 'Dribble']
        
        # Add shooting if in attacking zone
        if self._is_in_attacking_zone():
            base_actions.append('Shot')
        
        # Add clearance if defender under pressure
        if self.position in [Position.DEFENDER, Position.GOALKEEPER]:
            base_actions.append('Clearance')
        
        return base_actions
    
    def _calculate_action_weights(self, actions: List[str], pressure: float) -> Dict[str, float]:
        """Calculate weights for each available action"""
        weights = {}
        
        for action in actions:
            if action == 'Pass':
                weights[action] = self.passing * (1 + 0.5 * pressure)  # Passing preferred under pressure
            elif action == 'Dribble':
                weights[action] = self.dribbling * (1 - 0.3 * pressure)  # Dribbling harder under pressure
            elif action == 'Shot':
                weights[action] = self.shooting * self._get_shooting_modifier()
            elif action == 'Clearance':
                weights[action] = 40 * pressure  # Clearance more likely under pressure
        
        return weights
    
    def _weighted_choice(self, weights: Dict[str, float]) -> str:
        """Choose action based on weights"""
        total = sum(weights.values())
        if total == 0:
            return random.choice(list(weights.keys()))
        
        r = random.uniform(0, total)
        upto = 0
        for action, weight in weights.items():
            if upto + weight >= r:
                return action
            upto += weight
        
        return list(weights.keys())[-1]
    
    def _execute_action(self, action: str, pressure: float):
        """Execute the chosen action"""
        success_rate = self._calculate_success_rate(action, pressure)
        outcome = 'Success' if random.random() < success_rate else 'Failure'
        
        xg_change = 0.0
        
        if action == 'Pass':
            xg_change = self._execute_pass(outcome)
        elif action == 'Dribble':
            xg_change = self._execute_dribble(outcome)
        elif action == 'Shot':
            xg_change = self._execute_shot(outcome)
        elif action == 'Clearance':
            xg_change = self._execute_clearance(outcome)
        
        self._log_event(action, outcome, xg_change, pressure)
    
    def _execute_pass(self, outcome: str) -> float:
        """Execute a pass action"""
        if outcome == 'Success':
            # Find teammate to pass to
            teammate = self._find_pass_target()
            if teammate:
                self.has_ball = False
                teammate.has_ball = True
                teammate.zone = self._get_nearby_zone(self.zone)
                return 0.02  # Small positive xG change for successful pass
        else:
            # Pass intercepted - lose possession
            self._lose_possession()
            return -0.05  # Negative xG change for losing possession
        
        return 0.0
    
    def _execute_dribble(self, outcome: str) -> float:
        """Execute a dribble action"""
        if outcome == 'Success':
            # Move forward with ball
            self.zone = self._get_advanced_zone(self.zone)
            return 0.03  # Positive xG change for successful dribble
        else:
            # Lose possession
            self._lose_possession()
            return -0.03
        
        return 0.0
    
    def _execute_shot(self, outcome: str) -> float:
        """Execute a shot action"""
        xg_value = self._calculate_xg()
        
        if outcome == 'Success':
            # Goal scored
            self.model.score_goal(self.team)
            self._lose_possession()  # Restart play
            return xg_value
        else:
            # Shot missed or saved
            self._lose_possession()
            return -xg_value * 0.5  # Partial negative xG for missed shot
    
    def _execute_clearance(self, outcome: str) -> float:
        """Execute a clearance action"""
        self._lose_possession()
        return 0.0  # Clearance doesn't change xG significantly
    
    def _calculate_success_rate(self, action: str, pressure: float) -> float:
        """Calculate success rate for an action"""
        base_rates = {
            'Pass': self.passing / 100.0,
            'Dribble': self.dribbling / 100.0,
            'Shot': self.shooting / 100.0 * 0.3,  # Shots are naturally less likely to succeed
            'Clearance': 0.8  # Clearances usually succeed
        }
        
        base_rate = base_rates.get(action, 0.5)
        
        # Adjust for pressure
        pressure_penalty = pressure * 0.3
        
        # Adjust for stamina
        stamina_modifier = self.stamina / 100.0
        
        return max(0.1, min(0.95, base_rate * stamina_modifier - pressure_penalty))
    
    def _calculate_pressure(self) -> float:
        """Calculate pressure from opposing players"""
        # Simple pressure calculation based on nearby opponents
        opponents_nearby = len([agent for agent in self.model.agents 
                               if isinstance(agent, PlayerAgent) 
                               and agent.team != self.team 
                               and self._is_nearby(agent.zone)])
        
        return min(1.0, opponents_nearby * 0.3)
    
    def _calculate_xg(self) -> float:
        """Calculate expected goals value for current position"""
        zone_xg_values = {
            'D1': 0.15, 'D2': 0.25, 'D3': 0.35, 'D4': 0.25, 'D5': 0.15,
            'C1': 0.08, 'C2': 0.12, 'C3': 0.18, 'C4': 0.12, 'C5': 0.08,
            'B1': 0.03, 'B2': 0.05, 'B3': 0.07, 'B4': 0.05, 'B5': 0.03,
            'A1': 0.01, 'A2': 0.01, 'A3': 0.02, 'A4': 0.01, 'A5': 0.01
        }
        
        # Adjust for away team (flip zones)
        if self.team == "Away":
            flipped_zones = {
                'D': 'A', 'C': 'B', 'B': 'C', 'A': 'D'
            }
            original_row = self.zone[0]
            if original_row in flipped_zones:
                flipped_zone = flipped_zones[original_row] + self.zone[1]
                return zone_xg_values.get(flipped_zone, 0.05)
        
        return zone_xg_values.get(self.zone, 0.05)
    
    def _find_pass_target(self) -> Optional['PlayerAgent']:
        """Find a teammate to pass to"""
        teammates = [agent for agent in self.model.agents 
                    if isinstance(agent, PlayerAgent) 
                    and agent.team == self.team 
                    and not agent.has_ball
                    and agent.unique_id != self.unique_id]
        
        if teammates:
            # Prefer teammates in advanced positions
            return random.choice(teammates)
        
        return None
    
    def _lose_possession(self):
        """Lose possession of the ball"""
        self.has_ball = False
        self.model.change_possession()
    
    def _is_in_attacking_zone(self) -> bool:
        """Check if player is in attacking zone"""
        if self.team == "Home":
            return self.zone.startswith('C') or self.zone.startswith('D')
        else:
            return self.zone.startswith('A') or self.zone.startswith('B')
    
    def _is_nearby(self, other_zone: str) -> bool:
        """Check if another zone is nearby"""
        # Simple distance calculation
        if not other_zone or len(other_zone) < 2:
            return False
        
        try:
            row1, col1 = ord(self.zone[0]) - ord('A'), int(self.zone[1])
            row2, col2 = ord(other_zone[0]) - ord('A'), int(other_zone[1])
            distance = abs(row1 - row2) + abs(col1 - col2)
            return distance <= 2
        except (ValueError, IndexError):
            return False
    
    def _get_nearby_zone(self, current_zone: str) -> str:
        """Get a nearby zone"""
        zones = ['A1', 'A2', 'A3', 'A4', 'A5',
                'B1', 'B2', 'B3', 'B4', 'B5',
                'C1', 'C2', 'C3', 'C4', 'C5',
                'D1', 'D2', 'D3', 'D4', 'D5']
        
        nearby = [zone for zone in zones if self._is_nearby(zone)]
        return random.choice(nearby) if nearby else current_zone
    
    def _get_advanced_zone(self, current_zone: str) -> str:
        """Get a more advanced zone (closer to opponent goal)"""
        try:
            row, col = current_zone[0], current_zone[1]
            
            if self.team == "Home":
                # Advance toward D zones
                if row == 'A':
                    return 'B' + col
                elif row == 'B':
                    return 'C' + col
                elif row == 'C':
                    return 'D' + col
            else:
                # Advance toward A zones
                if row == 'D':
                    return 'C' + col
                elif row == 'C':
                    return 'B' + col
                elif row == 'B':
                    return 'A' + col
            
            return current_zone
        except (IndexError, ValueError):
            return current_zone
    
    def _get_shooting_modifier(self) -> float:
        """Get shooting modifier based on position and zone"""
        # Higher modifier for forwards and attacking zones
        position_modifier = {
            Position.FORWARD: 1.5,
            Position.MIDFIELDER: 1.0,
            Position.DEFENDER: 0.3,
            Position.GOALKEEPER: 0.1
        }.get(self.position, 1.0)
        
        zone_modifier = 1.0
        if self._is_in_attacking_zone():
            zone_modifier = 1.8
        
        return position_modifier * zone_modifier
    
    def _move_to_better_position(self):
        """Move to a better tactical position"""
        # Simple tactical movement
        new_zone = self._get_nearby_zone(self.zone)
        if new_zone != self.zone:
            self.zone = new_zone
    
    def _log_event(self, action: str, outcome: str, xg_change: float, pressure: float = 0.0):
        """Log an event to the model's event logger"""
        if hasattr(self.model, 'event_logger'):
            event = {
                'possession_id': f"M{self.model.match_id}-P{self.model.possession_counter:03d}",
                'team': self.team,
                'player_id': self.jersey_number,
                'action': action,
                'zone': self.zone,
                'pressure': int(pressure > 0.5),  # Binary pressure indicator
                'team_status': self.model.get_team_status(),
                'outcome': outcome,
                'xg_change': round(xg_change, 3)
            }
            self.model.event_logger.add(event)
    
    def receive_ball(self):
        """Receive the ball"""
        self.has_ball = True
        # Log ball recovery
        self._log_event('BallRecovery', 'Success', 0.01)
    
    def __str__(self):
        return f"{self.team} #{self.jersey_number} ({self.position.value}) at {self.zone}"
