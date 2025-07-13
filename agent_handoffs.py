"""
Agent Handoffs system for WordPress Plugin Generator.
Implements structured handoffs between agents following OpenAI Agents Python best practices.
"""

import json
from typing import Dict, Any, Optional, List, Type, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from loguru import logger

from agents import Agent, handoff
from context_manager import context_manager, PluginGenerationContext
from agent_hooks import on_handoff


class HandoffType(Enum):
    """Types of handoffs available."""
    SPECIFICATION = "specification"
    GENERATION = "generation"
    COMPLIANCE = "compliance"
    TESTING = "testing"
    SECURITY = "security"
    COMPLETION = "completion"


@dataclass
class HandoffMetadata:
    """Metadata for handoff operations."""
    from_agent: str
    to_agent: str
    handoff_type: HandoffType
    timestamp: datetime = field(default_factory=datetime.now)
    context_data: Dict[str, Any] = field(default_factory=dict)
    validation_results: Optional[Dict[str, Any]] = None
    security_clearance: bool = True
    previous_errors: List[str] = field(default_factory=list)


class HandoffManager:
    """Manages handoffs between agents in the WordPress plugin generation workflow."""
    
    def __init__(self):
        self.handoff_chain: List[HandoffMetadata] = []
        self.current_agent: Optional[str] = None
        self.workflow_state: Dict[str, Any] = {}
    
    def create_handoff(self, 
                      from_agent: str, 
                      to_agent: str, 
                      handoff_type: HandoffType,
                      context: Optional[PluginGenerationContext] = None,
                      validation_data: Optional[Dict[str, Any]] = None,
                      filter_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a handoff with proper data filtering and validation.
        
        Args:
            from_agent: Name of the agent initiating the handoff
            to_agent: Name of the agent receiving the handoff
            handoff_type: Type of handoff being performed
            context: Current plugin generation context
            validation_data: Data to validate before handoff
            filter_data: Data to filter and pass to the next agent
            
        Returns:
            Dictionary with handoff information and filtered data
        """
        
        # Validate handoff
        validation_result = self._validate_handoff(from_agent, to_agent, handoff_type, context, validation_data)
        
        if not validation_result["valid"]:
            logger.error(f"Handoff validation failed: {validation_result['error']}")
            return {
                "success": False,
                "error": validation_result["error"],
                "from_agent": from_agent,
                "to_agent": to_agent
            }
        
        # Filter data for the next agent
        filtered_data = self._filter_handoff_data(handoff_type, filter_data or {}, context)
        
        # Create handoff metadata
        handoff_metadata = HandoffMetadata(
            from_agent=from_agent,
            to_agent=to_agent,
            handoff_type=handoff_type,
            context_data=filtered_data,
            validation_results=validation_result,
            previous_errors=context.errors_encountered[-5:] if context else []
        )
        
        # Record handoff
        self.handoff_chain.append(handoff_metadata)
        self.current_agent = to_agent
        
        # Update workflow state
        self.workflow_state[handoff_type.value] = {
            "completed": True,
            "agent": from_agent,
            "timestamp": datetime.now().isoformat(),
            "data": filtered_data
        }
        
        # Trigger handoff hook
        on_handoff(from_agent, to_agent, context)
        
        # Update context
        if context:
            context.current_agent = to_agent
            context.add_agent_message(from_agent, f"Handing off to {to_agent} for {handoff_type.value}", "handoff")
            context_manager.update_context(context.session_id)
        
        logger.info(f"🔄 Handoff created: {from_agent} → {to_agent} ({handoff_type.value})")
        
        return {
            "success": True,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "handoff_type": handoff_type.value,
            "filtered_data": filtered_data,
            "handoff_id": len(self.handoff_chain) - 1,
            "instructions": self._get_handoff_instructions(handoff_type, context, filtered_data)
        }
    
    def _validate_handoff(self, from_agent: str, to_agent: str, handoff_type: HandoffType, 
                         context: Optional[PluginGenerationContext], 
                         validation_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate handoff prerequisites."""
        
        # Check if agents are valid
        valid_agents = [
            "Plugin Manager Agent",
            "Plugin Specification Agent", 
            "Plugin File Generator Agent",
            "Plugin Compliance Agent",
            "Plugin Testing Agent"
        ]
        
        if from_agent not in valid_agents or to_agent not in valid_agents:
            return {"valid": False, "error": f"Invalid agent names: {from_agent} → {to_agent}"}
        
        # Check handoff sequence
        sequence_validation = self._validate_handoff_sequence(handoff_type, context)
        if not sequence_validation["valid"]:
            return sequence_validation
        
        # Validate data requirements
        data_validation = self._validate_handoff_data(handoff_type, validation_data)
        if not data_validation["valid"]:
            return data_validation
        
        # Check context state
        if context and context.current_phase == "failed":
            return {"valid": False, "error": "Cannot perform handoff in failed state"}
        
        return {"valid": True, "message": "Handoff validation passed"}
    
    def _validate_handoff_sequence(self, handoff_type: HandoffType, context: Optional[PluginGenerationContext]) -> Dict[str, Any]:
        """Validate that handoff follows correct sequence."""
        
        if not context:
            return {"valid": True, "message": "No context to validate sequence"}
        
        # Define valid sequences
        valid_sequences = {
            HandoffType.SPECIFICATION: [],  # Can be first
            HandoffType.GENERATION: [HandoffType.SPECIFICATION],
            HandoffType.COMPLIANCE: [HandoffType.GENERATION],
            HandoffType.TESTING: [HandoffType.COMPLIANCE],
            HandoffType.SECURITY: [HandoffType.GENERATION, HandoffType.COMPLIANCE],
            HandoffType.COMPLETION: [HandoffType.TESTING, HandoffType.SECURITY]
        }
        
        required_previous = valid_sequences.get(handoff_type, [])
        
        if not required_previous:
            return {"valid": True, "message": "No prerequisites required"}
        
        # Check if required previous handoffs have occurred
        completed_types = [h.handoff_type for h in self.handoff_chain]
        
        for required_type in required_previous:
            if required_type not in completed_types:
                return {
                    "valid": False, 
                    "error": f"Handoff {handoff_type.value} requires {required_type.value} to be completed first"
                }
        
        return {"valid": True, "message": "Sequence validation passed"}
    
    def _validate_handoff_data(self, handoff_type: HandoffType, validation_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate data requirements for handoff."""
        
        if not validation_data:
            return {"valid": True, "message": "No data to validate"}
        
        # Define required fields for each handoff type
        required_fields = {
            HandoffType.SPECIFICATION: ["name", "description"],
            HandoffType.GENERATION: ["name", "slug", "features"],
            HandoffType.COMPLIANCE: ["files"],
            HandoffType.TESTING: ["files"],
            HandoffType.SECURITY: ["files", "content"],
            HandoffType.COMPLETION: ["results"]
        }
        
        required = required_fields.get(handoff_type, [])
        
        missing_fields = [field for field in required if field not in validation_data]
        
        if missing_fields:
            return {
                "valid": False,
                "error": f"Missing required fields for {handoff_type.value}: {', '.join(missing_fields)}"
            }
        
        return {"valid": True, "message": "Data validation passed"}
    
    def _filter_handoff_data(self, handoff_type: HandoffType, data: Dict[str, Any], 
                            context: Optional[PluginGenerationContext]) -> Dict[str, Any]:
        """Filter data passed to the next agent."""
        
        # Base filtering - include context information
        filtered_data = {}
        
        if context:
            filtered_data["context"] = {
                "session_id": context.session_id,
                "plugin_name": context.plugin_name,
                "plugin_slug": context.plugin_slug,
                "current_phase": context.current_phase,
                "progress": context.get_progress_percentage(),
                "advanced_tests_requested": context.advanced_tests_requested
            }
        
        # Type-specific filtering
        if handoff_type == HandoffType.SPECIFICATION:
            # Pass only essential specification data
            filtered_data.update({
                "user_input": data.get("user_input", ""),
                "requirements": data.get("requirements", []),
                "preferences": data.get("preferences", {})
            })
        
        elif handoff_type == HandoffType.GENERATION:
            # Pass plugin specification
            filtered_data.update({
                "plugin_spec": data.get("plugin_spec", {}),
                "requirements": data.get("requirements", []),
                "features": data.get("features", [])
            })
        
        elif handoff_type == HandoffType.COMPLIANCE:
            # Pass generated files for compliance checking
            filtered_data.update({
                "generated_files": data.get("generated_files", []),
                "plugin_spec": data.get("plugin_spec", {}),
                "file_paths": data.get("file_paths", [])
            })
        
        elif handoff_type == HandoffType.TESTING:
            # Pass files and compliance results
            filtered_data.update({
                "generated_files": data.get("generated_files", []),
                "compliance_results": data.get("compliance_results", {}),
                "file_paths": data.get("file_paths", [])
            })
        
        elif handoff_type == HandoffType.SECURITY:
            # Pass files and content for security analysis
            filtered_data.update({
                "generated_files": data.get("generated_files", []),
                "file_content": data.get("file_content", ""),
                "compliance_results": data.get("compliance_results", {})
            })
        
        elif handoff_type == HandoffType.COMPLETION:
            # Pass all results for final report
            filtered_data.update({
                "plugin_spec": data.get("plugin_spec", {}),
                "generated_files": data.get("generated_files", []),
                "compliance_results": data.get("compliance_results", {}),
                "test_results": data.get("test_results", {}),
                "security_results": data.get("security_results", {}),
                "file_paths": data.get("file_paths", [])
            })
        
        return filtered_data
    
    def _get_handoff_instructions(self, handoff_type: HandoffType, context: Optional[PluginGenerationContext], 
                                 filtered_data: Dict[str, Any]) -> str:
        """Get specific instructions for the receiving agent."""
        
        base_instructions = {
            HandoffType.SPECIFICATION: "Analyze the user requirements and create a detailed plugin specification.",
            HandoffType.GENERATION: "Generate complete plugin files based on the provided specification.",
            HandoffType.COMPLIANCE: "Review the generated files for WordPress compliance and coding standards.",
            HandoffType.TESTING: "Perform comprehensive testing of the generated plugin files.",
            HandoffType.SECURITY: "Conduct security analysis and vulnerability assessment.",
            HandoffType.COMPLETION: "Compile final report and prepare plugin for delivery."
        }
        
        instruction = base_instructions.get(handoff_type, "Process the provided data.")
        
        # Add context-specific instructions
        if context:
            if context.errors_encountered:
                instruction += f"\n\nNote: Previous errors encountered: {len(context.errors_encountered)} issues. Please address these patterns."
            
            if context.advanced_tests_requested:
                instruction += f"\n\nAdvanced testing requested: {', '.join(context.advanced_tests_requested)}"
        
        # Add data-specific instructions
        if filtered_data.get("requirements"):
            instruction += f"\n\nSpecific requirements: {len(filtered_data['requirements'])} items to address."
        
        return instruction
    
    def get_handoff_history(self) -> List[Dict[str, Any]]:
        """Get history of all handoffs."""
        return [
            {
                "from_agent": h.from_agent,
                "to_agent": h.to_agent,
                "handoff_type": h.handoff_type.value,
                "timestamp": h.timestamp.isoformat(),
                "data_size": len(str(h.context_data)),
                "security_clearance": h.security_clearance,
                "previous_errors": len(h.previous_errors)
            }
            for h in self.handoff_chain
        ]
    
    def get_workflow_state(self) -> Dict[str, Any]:
        """Get current workflow state."""
        return {
            "current_agent": self.current_agent,
            "completed_handoffs": len(self.handoff_chain),
            "workflow_state": self.workflow_state,
            "handoff_chain": self.get_handoff_history()
        }
    
    def reset_workflow(self):
        """Reset workflow state."""
        self.handoff_chain.clear()
        self.current_agent = None
        self.workflow_state.clear()
        logger.info("Workflow state reset")


# Global handoff manager instance
handoff_manager = HandoffManager()


def create_agent_handoff(to_agent_name: str, handoff_type: HandoffType, 
                        from_agent: str, context: Optional[PluginGenerationContext] = None,
                        validation_data: Optional[Dict[str, Any]] = None,
                        filter_data: Optional[Dict[str, Any]] = None):
    """
    Create a handoff to another agent.
    
    Args:
        to_agent_name: Name of the agent to hand off to
        handoff_type: Type of handoff being performed
        from_agent: Name of the agent initiating the handoff
        context: Current plugin generation context
        validation_data: Data to validate before handoff
        filter_data: Data to filter and pass to the next agent
        
    Returns:
        Handoff object that can be used as a tool
    """
    
    def on_handoff_callback(input_data: Dict[str, Any]):
        """Callback function executed when handoff is invoked."""
        
        # Create handoff with proper data filtering
        handoff_result = handoff_manager.create_handoff(
            from_agent=from_agent,
            to_agent=to_agent_name,
            handoff_type=handoff_type,
            context=context,
            validation_data=validation_data,
            filter_data=filter_data or input_data
        )
        
        if not handoff_result["success"]:
            logger.error(f"Handoff failed: {handoff_result['error']}")
            return handoff_result
        
        return handoff_result
    
    # Create handoff with proper configuration
    return handoff(
        agent=to_agent_name,
        tool_name_override=f"handoff_to_{to_agent_name.lower().replace(' ', '_')}",
        tool_description_override=f"Hand off workflow to {to_agent_name} for {handoff_type.value}",
        on_handoff=on_handoff_callback,
        input_filter=lambda data: handoff_manager._filter_handoff_data(handoff_type, data, context),
        is_enabled=True
    )


def get_handoff_tools(current_agent: str, context: Optional[PluginGenerationContext] = None) -> List[Any]:
    """
    Get handoff tools for the current agent.
    
    Args:
        current_agent: Name of the current agent
        context: Current plugin generation context
        
    Returns:
        List of handoff tools available to the current agent
    """
    
    handoff_tools = []
    
    # Define handoff flows for each agent
    handoff_flows = {
        "Plugin Manager Agent": [
            ("Plugin Specification Agent", HandoffType.SPECIFICATION),
            ("Plugin File Generator Agent", HandoffType.GENERATION),
            ("Plugin Compliance Agent", HandoffType.COMPLIANCE),
            ("Plugin Testing Agent", HandoffType.TESTING),
        ],
        "Plugin Specification Agent": [
            ("Plugin File Generator Agent", HandoffType.GENERATION),
            ("Plugin Manager Agent", HandoffType.COMPLETION),
        ],
        "Plugin File Generator Agent": [
            ("Plugin Compliance Agent", HandoffType.COMPLIANCE),
            ("Plugin Manager Agent", HandoffType.COMPLETION),
        ],
        "Plugin Compliance Agent": [
            ("Plugin Testing Agent", HandoffType.TESTING),
            ("Plugin Manager Agent", HandoffType.COMPLETION),
        ],
        "Plugin Testing Agent": [
            ("Plugin Manager Agent", HandoffType.COMPLETION),
        ]
    }
    
    # Get available handoffs for current agent
    available_handoffs = handoff_flows.get(current_agent, [])
    
    for to_agent, handoff_type in available_handoffs:
        handoff_tool = create_agent_handoff(
            to_agent_name=to_agent,
            handoff_type=handoff_type,
            from_agent=current_agent,
            context=context
        )
        handoff_tools.append(handoff_tool)
    
    return handoff_tools