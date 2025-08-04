"""
Data Logger
==========

Logs system data to SQLite database for analysis and monitoring.
"""

import sqlite3
import json
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class DataLogger:
    """Manages data logging to SQLite database."""
    
    def __init__(self, config):
        """Initialize data logger."""
        self.config = config
        self.db_path = config.get('logging.database_path', 'data/energy_system.db')
        self.log_interval = config.get('logging.log_interval', 60)
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # System state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    current_source TEXT NOT NULL,
                    sensor_data TEXT NOT NULL,
                    optimal_source TEXT,
                    confidence REAL,
                    system_health TEXT
                )
            ''')
            
            # Emergency events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emergency_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    sensor_data TEXT,
                    action_taken TEXT
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    unit TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def log_system_state(self, state_data):
        """Log current system state."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_state 
                (timestamp, current_source, sensor_data, optimal_source, confidence, system_health)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                state_data['timestamp'].isoformat() if hasattr(state_data['timestamp'], 'isoformat') 
                else str(state_data['timestamp']),
                state_data['current_source'],
                json.dumps(state_data['sensor_data']),
                state_data.get('optimal_source'),
                state_data.get('confidence'),
                state_data.get('system_health', 'unknown')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging system state: {e}")
    
    def log_emergency(self, event_description, sensor_data=None, action_taken=None):
        """Log emergency event."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO emergency_events 
                (timestamp, event_type, description, sensor_data, action_taken)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                'emergency',
                event_description,
                json.dumps(sensor_data) if sensor_data else None,
                action_taken
            ))
            
            conn.commit()
            conn.close()
            logger.critical(f"Emergency logged: {event_description}")
            
        except Exception as e:
            logger.error(f"Error logging emergency: {e}")
    
    def log_performance_metric(self, metric_name, value, unit=None):
        """Log performance metric."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (timestamp, metric_name, metric_value, unit)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                metric_name,
                float(value),
                unit
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging performance metric: {e}")
    
    def get_recent_data(self, hours=24, table='system_state'):
        """Get recent data from specified table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f'''
                SELECT * FROM {table} 
                WHERE datetime(timestamp) > datetime('now', '-{hours} hours')
                ORDER BY timestamp DESC
            ''')
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error retrieving recent data: {e}")
            return []
    
    def get_system_statistics(self, hours=24):
        """Get system performance statistics."""
        try:
            data = self.get_recent_data(hours)
            
            if not data:
                return {}
            
            # Count source usage
            source_counts = {}
            total_entries = len(data)
            
            for entry in data:
                source = entry['current_source']
                source_counts[source] = source_counts.get(source, 0) + 1
            
            # Calculate percentages
            source_percentages = {
                source: (count / total_entries) * 100 
                for source, count in source_counts.items()
            }
            
            # Get emergency count
            emergency_data = self.get_recent_data(hours, 'emergency_events')
            emergency_count = len(emergency_data)
            
            return {
                'total_entries': total_entries,
                'source_usage': source_percentages,
                'emergency_count': emergency_count,
                'data_period_hours': hours,
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def cleanup_old_data(self, days=30):
        """Remove data older than specified days."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            tables = ['system_state', 'emergency_events', 'performance_metrics']
            
            for table in tables:
                cursor.execute(f'''
                    DELETE FROM {table} 
                    WHERE datetime(timestamp) < datetime('now', '-{days} days')
                ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Cleaned up data older than {days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def export_data(self, output_file, hours=24):
        """Export recent data to JSON file."""
        try:
            data = {
                'system_state': self.get_recent_data(hours, 'system_state'),
                'emergency_events': self.get_recent_data(hours, 'emergency_events'),
                'performance_metrics': self.get_recent_data(hours, 'performance_metrics'),
                'statistics': self.get_system_statistics(hours),
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Data exported to {output_file}")
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
    
    def close(self):
        """Close data logger (cleanup if needed)."""
        # Perform any necessary cleanup
        self.cleanup_old_data()
        logger.info("Data logger closed")
