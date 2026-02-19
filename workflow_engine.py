import os
import subprocess
import threading
import time

class WorkflowEngine:
    """
    JARVIS - Autonomous Workflow Engine (Elite v10.0)
    Executes multi-step automated sequences (Macros).
    """
    def __init__(self, executor=None, terminal_callback=None):
        self.executor = executor
        self.log = terminal_callback
        
        # Pre-defined automated workflows
        self.workflows = {
            "dev_mode": [
                {"action": "open_app", "parameters": {"app_name": "vscode"}},
                {"action": "open_app", "parameters": {"app_name": "cmd"}},
                {"action": "open_website", "parameters": {"url": "https://github.com"}},
                {"action": "system_healer", "parameters": {}}
            ],
            "research_mode": [
                {"action": "perform_research", "parameters": {"topic": "latest AI trends"}},
                {"action": "open_app", "parameters": {"app_name": "notepad"}},
                {"action": "get_news_digest", "parameters": {}}
            ],
            "cleanup_mode": [
                {"action": "system_healer", "parameters": {}},
                {"action": "toggle_gaming_mode", "parameters": {}} # Actually just boosts priority
            ]
        }

    def run_workflow(self, workflow_name):
        """Execute a chain of actions"""
        if workflow_name not in self.workflows:
            if self.log: self.log(f"⚠️ [OMNI] Workflow '{workflow_name}' not found.")
            return False
        
        if self.log: self.log(f"🚀 [OMNI] Initiating '{workflow_name.upper()}' automation...")
        
        def _execute_chain():
            for task in self.workflows[workflow_name]:
                try:
                    action = task.get("action")
                    params = task.get("parameters")
                    if self.executor:
                        res = self.executor.execute(task)
                        if self.log: self.log(f"✅ [OMNI] Step: {action} -> Done")
                    time.sleep(1.5) # Gap between apps to prevent OS lag
                except Exception as e:
                    if self.log: self.log(f"❌ [OMNI] Step {action} failed: {str(e)}")
            
            if self.log: self.log(f"✨ [OMNI] '{workflow_name.upper()}' workflow complete.")
            
        threading.Thread(target=_execute_chain, daemon=True).start()
        return True
