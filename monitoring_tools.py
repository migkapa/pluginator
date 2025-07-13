"""
Monitoring tools for WordPress Plugin Generator agents.
Provides function tools for performance monitoring and error tracking.
"""

from typing import Dict, Any, Optional, List
from agents import function_tool
from loguru import logger

from agent_hooks import plugin_hooks
from context_manager import context_manager


@function_tool
def get_performance_metrics() -> Dict[str, Any]:
    """
    Get performance metrics for all agents.
    
    Returns:
        Dictionary with performance metrics including average execution times,
        error rates, and system health indicators.
    """
    try:
        logger.info("Retrieving performance metrics...")
        
        # Get basic performance data
        performance_summary = plugin_hooks.get_performance_summary()
        error_summary = plugin_hooks.get_error_summary()
        
        # Calculate system health indicators
        total_runs = sum(metrics["total_runs"] for metrics in performance_summary.values())
        total_errors = error_summary["total_errors"]
        
        overall_success_rate = ((total_runs - total_errors) / total_runs * 100) if total_runs > 0 else 100
        
        # Identify bottlenecks
        bottlenecks = []
        for agent_name, metrics in performance_summary.items():
            if metrics["avg_duration"] > 30:  # Slow agents
                bottlenecks.append({
                    "agent": agent_name,
                    "avg_duration": metrics["avg_duration"],
                    "issue": "slow_execution"
                })
        
        # Get recent events summary
        recent_events = plugin_hooks.events[-50:]  # Last 50 events
        event_types = {}
        for event in recent_events:
            event_types[event.hook_type.value] = event_types.get(event.hook_type.value, 0) + 1
        
        result = {
            "overall_health": {
                "success_rate": overall_success_rate,
                "total_runs": total_runs,
                "total_errors": total_errors,
                "status": "healthy" if overall_success_rate > 95 else "degraded" if overall_success_rate > 80 else "unhealthy"
            },
            "agent_performance": performance_summary,
            "error_summary": error_summary,
            "bottlenecks": bottlenecks,
            "recent_activity": {
                "event_types": event_types,
                "total_events": len(recent_events)
            },
            "recommendations": _get_performance_recommendations(performance_summary, error_summary, bottlenecks)
        }
        
        logger.info(f"Performance metrics retrieved. System status: {result['overall_health']['status']}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        return {
            "overall_health": {
                "success_rate": 0,
                "total_runs": 0,
                "total_errors": 0,
                "status": "error"
            },
            "agent_performance": {},
            "error_summary": {},
            "bottlenecks": [],
            "recent_activity": {},
            "recommendations": ["Check system logs for errors"],
            "error": str(e)
        }


@function_tool
def get_session_metrics(session_id: str = "") -> Dict[str, Any]:
    """
    Get detailed metrics for a specific session.
    
    Args:
        session_id: Session ID to get metrics for (defaults to current session)
        
    Returns:
        Dictionary with session-specific metrics and timeline
    """
    try:
        # Get session ID from context if not provided
        if not session_id:
            context = context_manager.get_context()
            if context:
                session_id = context.session_id
            else:
                return {"error": "No session ID provided and no active context"}
        
        logger.info(f"Retrieving session metrics for: {session_id}")
        
        # Get session report
        session_report = plugin_hooks.get_session_report(session_id)
        
        if "error" in session_report:
            return session_report
        
        # Add context information
        context = context_manager.get_context()
        if context and context.session_id == session_id:
            session_report["context"] = {
                "plugin_name": context.plugin_name,
                "current_phase": context.current_phase,
                "phases_completed": context.phases_completed,
                "progress": context.get_progress_percentage(),
                "errors_encountered": len(context.errors_encountered),
                "advanced_tests_requested": context.advanced_tests_requested
            }
        
        # Add analysis
        session_report["analysis"] = _analyze_session_performance(session_report)
        
        logger.info(f"Session metrics retrieved. Success rate: {session_report['success_rate']:.1f}%")
        return session_report
        
    except Exception as e:
        logger.error(f"Failed to get session metrics: {e}")
        return {
            "session_id": session_id,
            "error": str(e),
            "analysis": {
                "status": "error",
                "recommendations": ["Check logs for detailed error information"]
            }
        }


@function_tool
def get_error_analysis() -> Dict[str, Any]:
    """
    Get detailed analysis of errors and failures.
    
    Returns:
        Dictionary with error analysis, patterns, and recommendations
    """
    try:
        logger.info("Analyzing errors and failures...")
        
        # Get all error events
        error_events = [e for e in plugin_hooks.events if not e.success]
        
        if not error_events:
            return {
                "total_errors": 0,
                "error_patterns": {},
                "agent_errors": {},
                "tool_errors": {},
                "timeline": [],
                "recommendations": ["System is running without errors"],
                "status": "healthy"
            }
        
        # Analyze error patterns
        error_patterns = {}
        agent_errors = {}
        tool_errors = {}
        
        for event in error_events:
            # Pattern analysis
            if event.error:
                error_key = event.error.lower()
                error_patterns[error_key] = error_patterns.get(error_key, 0) + 1
            
            # Agent error tracking
            agent_errors[event.agent_name] = agent_errors.get(event.agent_name, 0) + 1
            
            # Tool error tracking
            if event.tool_name:
                tool_errors[event.tool_name] = tool_errors.get(event.tool_name, 0) + 1
        
        # Find most common issues
        most_common_pattern = max(error_patterns.items(), key=lambda x: x[1]) if error_patterns else None
        most_problematic_agent = max(agent_errors.items(), key=lambda x: x[1]) if agent_errors else None
        most_problematic_tool = max(tool_errors.items(), key=lambda x: x[1]) if tool_errors else None
        
        # Create timeline of recent errors
        recent_errors = sorted(error_events[-20:], key=lambda x: x.timestamp, reverse=True)
        timeline = [
            {
                "timestamp": event.timestamp.isoformat(),
                "agent": event.agent_name,
                "tool": event.tool_name,
                "error": event.error,
                "type": event.hook_type.value
            }
            for event in recent_errors
        ]
        
        result = {
            "total_errors": len(error_events),
            "error_patterns": error_patterns,
            "agent_errors": agent_errors,
            "tool_errors": tool_errors,
            "most_common_issue": most_common_pattern,
            "most_problematic_agent": most_problematic_agent,
            "most_problematic_tool": most_problematic_tool,
            "timeline": timeline,
            "recommendations": _get_error_recommendations(error_patterns, agent_errors, tool_errors),
            "status": "critical" if len(error_events) > 20 else "warning" if len(error_events) > 5 else "stable"
        }
        
        logger.info(f"Error analysis completed. Status: {result['status']}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to analyze errors: {e}")
        return {
            "total_errors": 0,
            "error_patterns": {},
            "agent_errors": {},
            "tool_errors": {},
            "timeline": [],
            "recommendations": ["Check system logs for analysis errors"],
            "status": "error",
            "error": str(e)
        }


@function_tool
def get_health_status() -> Dict[str, Any]:
    """
    Get overall system health status.
    
    Returns:
        Dictionary with system health indicators and recommendations
    """
    try:
        logger.info("Checking system health status...")
        
        # Get basic metrics
        performance_metrics = plugin_hooks.get_performance_summary()
        error_summary = plugin_hooks.get_error_summary()
        
        # Calculate health indicators
        total_runs = sum(metrics["total_runs"] for metrics in performance_metrics.values())
        total_errors = error_summary["total_errors"]
        
        # Health checks
        checks = {
            "agent_performance": _check_agent_performance(performance_metrics),
            "error_rate": _check_error_rate(total_runs, total_errors),
            "system_resources": _check_system_resources(),
            "security_status": _check_security_status()
        }
        
        # Overall health calculation
        passed_checks = sum(1 for check in checks.values() if check["status"] == "healthy")
        total_checks = len(checks)
        health_score = (passed_checks / total_checks) * 100
        
        overall_status = "healthy" if health_score >= 80 else "degraded" if health_score >= 60 else "unhealthy"
        
        result = {
            "overall_status": overall_status,
            "health_score": health_score,
            "checks": checks,
            "summary": {
                "total_agents": len(performance_metrics),
                "total_runs": total_runs,
                "total_errors": total_errors,
                "success_rate": ((total_runs - total_errors) / total_runs * 100) if total_runs > 0 else 100
            },
            "recommendations": _get_health_recommendations(checks, overall_status)
        }
        
        logger.info(f"Health status checked. Overall status: {overall_status} ({health_score:.1f}%)")
        return result
        
    except Exception as e:
        logger.error(f"Failed to check health status: {e}")
        return {
            "overall_status": "error",
            "health_score": 0,
            "checks": {},
            "summary": {},
            "recommendations": ["Check system logs for health check errors"],
            "error": str(e)
        }


def _get_performance_recommendations(performance_summary: Dict, error_summary: Dict, bottlenecks: List) -> List[str]:
    """Generate performance recommendations."""
    recommendations = []
    
    if bottlenecks:
        recommendations.append("Consider optimizing slow agents or increasing system resources")
    
    if error_summary["total_errors"] > 10:
        recommendations.append("Review error logs and fix recurring issues")
    
    if not performance_summary:
        recommendations.append("No performance data available - run some operations first")
    
    return recommendations or ["System is performing well"]


def _analyze_session_performance(session_report: Dict) -> Dict[str, Any]:
    """Analyze session performance."""
    analysis = {
        "status": "completed" if session_report["success_rate"] > 90 else "partial" if session_report["success_rate"] > 70 else "failed",
        "duration_assessment": "fast" if session_report["total_duration"] < 60 else "normal" if session_report["total_duration"] < 180 else "slow",
        "recommendations": []
    }
    
    if session_report["success_rate"] < 90:
        analysis["recommendations"].append("Review and address failed operations")
    
    if session_report["total_duration"] > 180:
        analysis["recommendations"].append("Consider optimizing for faster execution")
    
    return analysis


def _get_error_recommendations(error_patterns: Dict, agent_errors: Dict, tool_errors: Dict) -> List[str]:
    """Generate error-based recommendations."""
    recommendations = []
    
    if error_patterns:
        most_common = max(error_patterns.items(), key=lambda x: x[1])
        recommendations.append(f"Address most common error pattern: {most_common[0]}")
    
    if agent_errors:
        most_problematic = max(agent_errors.items(), key=lambda x: x[1])
        recommendations.append(f"Review and fix issues in {most_problematic[0]} agent")
    
    if tool_errors:
        most_problematic = max(tool_errors.items(), key=lambda x: x[1])
        recommendations.append(f"Investigate problems with {most_problematic[0]} tool")
    
    return recommendations or ["Continue monitoring for error patterns"]


def _check_agent_performance(performance_metrics: Dict) -> Dict[str, Any]:
    """Check agent performance health."""
    if not performance_metrics:
        return {"status": "unknown", "message": "No performance data available"}
    
    slow_agents = [name for name, metrics in performance_metrics.items() if metrics["avg_duration"] > 30]
    
    if not slow_agents:
        return {"status": "healthy", "message": "All agents performing well"}
    else:
        return {"status": "degraded", "message": f"Slow agents detected: {', '.join(slow_agents)}"}


def _check_error_rate(total_runs: int, total_errors: int) -> Dict[str, Any]:
    """Check error rate health."""
    if total_runs == 0:
        return {"status": "unknown", "message": "No operations recorded"}
    
    error_rate = (total_errors / total_runs) * 100
    
    if error_rate < 5:
        return {"status": "healthy", "message": f"Low error rate: {error_rate:.1f}%"}
    elif error_rate < 20:
        return {"status": "degraded", "message": f"Moderate error rate: {error_rate:.1f}%"}
    else:
        return {"status": "unhealthy", "message": f"High error rate: {error_rate:.1f}%"}


def _check_system_resources() -> Dict[str, Any]:
    """Check system resources (simplified)."""
    # This is a simplified check - in production, you'd check actual system resources
    return {"status": "healthy", "message": "System resources appear adequate"}


def _check_security_status() -> Dict[str, Any]:
    """Check security status."""
    # Count security-related events
    security_events = [e for e in plugin_hooks.events if e.hook_type.value == "security_check"]
    security_violations = [e for e in security_events if not e.success]
    
    if not security_events:
        return {"status": "unknown", "message": "No security checks performed"}
    
    violation_rate = (len(security_violations) / len(security_events)) * 100
    
    if violation_rate == 0:
        return {"status": "healthy", "message": "No security violations detected"}
    elif violation_rate < 10:
        return {"status": "degraded", "message": f"Some security violations: {violation_rate:.1f}%"}
    else:
        return {"status": "unhealthy", "message": f"High security violation rate: {violation_rate:.1f}%"}


def _get_health_recommendations(checks: Dict, overall_status: str) -> List[str]:
    """Generate health-based recommendations."""
    recommendations = []
    
    for check_name, check_result in checks.items():
        if check_result["status"] != "healthy":
            recommendations.append(f"Address {check_name}: {check_result['message']}")
    
    if overall_status == "unhealthy":
        recommendations.append("System requires immediate attention")
    elif overall_status == "degraded":
        recommendations.append("Monitor system closely and address issues")
    
    return recommendations or ["System is healthy - continue monitoring"]