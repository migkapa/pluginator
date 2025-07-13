"""
Handoff tools for WordPress Plugin Generator agents.
Provides function tools for managing agent handoffs and workflow coordination.
"""

from typing import Dict, Any, Optional, List
from agents import function_tool
from loguru import logger

from agent_handoffs import handoff_manager, HandoffType
from context_manager import context_manager


@function_tool
def initiate_handoff(to_agent: str, handoff_type: str, data: str, validation_data: str = "") -> Dict[str, Any]:
    """
    Initiate a handoff to another agent.
    
    Args:
        to_agent: Name of the agent to hand off to
        handoff_type: Type of handoff (specification, generation, compliance, testing, security, completion)
        data: JSON string containing data to pass to the next agent
        validation_data: JSON string containing data to validate before handoff
        
    Returns:
        Dictionary with handoff results
    """
    try:
        logger.info(f"Initiating handoff to {to_agent} for {handoff_type}")
        
        # Parse JSON inputs
        import json
        try:
            data_dict = json.loads(data) if data else {}
        except json.JSONDecodeError:
            return {"success": False, "error": "Invalid JSON in data parameter"}
        
        try:
            validation_dict = json.loads(validation_data) if validation_data else {}
        except json.JSONDecodeError:
            return {"success": False, "error": "Invalid JSON in validation_data parameter"}
        
        # Get current context
        context = context_manager.get_context()
        
        # Convert string to HandoffType enum
        try:
            handoff_type_enum = HandoffType(handoff_type)
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid handoff type: {handoff_type}",
                "valid_types": [t.value for t in HandoffType]
            }
        
        # Determine current agent from context
        current_agent = context.current_agent if context else "Unknown Agent"
        
        # Create handoff
        handoff_result = handoff_manager.create_handoff(
            from_agent=current_agent,
            to_agent=to_agent,
            handoff_type=handoff_type_enum,
            context=context,
            validation_data=validation_dict or data_dict,
            filter_data=data_dict
        )
        
        if handoff_result["success"]:
            logger.info(f"✅ Handoff successful: {current_agent} → {to_agent}")
        else:
            logger.error(f"❌ Handoff failed: {handoff_result.get('error', 'Unknown error')}")
        
        return handoff_result
        
    except Exception as e:
        logger.error(f"Failed to initiate handoff: {e}")
        return {
            "success": False,
            "error": str(e),
            "to_agent": to_agent,
            "handoff_type": handoff_type
        }


@function_tool
def get_handoff_status() -> Dict[str, Any]:
    """
    Get the current handoff status and workflow state.
    
    Returns:
        Dictionary with current handoff status and workflow information
    """
    try:
        logger.info("Getting handoff status...")
        
        # Get workflow state
        workflow_state = handoff_manager.get_workflow_state()
        
        # Get context information
        context = context_manager.get_context()
        context_info = {}
        if context:
            context_info = {
                "session_id": context.session_id,
                "plugin_name": context.plugin_name,
                "current_phase": context.current_phase,
                "progress": context.get_progress_percentage(),
                "current_agent": context.current_agent,
                "phases_completed": context.phases_completed
            }
        
        # Get handoff history
        handoff_history = handoff_manager.get_handoff_history()
        
        # Calculate handoff statistics
        total_handoffs = len(handoff_history)
        successful_handoffs = sum(1 for h in handoff_history if h.get("security_clearance", True))
        
        result = {
            "workflow_state": workflow_state,
            "context_info": context_info,
            "handoff_history": handoff_history,
            "statistics": {
                "total_handoffs": total_handoffs,
                "successful_handoffs": successful_handoffs,
                "success_rate": (successful_handoffs / total_handoffs * 100) if total_handoffs > 0 else 100
            },
            "next_recommended_handoffs": _get_recommended_handoffs(workflow_state, context)
        }
        
        logger.info(f"Handoff status retrieved. Total handoffs: {total_handoffs}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to get handoff status: {e}")
        return {
            "workflow_state": {},
            "context_info": {},
            "handoff_history": [],
            "statistics": {},
            "next_recommended_handoffs": [],
            "error": str(e)
        }


@function_tool
def validate_handoff_data(handoff_type: str, data: str) -> Dict[str, Any]:
    """
    Validate data before performing a handoff.
    
    Args:
        handoff_type: Type of handoff to validate for
        data: JSON string containing data to validate
        
    Returns:
        Dictionary with validation results
    """
    try:
        logger.info(f"Validating handoff data for {handoff_type}")
        
        # Parse JSON input
        import json
        try:
            data_dict = json.loads(data) if data else {}
        except json.JSONDecodeError:
            return {"valid": False, "error": "Invalid JSON in data parameter"}
        
        # Convert string to HandoffType enum
        try:
            handoff_type_enum = HandoffType(handoff_type)
        except ValueError:
            return {
                "valid": False,
                "error": f"Invalid handoff type: {handoff_type}",
                "valid_types": [t.value for t in HandoffType]
            }
        
        # Get context
        context = context_manager.get_context()
        
        # Validate data using handoff manager
        validation_result = handoff_manager._validate_handoff_data(handoff_type_enum, data_dict)
        
        # Additional validation checks
        additional_checks = _perform_additional_validation(handoff_type_enum, data_dict, context)
        
        # Combine results
        result = {
            "valid": validation_result["valid"] and additional_checks["valid"],
            "handoff_type": handoff_type,
            "data_size": len(str(data_dict)),
            "validation_details": validation_result,
            "additional_checks": additional_checks,
            "recommendations": _get_validation_recommendations(handoff_type_enum, data_dict, validation_result, additional_checks)
        }
        
        if not result["valid"]:
            logger.warning(f"Handoff data validation failed for {handoff_type}")
        else:
            logger.info(f"Handoff data validation passed for {handoff_type}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to validate handoff data: {e}")
        return {
            "valid": False,
            "error": str(e),
            "handoff_type": handoff_type,
            "data_size": len(str(data_dict)),
            "validation_details": {},
            "additional_checks": {},
            "recommendations": ["Fix validation errors and retry"]
        }


@function_tool
def reset_handoff_workflow() -> Dict[str, Any]:
    """
    Reset the handoff workflow state.
    
    Returns:
        Dictionary with reset confirmation
    """
    try:
        logger.info("Resetting handoff workflow...")
        
        # Get current state before reset
        current_state = handoff_manager.get_workflow_state()
        
        # Reset workflow
        handoff_manager.reset_workflow()
        
        # Update context if available
        context = context_manager.get_context()
        if context:
            context.current_agent = None
            context.add_agent_message("System", "Workflow reset", "info")
            context_manager.update_context(context.session_id)
        
        result = {
            "success": True,
            "message": "Handoff workflow reset successfully",
            "previous_state": current_state,
            "reset_timestamp": handoff_manager.handoff_chain[0].timestamp.isoformat() if handoff_manager.handoff_chain else None
        }
        
        logger.info("✅ Handoff workflow reset successfully")
        return result
        
    except Exception as e:
        logger.error(f"Failed to reset handoff workflow: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to reset handoff workflow"
        }


def _get_recommended_handoffs(workflow_state: Dict[str, Any], context) -> List[Dict[str, str]]:
    """Get recommended next handoffs based on current state."""
    recommendations = []
    
    completed_states = workflow_state.get("workflow_state", {})
    current_agent = workflow_state.get("current_agent", "")
    
    # Define handoff sequence
    handoff_sequence = [
        ("specification", "Plugin Specification Agent"),
        ("generation", "Plugin File Generator Agent"),
        ("compliance", "Plugin Compliance Agent"),
        ("testing", "Plugin Testing Agent"),
        ("completion", "Plugin Manager Agent")
    ]
    
    # Find next recommended handoffs
    for state, agent in handoff_sequence:
        if state not in completed_states:
            recommendations.append({
                "handoff_type": state,
                "to_agent": agent,
                "reason": f"Next step in workflow sequence"
            })
            break  # Only recommend the next logical step
    
    # Add context-specific recommendations
    if context and context.advanced_tests_requested:
        if "testing" not in completed_states:
            recommendations.append({
                "handoff_type": "testing",
                "to_agent": "Plugin Testing Agent",
                "reason": "Advanced testing requested"
            })
    
    return recommendations


def _perform_additional_validation(handoff_type: HandoffType, data: Dict[str, Any], context) -> Dict[str, Any]:
    """Perform additional validation checks beyond basic data validation."""
    
    checks = {
        "context_consistency": True,
        "data_completeness": True,
        "workflow_sequence": True,
        "security_clearance": True
    }
    
    errors = []
    
    # Context consistency check
    if context and context.current_phase == "failed":
        checks["context_consistency"] = False
        errors.append("Context is in failed state")
    
    # Data completeness check
    if handoff_type == HandoffType.GENERATION and not data.get("plugin_spec"):
        checks["data_completeness"] = False
        errors.append("Missing plugin specification for generation handoff")
    
    if handoff_type == HandoffType.COMPLIANCE and not data.get("generated_files"):
        checks["data_completeness"] = False
        errors.append("Missing generated files for compliance handoff")
    
    # Workflow sequence check
    if handoff_type == HandoffType.TESTING and not any(state in handoff_manager.workflow_state for state in ["generation", "compliance"]):
        checks["workflow_sequence"] = False
        errors.append("Testing handoff requires generation or compliance to be completed first")
    
    # Security clearance check (simplified)
    if data.get("security_scan_required") and not data.get("security_clearance"):
        checks["security_clearance"] = False
        errors.append("Security clearance required but not provided")
    
    return {
        "valid": all(checks.values()),
        "checks": checks,
        "errors": errors
    }


def _get_validation_recommendations(handoff_type: HandoffType, data: Dict[str, Any], 
                                   validation_result: Dict[str, Any], 
                                   additional_checks: Dict[str, Any]) -> List[str]:
    """Get validation recommendations."""
    recommendations = []
    
    # Basic validation recommendations
    if not validation_result["valid"]:
        recommendations.append(f"Fix data validation errors: {validation_result.get('error', 'Unknown error')}")
    
    # Additional check recommendations
    if not additional_checks["valid"]:
        for error in additional_checks.get("errors", []):
            recommendations.append(f"Address: {error}")
    
    # Type-specific recommendations
    if handoff_type == HandoffType.GENERATION:
        if not data.get("features"):
            recommendations.append("Ensure plugin features are clearly defined")
    
    if handoff_type == HandoffType.COMPLIANCE:
        if not data.get("file_paths"):
            recommendations.append("Provide file paths for compliance checking")
    
    if handoff_type == HandoffType.TESTING:
        if not data.get("test_requirements"):
            recommendations.append("Define specific testing requirements")
    
    return recommendations or ["Data validation passed - ready for handoff"]