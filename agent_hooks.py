"""
Agent Hooks system for WordPress Plugin Generator.
Implements lifecycle hooks for monitoring, logging, and error handling following OpenAI Agents Python best practices.
"""

import time
import json
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from loguru import logger

from context_manager import context_manager, PluginGenerationContext
from security_guardrails import security_guardrails, input_guardrail, output_guardrail


class HookType(Enum):
    """Types of hooks available."""
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    HANDOFF = "handoff"
    ERROR = "error"
    VALIDATION = "validation"
    SECURITY_CHECK = "security_check"


@dataclass
class HookEvent:
    """Represents a hook event."""
    hook_type: HookType
    agent_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    tool_name: Optional[str] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    success: bool = True


class PluginGeneratorHooks:
    """Hooks implementation for WordPress Plugin Generator."""
    
    def __init__(self):
        self.events: List[HookEvent] = []
        self.performance_metrics: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
        self.active_operations: Dict[str, datetime] = {}
        self.callbacks: Dict[HookType, List[Callable]] = {hook_type: [] for hook_type in HookType}
    
    def register_callback(self, hook_type: HookType, callback: Callable):
        """Register a callback for a specific hook type."""
        self.callbacks[hook_type].append(callback)
        logger.debug(f"Registered callback for {hook_type.value}")
    
    def trigger_callbacks(self, event: HookEvent):
        """Trigger all callbacks for a hook event."""
        for callback in self.callbacks.get(event.hook_type, []):
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Hook callback failed: {e}")
    
    def on_agent_start(self, agent_name: str, context: Optional[PluginGenerationContext] = None):
        """Called when an agent starts execution."""
        start_time = datetime.now()
        self.active_operations[agent_name] = start_time
        
        # Update context
        if context:
            context.current_agent = agent_name
            context.add_agent_message(agent_name, "Agent started", "info")
            context_manager.update_context(context.session_id)
        
        # Create event
        event = HookEvent(
            hook_type=HookType.AGENT_START,
            agent_name=agent_name,
            timestamp=start_time,
            metadata={
                "session_id": context.session_id if context else None,
                "phase": context.current_phase if context else "unknown"
            }
        )
        
        self.events.append(event)
        self.trigger_callbacks(event)
        
        logger.info(f"🚀 Agent started: {agent_name}")
    
    def on_agent_end(self, agent_name: str, success: bool = True, error: Optional[str] = None, context: Optional[PluginGenerationContext] = None):
        """Called when an agent ends execution."""
        end_time = datetime.now()
        
        # Calculate duration
        duration = None
        if agent_name in self.active_operations:
            start_time = self.active_operations.pop(agent_name)
            duration = (end_time - start_time).total_seconds()
            
            # Track performance metrics
            if agent_name not in self.performance_metrics:
                self.performance_metrics[agent_name] = []
            self.performance_metrics[agent_name].append(duration)
        
        # Update context
        if context:
            message = "Agent completed successfully" if success else f"Agent failed: {error}"
            message_type = "success" if success else "error"
            context.add_agent_message(agent_name, message, message_type)
            
            if error:
                context.add_error("agent_execution", error, agent_name)
            
            context_manager.update_context(context.session_id)
        
        # Track error counts
        if not success and error:
            self.error_counts[agent_name] = self.error_counts.get(agent_name, 0) + 1
        
        # Create event
        event = HookEvent(
            hook_type=HookType.AGENT_END,
            agent_name=agent_name,
            timestamp=end_time,
            duration=duration,
            success=success,
            error=error,
            metadata={
                "session_id": context.session_id if context else None,
                "phase": context.current_phase if context else "unknown",
                "performance_avg": sum(self.performance_metrics.get(agent_name, [0])) / len(self.performance_metrics.get(agent_name, [1])) if self.performance_metrics.get(agent_name) else 0
            }
        )
        
        self.events.append(event)
        self.trigger_callbacks(event)
        
        status = "✅" if success else "❌"
        duration_str = f" ({duration:.2f}s)" if duration else ""
        logger.info(f"{status} Agent ended: {agent_name}{duration_str}")
        
        if error:
            logger.error(f"Agent error: {error}")
    
    def on_tool_start(self, tool_name: str, agent_name: str, context: Optional[PluginGenerationContext] = None):
        """Called when a tool starts execution."""
        start_time = datetime.now()
        operation_key = f"{agent_name}:{tool_name}"
        self.active_operations[operation_key] = start_time
        
        # Update context
        if context:
            context.add_agent_message(agent_name, f"Using tool: {tool_name}", "info")
            context_manager.update_context(context.session_id)
        
        # Create event
        event = HookEvent(
            hook_type=HookType.TOOL_START,
            agent_name=agent_name,
            tool_name=tool_name,
            timestamp=start_time,
            metadata={
                "session_id": context.session_id if context else None,
                "phase": context.current_phase if context else "unknown"
            }
        )
        
        self.events.append(event)
        self.trigger_callbacks(event)
        
        logger.debug(f"🔧 Tool started: {tool_name} (agent: {agent_name})")
    
    def on_tool_end(self, tool_name: str, agent_name: str, success: bool = True, error: Optional[str] = None, result: Optional[Any] = None, context: Optional[PluginGenerationContext] = None):
        """Called when a tool ends execution."""
        end_time = datetime.now()
        operation_key = f"{agent_name}:{tool_name}"
        
        # Calculate duration
        duration = None
        if operation_key in self.active_operations:
            start_time = self.active_operations.pop(operation_key)
            duration = (end_time - start_time).total_seconds()
        
        # Update context
        if context:
            message = f"Tool {tool_name} completed" if success else f"Tool {tool_name} failed: {error}"
            message_type = "success" if success else "error"
            context.add_agent_message(agent_name, message, message_type)
            
            if error:
                context.add_error("tool_execution", error, agent_name)
            
            context_manager.update_context(context.session_id)
        
        # Security validation for certain tools
        if success and tool_name in ["generate_plugin_files", "write_file"] and result:
            try:
                self.on_security_check(tool_name, agent_name, result, context)
            except Exception as e:
                logger.warning(f"Security check failed for {tool_name}: {e}")
        
        # Create event
        event = HookEvent(
            hook_type=HookType.TOOL_END,
            agent_name=agent_name,
            tool_name=tool_name,
            timestamp=end_time,
            duration=duration,
            success=success,
            error=error,
            metadata={
                "session_id": context.session_id if context else None,
                "phase": context.current_phase if context else "unknown",
                "result_size": len(str(result)) if result else 0
            }
        )
        
        self.events.append(event)
        self.trigger_callbacks(event)
        
        status = "✅" if success else "❌"
        duration_str = f" ({duration:.2f}s)" if duration else ""
        logger.debug(f"{status} Tool ended: {tool_name}{duration_str}")
        
        if error:
            logger.error(f"Tool error: {error}")
    
    def on_handoff(self, from_agent: str, to_agent: str, context: Optional[PluginGenerationContext] = None):
        """Called when control is handed off between agents."""
        # Update context
        if context:
            context.current_agent = to_agent
            context.add_agent_message(from_agent, f"Handing off to {to_agent}", "info")
            context_manager.update_context(context.session_id)
        
        # Create event
        event = HookEvent(
            hook_type=HookType.HANDOFF,
            agent_name=from_agent,
            timestamp=datetime.now(),
            metadata={
                "to_agent": to_agent,
                "session_id": context.session_id if context else None,
                "phase": context.current_phase if context else "unknown"
            }
        )
        
        self.events.append(event)
        self.trigger_callbacks(event)
        
        logger.info(f"🔄 Handoff: {from_agent} → {to_agent}")
    
    def on_error(self, error_type: str, message: str, agent_name: str, context: Optional[PluginGenerationContext] = None):
        """Called when an error occurs."""
        # Update context
        if context:
            context.add_error(error_type, message, agent_name)
            context_manager.update_context(context.session_id)
        
        # Create event
        event = HookEvent(
            hook_type=HookType.ERROR,
            agent_name=agent_name,
            timestamp=datetime.now(),
            success=False,
            error=message,
            metadata={
                "error_type": error_type,
                "session_id": context.session_id if context else None,
                "phase": context.current_phase if context else "unknown"
            }
        )
        
        self.events.append(event)
        self.trigger_callbacks(event)
        
        logger.error(f"❌ Error in {agent_name}: {message}")
    
    def on_security_check(self, tool_name: str, agent_name: str, content: Any, context: Optional[PluginGenerationContext] = None):
        """Called to perform security checks on content."""
        try:
            # Perform security validation
            violations = []
            
            if isinstance(content, str):
                violations = output_guardrail(content, "code", context)
            elif isinstance(content, list) and all(isinstance(item, dict) for item in content):
                # Handle plugin files
                violations = security_guardrails.validate_output(json.dumps(content), "plugin_files", context)
            
            # Update context with security results
            if context and violations:
                for violation in violations:
                    context.add_error("security_violation", violation.message, agent_name)
                context_manager.update_context(context.session_id)
            
            # Create event
            event = HookEvent(
                hook_type=HookType.SECURITY_CHECK,
                agent_name=agent_name,
                tool_name=tool_name,
                timestamp=datetime.now(),
                success=len(violations) == 0,
                metadata={
                    "violations_count": len(violations),
                    "session_id": context.session_id if context else None,
                    "phase": context.current_phase if context else "unknown"
                }
            )
            
            self.events.append(event)
            self.trigger_callbacks(event)
            
            if violations:
                logger.warning(f"🔒 Security violations detected in {tool_name}: {len(violations)} issues")
            else:
                logger.debug(f"🔒 Security check passed for {tool_name}")
                
        except Exception as e:
            logger.error(f"Security check failed: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all agents."""
        summary = {}
        
        for agent_name, times in self.performance_metrics.items():
            if times:
                summary[agent_name] = {
                    "avg_duration": sum(times) / len(times),
                    "min_duration": min(times),
                    "max_duration": max(times),
                    "total_runs": len(times),
                    "total_time": sum(times)
                }
        
        return summary
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary for all agents."""
        return {
            "error_counts": self.error_counts.copy(),
            "total_errors": sum(self.error_counts.values()),
            "most_errors": max(self.error_counts.items(), key=lambda x: x[1]) if self.error_counts else None
        }
    
    def get_session_report(self, session_id: str) -> Dict[str, Any]:
        """Get detailed report for a specific session."""
        session_events = [e for e in self.events if e.metadata.get("session_id") == session_id]
        
        if not session_events:
            return {"error": "No events found for session"}
        
        # Analyze events
        agents_used = list(set(e.agent_name for e in session_events))
        tools_used = list(set(e.tool_name for e in session_events if e.tool_name))
        errors = [e for e in session_events if not e.success]
        
        # Calculate total duration
        start_time = min(e.timestamp for e in session_events)
        end_time = max(e.timestamp for e in session_events)
        total_duration = (end_time - start_time).total_seconds()
        
        return {
            "session_id": session_id,
            "total_duration": total_duration,
            "agents_used": agents_used,
            "tools_used": tools_used,
            "total_events": len(session_events),
            "errors": len(errors),
            "success_rate": (len(session_events) - len(errors)) / len(session_events) * 100 if session_events else 0,
            "timeline": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "type": e.hook_type.value,
                    "agent": e.agent_name,
                    "tool": e.tool_name,
                    "success": e.success,
                    "duration": e.duration
                }
                for e in session_events
            ]
        }
    
    def clear_old_events(self, max_age_hours: int = 24):
        """Clear events older than specified hours."""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        old_count = len(self.events)
        self.events = [e for e in self.events if e.timestamp.timestamp() > cutoff_time]
        new_count = len(self.events)
        
        if old_count > new_count:
            logger.info(f"Cleared {old_count - new_count} old events")


# Global hooks instance
plugin_hooks = PluginGeneratorHooks()


# Convenience functions for easy integration
def on_agent_start(agent_name: str, context: Optional[PluginGenerationContext] = None):
    """Convenience function for agent start hook."""
    plugin_hooks.on_agent_start(agent_name, context)


def on_agent_end(agent_name: str, success: bool = True, error: Optional[str] = None, context: Optional[PluginGenerationContext] = None):
    """Convenience function for agent end hook."""
    plugin_hooks.on_agent_end(agent_name, success, error, context)


def on_tool_start(tool_name: str, agent_name: str, context: Optional[PluginGenerationContext] = None):
    """Convenience function for tool start hook."""
    plugin_hooks.on_tool_start(tool_name, agent_name, context)


def on_tool_end(tool_name: str, agent_name: str, success: bool = True, error: Optional[str] = None, result: Optional[Any] = None, context: Optional[PluginGenerationContext] = None):
    """Convenience function for tool end hook."""
    plugin_hooks.on_tool_end(tool_name, agent_name, success, error, result, context)


def on_handoff(from_agent: str, to_agent: str, context: Optional[PluginGenerationContext] = None):
    """Convenience function for handoff hook."""
    plugin_hooks.on_handoff(from_agent, to_agent, context)


def on_error(error_type: str, message: str, agent_name: str, context: Optional[PluginGenerationContext] = None):
    """Convenience function for error hook."""
    plugin_hooks.on_error(error_type, message, agent_name, context)


# Example callback functions
def log_performance_callback(event: HookEvent):
    """Example callback to log performance metrics."""
    if event.hook_type == HookType.AGENT_END and event.duration:
        if event.duration > 30:  # Log slow operations
            logger.warning(f"Slow agent execution: {event.agent_name} took {event.duration:.2f}s")


def security_alert_callback(event: HookEvent):
    """Example callback to alert on security issues."""
    if event.hook_type == HookType.SECURITY_CHECK and not event.success:
        logger.critical(f"Security violation detected in {event.agent_name}: {event.tool_name}")


# Register default callbacks
plugin_hooks.register_callback(HookType.AGENT_END, log_performance_callback)
plugin_hooks.register_callback(HookType.SECURITY_CHECK, security_alert_callback)