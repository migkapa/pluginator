"""
Context injection system for WordPress Plugin Generator.
Enables state sharing between agents using OpenAI Agents Python best practices.
"""

import json
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from loguru import logger
from threading import Lock


@dataclass
class PluginGenerationContext:
    """Context object for plugin generation workflow."""
    
    # Core plugin information
    plugin_name: Optional[str] = None
    plugin_slug: Optional[str] = None
    plugin_version: Optional[str] = "1.0.0"
    plugin_author: Optional[str] = "Anonymous"
    
    # Workflow state
    current_phase: str = "initialization"
    phases_completed: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    
    # User preferences and settings
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    requested_features: List[str] = field(default_factory=list)
    advanced_tests_requested: List[str] = field(default_factory=list)
    
    # Generated content tracking
    generated_files: List[Dict[str, Any]] = field(default_factory=list)
    compliance_issues: List[Dict[str, Any]] = field(default_factory=list)
    test_results: Dict[str, Any] = field(default_factory=dict)
    
    # Session information
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_used: Optional[str] = None
    output_directory: Optional[str] = None
    
    # Error handling and recovery
    errors_encountered: List[Dict[str, Any]] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    
    # Agent communication
    agent_messages: List[Dict[str, Any]] = field(default_factory=list)
    current_agent: Optional[str] = None
    
    def add_error(self, error_type: str, message: str, agent: Optional[str] = None):
        """Add an error to the context."""
        self.errors_encountered.append({
            "type": error_type,
            "message": message,
            "agent": agent or self.current_agent,
            "timestamp": datetime.now().isoformat(),
            "phase": self.current_phase
        })
    
    def add_agent_message(self, agent: str, message: str, message_type: str = "info"):
        """Add an agent message to the context."""
        self.agent_messages.append({
            "agent": agent,
            "message": message,
            "type": message_type,
            "timestamp": datetime.now().isoformat(),
            "phase": self.current_phase
        })
    
    def mark_phase_complete(self, phase: str):
        """Mark a phase as completed."""
        if phase not in self.phases_completed:
            self.phases_completed.append(phase)
        self.current_phase = phase
    
    def get_progress_percentage(self) -> float:
        """Calculate progress percentage based on completed phases."""
        total_phases = ["planning", "specification", "generation", "writing", "compliance", "testing", "packaging"]
        completed_count = len([p for p in self.phases_completed if p in total_phases])
        return (completed_count / len(total_phases)) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginGenerationContext':
        """Create context from dictionary."""
        # Convert datetime strings back to datetime objects
        if 'start_time' in data and isinstance(data['start_time'], str):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        
        return cls(**data)


class ContextManager:
    """Manages plugin generation context with persistence and thread safety."""
    
    def __init__(self, context_dir: str = "./.context"):
        self.context_dir = Path(context_dir)
        self.context_dir.mkdir(exist_ok=True)
        self._contexts: Dict[str, PluginGenerationContext] = {}
        self._lock = Lock()
        self._current_context: Optional[PluginGenerationContext] = None
    
    def create_context(self, **kwargs) -> PluginGenerationContext:
        """Create a new plugin generation context."""
        with self._lock:
            context = PluginGenerationContext(**kwargs)
            self._contexts[context.session_id] = context
            self._current_context = context
            self._save_context(context)
            logger.info(f"Created new context: {context.session_id}")
            return context
    
    def get_context(self, session_id: Optional[str] = None) -> Optional[PluginGenerationContext]:
        """Get context by session ID or return current context."""
        with self._lock:
            if session_id:
                return self._contexts.get(session_id)
            return self._current_context
    
    def update_context(self, session_id: str, **updates):
        """Update context with new values."""
        with self._lock:
            if session_id in self._contexts:
                context = self._contexts[session_id]
                for key, value in updates.items():
                    if hasattr(context, key):
                        setattr(context, key, value)
                self._save_context(context)
                logger.debug(f"Updated context {session_id}: {updates}")
    
    def _save_context(self, context: PluginGenerationContext):
        """Save context to disk."""
        try:
            context_file = self.context_dir / f"{context.session_id}.json"
            with open(context_file, 'w') as f:
                json.dump(context.to_dict(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
    
    def load_context(self, session_id: str) -> Optional[PluginGenerationContext]:
        """Load context from disk."""
        try:
            context_file = self.context_dir / f"{session_id}.json"
            if context_file.exists():
                with open(context_file, 'r') as f:
                    data = json.load(f)
                context = PluginGenerationContext.from_dict(data)
                with self._lock:
                    self._contexts[session_id] = context
                    self._current_context = context
                logger.info(f"Loaded context: {session_id}")
                return context
        except Exception as e:
            logger.error(f"Failed to load context {session_id}: {e}")
        return None
    
    def list_contexts(self) -> List[Dict[str, Any]]:
        """List all available contexts."""
        contexts = []
        for context_file in self.context_dir.glob("*.json"):
            try:
                with open(context_file, 'r') as f:
                    data = json.load(f)
                contexts.append({
                    "session_id": data.get("session_id"),
                    "plugin_name": data.get("plugin_name"),
                    "current_phase": data.get("current_phase"),
                    "start_time": data.get("start_time"),
                    "progress": len(data.get("phases_completed", [])) / 7 * 100
                })
            except Exception as e:
                logger.warning(f"Failed to read context file {context_file}: {e}")
        return sorted(contexts, key=lambda x: x.get("start_time", ""), reverse=True)
    
    def cleanup_old_contexts(self, max_age_days: int = 30):
        """Clean up old context files."""
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        for context_file in self.context_dir.glob("*.json"):
            if context_file.stat().st_mtime < cutoff_time:
                try:
                    context_file.unlink()
                    logger.debug(f"Cleaned up old context: {context_file}")
                except Exception as e:
                    logger.warning(f"Failed to delete old context {context_file}: {e}")


class ContextualAgent:
    """Base class for agents that use context injection."""
    
    def __init__(self, name: str, context_manager: ContextManager):
        self.name = name
        self.context_manager = context_manager
    
    def get_context(self) -> Optional[PluginGenerationContext]:
        """Get current context."""
        return self.context_manager.get_context()
    
    def update_context(self, **updates):
        """Update current context."""
        context = self.get_context()
        if context:
            context.current_agent = self.name
            self.context_manager.update_context(context.session_id, **updates)
    
    def log_message(self, message: str, message_type: str = "info"):
        """Log a message to the context."""
        context = self.get_context()
        if context:
            context.add_agent_message(self.name, message, message_type)
            self.context_manager.update_context(context.session_id)
    
    def log_error(self, error_type: str, message: str):
        """Log an error to the context."""
        context = self.get_context()
        if context:
            context.add_error(error_type, message, self.name)
            self.context_manager.update_context(context.session_id)
    
    def mark_phase_complete(self, phase: str):
        """Mark a phase as completed."""
        context = self.get_context()
        if context:
            context.mark_phase_complete(phase)
            self.context_manager.update_context(context.session_id)


# Global context manager instance
context_manager = ContextManager()


def get_context_instructions(context: PluginGenerationContext) -> str:
    """Generate dynamic instructions based on context."""
    instructions = []
    
    if context.plugin_name:
        instructions.append(f"Working on plugin: {context.plugin_name}")
    
    if context.current_phase:
        instructions.append(f"Current phase: {context.current_phase}")
    
    if context.errors_encountered:
        recent_errors = context.errors_encountered[-3:]  # Last 3 errors
        instructions.append(f"Recent errors to avoid: {[e['message'] for e in recent_errors]}")
    
    if context.user_preferences:
        instructions.append(f"User preferences: {context.user_preferences}")
    
    if context.advanced_tests_requested:
        instructions.append(f"Advanced tests requested: {context.advanced_tests_requested}")
    
    progress = context.get_progress_percentage()
    instructions.append(f"Progress: {progress:.1f}% complete")
    
    return "\n".join(instructions)


def create_contextual_agent_function(agent_func, context_manager: ContextManager):
    """Decorator to inject context into agent functions."""
    def wrapper(*args, **kwargs):
        # Get current context
        context = context_manager.get_context()
        
        # Add context to kwargs if not already present
        if context and 'context' not in kwargs:
            kwargs['context'] = context
        
        # Call original function
        return agent_func(*args, **kwargs)
    
    return wrapper