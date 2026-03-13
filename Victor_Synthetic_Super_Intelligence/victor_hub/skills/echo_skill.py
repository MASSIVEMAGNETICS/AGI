"""
Echo Skill - Simple test skill that echoes back input
Demonstrates the skill interface
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from victor_hub.victor_boot import Skill, Task, Result


class EchoSkill(Skill):
    """Simple echo skill for testing"""
    
    def __init__(self):
        super().__init__(
            name="echo",
            repo="Victor_Synthetic_Super_Intelligence",
            capabilities=["echo", "test", "general"]
        )
    
    def execute(self, task: Task, context: dict) -> Result:
        """Echo back the task description"""
        output = f"Echo: {task.description}"
        
        return Result(
            task_id=task.id,
            status="success",
            output=output,
            metadata={"skill": self.name}
        )
