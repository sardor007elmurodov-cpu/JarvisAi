"""
JARVIS Advanced Scheduler
Morning routines, smart reminders, recurring tasks
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from utils import setup_logger

class AdvancedScheduler:
    """
    Advanced scheduling with routines and smart reminders
    """
    def __init__(self, data_file="scheduler_data.json"):
        self.logger = setup_logger("AdvancedScheduler")
        self.data_file = data_file
        self.routines = {}
        self.reminders = []
        self.load_data()
        
    def load_data(self):
        """Load schedules from JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.routines = data.get('routines', {})
                    self.reminders = data.get('reminders', [])
            except Exception as e:
                self.logger.error(f"Load error: {e}")
    
    def save_data(self):
        """Save schedules to JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'routines': self.routines,
                    'reminders': self.reminders
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Save error: {e}")
    
    def add_routine(self, name, time, tasks):
        """
        Add new routine
        Args:
            name: 'morning', 'evening', etc.
            time: '07:00', '22:00'
            tasks: List of tasks ["open_browser", "check_email", ...]
        """
        self.routines[name] = {
            'time': time,
            'tasks': tasks,
            'enabled': True
        }
        self.save_data()
        return f"Routine '{name}' added at {time}"
    
    def add_reminder(self, text, when, recurring=False):
        """
        Add reminder
        Args:
            text: Reminder text
            when: datetime or time string
            recurring: daily, weekly, monthly
        """
        reminder = {
            'text': text,
            'when': when if isinstance(when, str) else when.isoformat(),
            'recurring': recurring,
            'created': datetime.now().isoformat()
        }
        self.reminders.append(reminder)
        self.save_data()
        return f"Reminder added: {text}"
    
    def get_pending_reminders(self):
        """Get reminders that should be triggered now"""
        pending = []
        now = datetime.now()
        
        for reminder in self.reminders:
            try:
                when = datetime.fromisoformat(reminder['when'])
                if when <= now:
                    pending.append(reminder)
            except:
                # Time-only reminders (recurring)
                pass
        
        return pending
    
    def should_run_routine(self, name):
        """Check if routine should run now"""
        if name not in self.routines or not self.routines[name]['enabled']:
            return False
        
        routine_time = self.routines[name]['time']
        now = datetime.now().strftime('%H:%M')
        
        return routine_time == now
    
    def get_todays_schedule(self):
        """Get all reminders and routines for today"""
        schedule = []
        
        # Add routines
        for name, routine in self.routines.items():
            if routine['enabled']:
                schedule.append({
                    'type': 'routine',
                    'time': routine['time'],
                    'name': name,
                    'tasks': routine['tasks']
                })
        
        # Add today's reminders
        today = datetime.now().date()
        for reminder in self.reminders:
            try:
                when = datetime.fromisoformat(reminder['when'])
                if when.date() == today:
                    schedule.append({
                        'type': 'reminder',
                        'time': when.strftime('%H:%M'),
                        'text': reminder['text']
                    })
            except:
                pass
        
        # Sort by time
        schedule.sort(key=lambda x: x['time'])
        return schedule

if __name__ == "__main__":
    scheduler = AdvancedScheduler()
    scheduler.add_routine('morning', '07:00', ['open_browser', 'check_weather'])
    print("Scheduler ready")
