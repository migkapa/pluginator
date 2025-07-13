"""
Security tools for WordPress Plugin Generator agents.
Provides function tools for security validation and scanning.
"""

from typing import List, Dict, Any, Optional
from agents import function_tool
from loguru import logger

from security_guardrails import security_guardrails, plugin_security_scanner, GuardrailViolation
from context_manager import context_manager


@function_tool
def validate_plugin_security(plugin_files: str) -> Dict[str, Any]:
    """
    Perform comprehensive security validation on plugin files.
    
    Args:
        plugin_files: JSON string containing list of plugin files with 'path' and 'content' keys
        
    Returns:
        Dictionary with security validation results
    """
    try:
        logger.info("Starting plugin security validation...")
        
        # Parse JSON input
        import json
        try:
            files_data = json.loads(plugin_files)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON input for plugin files"}
        
        # Run security scanner
        violations = plugin_security_scanner(files_data)
        
        # Update context with security results
        context = context_manager.get_context()
        if context:
            context.compliance_issues.extend([
                {
                    "type": "security",
                    "severity": v.severity.value,
                    "message": v.message,
                    "file": v.file_path,
                    "category": v.category.value,
                    "fix_suggestion": v.suggested_fix
                }
                for v in violations
            ])
            context_manager.update_context(context.session_id)
        
        # Categorize violations by severity
        critical_violations = [v for v in violations if v.severity.value == "critical"]
        high_violations = [v for v in violations if v.severity.value == "high"]
        medium_violations = [v for v in violations if v.severity.value == "medium"]
        low_violations = [v for v in violations if v.severity.value == "low"]
        
        # Create summary
        summary = {
            "total_violations": len(violations),
            "critical_count": len(critical_violations),
            "high_count": len(high_violations),
            "medium_count": len(medium_violations),
            "low_count": len(low_violations),
            "security_score": max(0, 100 - (len(critical_violations) * 25 + len(high_violations) * 15 + len(medium_violations) * 10 + len(low_violations) * 5)),
            "passed": len(critical_violations) == 0 and len(high_violations) == 0
        }
        
        # Create detailed report
        detailed_violations = []
        for violation in violations:
            detailed_violations.append({
                "severity": violation.severity.value,
                "category": violation.category.value,
                "message": violation.message,
                "file_path": violation.file_path,
                "line_number": violation.line_number,
                "details": violation.details,
                "suggested_fix": violation.suggested_fix
            })
        
        result = {
            "summary": summary,
            "violations": detailed_violations,
            "recommendations": _get_security_recommendations(violations)
        }
        
        logger.info(f"Security validation completed. Score: {summary['security_score']}/100")
        return result
        
    except Exception as e:
        logger.error(f"Security validation failed: {e}")
        return {
            "summary": {
                "total_violations": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "security_score": 0,
                "passed": False,
                "error": str(e)
            },
            "violations": [],
            "recommendations": ["Fix security validation errors and retry"]
        }


@function_tool
def check_wordpress_security_compliance(plugin_content: str, plugin_name: str) -> Dict[str, Any]:
    """
    Check WordPress security compliance for a single plugin file.
    
    Args:
        plugin_content: Content of the plugin file
        plugin_name: Name of the plugin file
        
    Returns:
        Dictionary with compliance check results
    """
    try:
        logger.info(f"Checking WordPress security compliance for {plugin_name}")
        
        violations = security_guardrails._check_code_security(plugin_content)
        
        # WordPress-specific security checks
        wordpress_checks = {
            "abspath_check": "if (!defined('ABSPATH')) exit;" in plugin_content,
            "nonce_usage": "wp_verify_nonce" in plugin_content or "wp_create_nonce" in plugin_content,
            "capability_checks": "current_user_can" in plugin_content,
            "input_sanitization": any(func in plugin_content for func in ["sanitize_text_field", "sanitize_email", "sanitize_url", "esc_html", "esc_attr"]),
            "prepared_statements": "$wpdb->prepare" in plugin_content,
            "no_direct_access": not any(danger in plugin_content for danger in ["$_GET", "$_POST", "$_REQUEST", "$_COOKIE"]) or "wp_verify_nonce" in plugin_content
        }
        
        # Calculate compliance score
        passed_checks = sum(1 for check in wordpress_checks.values() if check)
        total_checks = len(wordpress_checks)
        compliance_score = (passed_checks / total_checks) * 100
        
        result = {
            "plugin_name": plugin_name,
            "compliance_score": compliance_score,
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "wordpress_checks": wordpress_checks,
            "security_violations": [
                {
                    "severity": v.severity.value,
                    "message": v.message,
                    "suggested_fix": v.suggested_fix
                }
                for v in violations
            ],
            "recommendations": _get_wordpress_compliance_recommendations(wordpress_checks, violations)
        }
        
        logger.info(f"WordPress compliance check completed. Score: {compliance_score:.1f}%")
        return result
        
    except Exception as e:
        logger.error(f"WordPress compliance check failed: {e}")
        return {
            "plugin_name": plugin_name,
            "compliance_score": 0,
            "passed_checks": 0,
            "total_checks": 0,
            "wordpress_checks": {},
            "security_violations": [],
            "recommendations": ["Fix compliance check errors and retry"],
            "error": str(e)
        }


@function_tool
def scan_for_malicious_patterns(content: str, content_type: str = "code") -> Dict[str, Any]:
    """
    Scan content for malicious patterns and security threats.
    
    Args:
        content: Content to scan
        content_type: Type of content (code, input, output)
        
    Returns:
        Dictionary with scan results
    """
    try:
        logger.info(f"Scanning {content_type} for malicious patterns...")
        
        violations = security_guardrails._check_malicious_content(content)
        violations.extend(security_guardrails._check_inappropriate_requests(content))
        
        if content_type == "code":
            violations.extend(security_guardrails._check_code_security(content))
        
        # Categorize threats
        critical_threats = [v for v in violations if v.severity.value == "critical"]
        high_threats = [v for v in violations if v.severity.value == "high"]
        medium_threats = [v for v in violations if v.severity.value == "medium"]
        
        threat_level = "CRITICAL" if critical_threats else "HIGH" if high_threats else "MEDIUM" if medium_threats else "LOW"
        
        result = {
            "content_type": content_type,
            "threat_level": threat_level,
            "total_threats": len(violations),
            "critical_threats": len(critical_threats),
            "high_threats": len(high_threats),
            "medium_threats": len(medium_threats),
            "threats_detected": [
                {
                    "severity": v.severity.value,
                    "category": v.category.value,
                    "message": v.message,
                    "details": v.details,
                    "suggested_fix": v.suggested_fix
                }
                for v in violations
            ],
            "safe_to_proceed": len(critical_threats) == 0 and len(high_threats) == 0
        }
        
        logger.info(f"Malicious pattern scan completed. Threat level: {threat_level}")
        return result
        
    except Exception as e:
        logger.error(f"Malicious pattern scan failed: {e}")
        return {
            "content_type": content_type,
            "threat_level": "UNKNOWN",
            "total_threats": 0,
            "critical_threats": 0,
            "high_threats": 0,
            "medium_threats": 0,
            "threats_detected": [],
            "safe_to_proceed": False,
            "error": str(e)
        }


def _get_security_recommendations(violations: List[GuardrailViolation]) -> List[str]:
    """Generate security recommendations based on violations."""
    recommendations = []
    
    # Count violations by category
    categories = {}
    for violation in violations:
        category = violation.category.value
        categories[category] = categories.get(category, 0) + 1
    
    # Generate recommendations
    if categories.get("security_scan", 0) > 0:
        recommendations.append("Review and fix security vulnerabilities in the code")
        recommendations.append("Use WordPress security best practices and APIs")
    
    if categories.get("content_filter", 0) > 0:
        recommendations.append("Remove or modify prohibited content")
        recommendations.append("Ensure plugin purpose is legitimate and helpful")
    
    if categories.get("input_validation", 0) > 0:
        recommendations.append("Simplify and clarify input requirements")
        recommendations.append("Follow input format guidelines")
    
    if categories.get("output_validation", 0) > 0:
        recommendations.append("Regenerate output with better specifications")
        recommendations.append("Check for underlying generation issues")
    
    # Add general recommendations
    recommendations.append("Test the plugin thoroughly before deployment")
    recommendations.append("Follow WordPress Plugin Review Guidelines")
    
    return recommendations


def _get_wordpress_compliance_recommendations(checks: Dict[str, bool], violations: List[GuardrailViolation]) -> List[str]:
    """Generate WordPress compliance recommendations."""
    recommendations = []
    
    if not checks.get("abspath_check", False):
        recommendations.append("Add ABSPATH security check to prevent direct file access")
    
    if not checks.get("nonce_usage", False):
        recommendations.append("Implement nonce verification for form submissions and AJAX calls")
    
    if not checks.get("capability_checks", False):
        recommendations.append("Add capability checks for administrative functions")
    
    if not checks.get("input_sanitization", False):
        recommendations.append("Implement proper input sanitization and output escaping")
    
    if not checks.get("prepared_statements", False):
        recommendations.append("Use prepared statements for database queries")
    
    if not checks.get("no_direct_access", False):
        recommendations.append("Avoid direct access to superglobals without proper validation")
    
    # Add violation-specific recommendations
    for violation in violations:
        if violation.suggested_fix:
            recommendations.append(violation.suggested_fix)
    
    return list(set(recommendations))  # Remove duplicates