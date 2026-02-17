"""
Base Agent Class
Provides common functionality for all recruitment agents
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio


class BaseAgent(ABC):
    """
    Abstract base class for all recruitment agents
    """

    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent

        Args:
            agent_id: Unique identifier for the agent
            config: Configuration dictionary for the agent
        """
        self.agent_id = agent_id
        self.config = config or {}
        self.status = "initialized"
        self.created_at = datetime.now()
        self.last_run = None
        self.results = []
        self.errors = []

        # Setup logging
        self.logger = logging.getLogger(f"{self.__class__.__name__}[{agent_id}]")
        self.logger.setLevel(logging.INFO)

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's main task

        Returns:
            Dictionary containing execution results
        """
        pass

    def log(self, message: str, level: str = "info"):
        """
        Log a message with the specified level

        Args:
            message: Message to log
            level: Log level (info, warning, error, debug)
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)

    def update_status(self, status: str):
        """
        Update agent status

        Args:
            status: New status (running, completed, failed, idle)
        """
        self.status = status
        self.log(f"Status updated to: {status}")

    def add_result(self, result: Dict[str, Any]):
        """
        Add a result to the agent's results list

        Args:
            result: Result dictionary to add
        """
        result['timestamp'] = datetime.now().isoformat()
        self.results.append(result)

    def add_error(self, error: str, exception: Optional[Exception] = None):
        """
        Add an error to the agent's error list

        Args:
            error: Error message
            exception: Optional exception object
        """
        error_entry = {
            'message': error,
            'timestamp': datetime.now().isoformat(),
            'exception': str(exception) if exception else None
        }
        self.errors.append(error_entry)
        self.log(error, level="error")

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the agent's current state

        Returns:
            Dictionary with agent summary information
        """
        return {
            'agent_id': self.agent_id,
            'agent_type': self.__class__.__name__,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'results_count': len(self.results),
            'errors_count': len(self.errors),
            'config': self.config
        }

    async def run(self, **kwargs) -> Dict[str, Any]:
        """
        Run the agent with error handling and status management

        Returns:
            Dictionary containing execution results and status
        """
        try:
            self.update_status("running")
            self.last_run = datetime.now()

            result = await self.execute(**kwargs)

            self.update_status("completed")
            return {
                'success': True,
                'agent_id': self.agent_id,
                'data': result,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.update_status("failed")
            self.add_error(f"Execution failed: {str(e)}", e)

            return {
                'success': False,
                'agent_id': self.agent_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
