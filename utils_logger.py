"""
Event Logger for Football Simulation
Handles logging events to both CSV and XES formats for process mining
"""

import pandas as pd
import pm4py
from datetime import datetime
from typing import Dict, List, Any
import json
import os


class EventLogger:
    """Event logger for football simulation events"""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
    
    def add(self, event_dict: Dict[str, Any]):
        """Add an event to the buffer"""
        # Ensure all required fields are present
        required_fields = [
            'possession_id', 'timestamp', 'team', 'player_id', 
            'action', 'zone', 'pressure', 'team_status', 'outcome', 'xg_change'
        ]
        
        # Add timestamp if not present
        if 'timestamp' not in event_dict:
            event_dict['timestamp'] = datetime.now().isoformat() + 'Z'
        
        # Add default values for missing fields
        for field in required_fields:
            if field not in event_dict:
                if field == 'pressure':
                    event_dict[field] = 0
                elif field == 'team_status':
                    event_dict[field] = 'Tied'
                elif field == 'outcome':
                    event_dict[field] = 'Success'
                elif field == 'xg_change':
                    event_dict[field] = 0.0
                else:
                    event_dict[field] = 'Unknown'
        
        self.events.append(event_dict.copy())
    
    def dump_csv(self, path: str):
        """Export events to CSV format"""
        if not self.events:
            print("No events to export")
            return
        
        df = pd.DataFrame(self.events)
        
        # Ensure proper column order
        columns = [
            'possession_id', 'timestamp', 'team', 'player_id', 
            'action', 'zone', 'pressure', 'team_status', 'outcome', 'xg_change'
        ]
        
        # Reorder columns if they exist
        existing_columns = [col for col in columns if col in df.columns]
        df = df[existing_columns]
        
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        df.to_csv(path, index=False)
        print(f"Events exported to CSV: {path}")
    
    def dump_xes(self, path: str):
        """Export events to XES format for process mining"""
        if not self.events:
            print("No events to export")
            return
        
        try:
            df = pd.DataFrame(self.events)
            
            # PM4Py expects specific column names
            # Map our columns to PM4Py standard names
            df_pm4py = df.copy()
            df_pm4py['case:concept:name'] = df_pm4py['possession_id']
            df_pm4py['concept:name'] = df_pm4py['action']
            df_pm4py['time:timestamp'] = pd.to_datetime(df_pm4py['timestamp'])
            
            # Add additional attributes
            df_pm4py['org:resource'] = df_pm4py['player_id'].astype(str)
            df_pm4py['team'] = df_pm4py['team']
            df_pm4py['zone'] = df_pm4py['zone']
            df_pm4py['pressure'] = df_pm4py['pressure']
            df_pm4py['outcome'] = df_pm4py['outcome']
            df_pm4py['xg_change'] = df_pm4py['xg_change']
            
            # Create event log
            event_log = pm4py.format_dataframe(
                df_pm4py, 
                case_id='case:concept:name',
                activity_key='concept:name',
                timestamp_key='time:timestamp'
            )
            
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
            pm4py.write_xes(event_log, path)
            print(f"Events exported to XES: {path}")
            
        except Exception as e:
            print(f"Error exporting to XES: {e}")
            # Fallback to manual XES creation
            self._create_manual_xes(path)
    
    def _create_manual_xes(self, path: str):
        """Create XES file manually if PM4Py fails"""
        xes_content = '''<?xml version="1.0" encoding="UTF-8" ?>
<log xes.version="1.0" xes.features="nested-attributes" openxes.version="1.0RC7">
  <extension name="Lifecycle" prefix="lifecycle" uri="http://www.xes-standard.org/lifecycle.xesext"/>
  <extension name="Organizational" prefix="org" uri="http://www.xes-standard.org/org.xesext"/>
  <extension name="Time" prefix="time" uri="http://www.xes-standard.org/time.xesext"/>
  <extension name="Concept" prefix="concept" uri="http://www.xes-standard.org/concept.xesext"/>
  <global scope="trace">
    <string key="concept:name" value="UNKNOWN"/>
  </global>
  <global scope="event">
    <string key="concept:name" value="UNKNOWN"/>
    <string key="lifecycle:transition" value="complete"/>
  </global>
'''
        
        # Group events by possession_id (case)
        cases = {}
        for event in self.events:
            case_id = event['possession_id']
            if case_id not in cases:
                cases[case_id] = []
            cases[case_id].append(event)
        
        # Create traces
        for case_id, events in cases.items():
            xes_content += f'  <trace>\n'
            xes_content += f'    <string key="concept:name" value="{case_id}"/>\n'
            
            for event in events:
                xes_content += f'    <event>\n'
                xes_content += f'      <string key="concept:name" value="{event["action"]}"/>\n'
                xes_content += f'      <date key="time:timestamp" value="{event["timestamp"]}"/>\n'
                xes_content += f'      <string key="org:resource" value="{event["player_id"]}"/>\n'
                xes_content += f'      <string key="team" value="{event["team"]}"/>\n'
                xes_content += f'      <string key="zone" value="{event["zone"]}"/>\n'
                xes_content += f'      <int key="pressure" value="{event["pressure"]}"/>\n'
                xes_content += f'      <string key="outcome" value="{event["outcome"]}"/>\n'
                xes_content += f'      <float key="xg_change" value="{event["xg_change"]}"/>\n'
                xes_content += f'    </event>\n'
            
            xes_content += f'  </trace>\n'
        
        xes_content += '</log>'
        
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(xes_content)
        print(f"Events exported to XES (manual): {path}")
    
    def clear(self):
        """Clear all events from the buffer"""
        self.events.clear()
    
    def get_event_count(self):
        """Return the number of logged events"""
        return len(self.events)
    
    def get_summary(self):
        """Get a summary of logged events"""
        if not self.events:
            return "No events logged"
        
        df = pd.DataFrame(self.events)
        summary = {
            'total_events': len(self.events),
            'unique_possessions': df['possession_id'].nunique() if 'possession_id' in df.columns else 0,
            'actions': df['action'].value_counts().to_dict() if 'action' in df.columns else {},
            'teams': df['team'].value_counts().to_dict() if 'team' in df.columns else {}
        }
        return summary
