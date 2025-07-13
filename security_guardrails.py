"""
Security Guardrails for WordPress Plugin Generator.
Implements input/output validation and security checks following OpenAI Agents Python best practices.
"""

import re
import json
import hashlib
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from context_manager import PluginGenerationContext


class GuardrailSeverity(Enum):
    """Severity levels for guardrail violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GuardrailCategory(Enum):
    """Categories of security guardrails."""
    INPUT_VALIDATION = "input_validation"
    OUTPUT_VALIDATION = "output_validation"
    SECURITY_SCAN = "security_scan"
    CONTENT_FILTER = "content_filter"
    PLUGIN_COMPLIANCE = "plugin_compliance"


@dataclass
class GuardrailViolation:
    """Represents a guardrail violation."""
    category: GuardrailCategory
    severity: GuardrailSeverity
    message: str
    details: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None


class GuardrailTripwireTriggered(Exception):
    """Exception raised when a critical guardrail is triggered."""
    
    def __init__(self, violation: GuardrailViolation):
        self.violation = violation
        super().__init__(f"Critical guardrail violation: {violation.message}")


class SecurityGuardrails:
    """Security guardrails for WordPress plugin generation."""
    
    def __init__(self):
        self.violations: List[GuardrailViolation] = []
        
        # Dangerous PHP functions and patterns
        self.dangerous_functions = {
            'eval', 'exec', 'system', 'shell_exec', 'passthru', 'proc_open',
            'popen', 'file_get_contents', 'file_put_contents', 'fopen', 'fwrite',
            'unlink', 'rmdir', 'mkdir', 'chmod', 'chown', 'curl_exec'
        }
        
        # SQL injection patterns
        self.sql_injection_patterns = [
            r'\$_(?:GET|POST|REQUEST|COOKIE)\[.*?\].*?(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)',
            r'mysql_query\s*\(\s*["\'].*?\$',
            r'query\s*\(\s*["\'].*?\$',
        ]
        
        # WordPress security patterns
        self.wordpress_security_patterns = {
            'missing_abspath': r'^<\?php\s*$',
            'direct_file_access': r'(?<!if\s*\(\s*!\s*defined\s*\(\s*["\']ABSPATH["\'])',
            'missing_nonce': r'(?:wp_ajax_|admin_post_).*?(?<!wp_verify_nonce)',
            'unsafe_output': r'echo\s+\$_(?:GET|POST|REQUEST|COOKIE)',
            'missing_capability': r'(?:add_menu_page|add_submenu_page).*?(?<!current_user_can)',
        }
        
        # Prohibited content patterns
        self.prohibited_content = [
            r'(?i)malware',
            r'(?i)backdoor',
            r'(?i)exploit',
            r'(?i)hack',
            r'(?i)phishing',
            r'(?i)spam',
            r'(?i)virus',
            r'(?i)trojan',
        ]
    
    def validate_input(self, user_input: str, context: Optional[PluginGenerationContext] = None) -> List[GuardrailViolation]:
        """Validate user input for security issues."""
        violations = []
        
        # Check for malicious content in input
        violations.extend(self._check_malicious_content(user_input))
        
        # Check for inappropriate requests
        violations.extend(self._check_inappropriate_requests(user_input))
        
        # Check input length and complexity
        violations.extend(self._check_input_limits(user_input))
        
        # Context-specific validation
        if context:
            violations.extend(self._check_context_consistency(user_input, context))
        
        return violations
    
    def validate_output(self, output: str, output_type: str = "code", context: Optional[PluginGenerationContext] = None) -> List[GuardrailViolation]:
        """Validate agent output for security issues."""
        violations = []
        
        if output_type == "code":
            violations.extend(self._check_code_security(output))
        elif output_type == "plugin_files":
            violations.extend(self._check_plugin_files_security(output))
        elif output_type == "compliance_report":
            violations.extend(self._check_compliance_report(output))
        
        # General output validation
        violations.extend(self._check_output_quality(output))
        
        return violations
    
    def _check_malicious_content(self, content: str) -> List[GuardrailViolation]:
        """Check for malicious content patterns."""
        violations = []
        
        for pattern in self.prohibited_content:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(GuardrailViolation(
                    category=GuardrailCategory.CONTENT_FILTER,
                    severity=GuardrailSeverity.CRITICAL,
                    message=f"Prohibited content detected: {pattern}",
                    details=f"Input contains potentially malicious content matching pattern: {pattern}",
                    suggested_fix="Remove or rephrase the problematic content"
                ))
        
        return violations
    
    def _check_inappropriate_requests(self, content: str) -> List[GuardrailViolation]:
        """Check for inappropriate plugin requests."""
        violations = []
        
        # Check for admin/security bypass requests
        admin_bypass_patterns = [
            r'(?i)bypass.*(?:admin|security|authentication)',
            r'(?i)disable.*(?:security|validation|checks)',
            r'(?i)backdoor.*(?:access|login|admin)',
            r'(?i)exploit.*(?:vulnerability|weakness)',
        ]
        
        for pattern in admin_bypass_patterns:
            if re.search(pattern, content):
                violations.append(GuardrailViolation(
                    category=GuardrailCategory.CONTENT_FILTER,
                    severity=GuardrailSeverity.CRITICAL,
                    message="Inappropriate security bypass request detected",
                    details=f"Content matches security bypass pattern: {pattern}",
                    suggested_fix="Request legitimate WordPress functionality instead"
                ))
        
        return violations
    
    def _check_input_limits(self, content: str) -> List[GuardrailViolation]:
        """Check input length and complexity limits."""
        violations = []
        
        # Check length limits
        if len(content) > 10000:
            violations.append(GuardrailViolation(
                category=GuardrailCategory.INPUT_VALIDATION,
                severity=GuardrailSeverity.MEDIUM,
                message="Input exceeds maximum length limit",
                details=f"Input length: {len(content)} characters (max: 10000)",
                suggested_fix="Reduce input length or break into multiple requests"
            ))
        
        # Check for excessive complexity
        if content.count('\n') > 100:
            violations.append(GuardrailViolation(
                category=GuardrailCategory.INPUT_VALIDATION,
                severity=GuardrailSeverity.LOW,
                message="Input has excessive complexity",
                details=f"Input contains {content.count(chr(10))} lines",
                suggested_fix="Simplify the request or break into smaller parts"
            ))
        
        return violations
    
    def _check_context_consistency(self, content: str, context: PluginGenerationContext) -> List[GuardrailViolation]:
        """Check input consistency with context."""
        violations = []
        
        # Check if input matches current phase
        if context.current_phase == "completed":
            violations.append(GuardrailViolation(
                category=GuardrailCategory.INPUT_VALIDATION,
                severity=GuardrailSeverity.MEDIUM,
                message="Input received for completed session",
                details="Session is already marked as completed",
                suggested_fix="Start a new session for additional requests"
            ))
        
        # Check retry limits
        if context.retry_count >= context.max_retries:
            violations.append(GuardrailViolation(
                category=GuardrailCategory.INPUT_VALIDATION,
                severity=GuardrailSeverity.HIGH,
                message="Maximum retry attempts exceeded",
                details=f"Retry count: {context.retry_count} (max: {context.max_retries})",
                suggested_fix="Review and fix underlying issues before retrying"
            ))
        
        return violations
    
    def _check_code_security(self, code: str) -> List[GuardrailViolation]:
        """Check code for security vulnerabilities."""
        violations = []
        
        # Check for dangerous PHP functions
        for func in self.dangerous_functions:
            pattern = rf'\b{func}\s*\('
            if re.search(pattern, code, re.IGNORECASE):
                violations.append(GuardrailViolation(
                    category=GuardrailCategory.SECURITY_SCAN,
                    severity=GuardrailSeverity.HIGH,
                    message=f"Dangerous PHP function detected: {func}",
                    details=f"Function '{func}' can be used for malicious purposes",
                    suggested_fix=f"Replace '{func}' with safer WordPress alternatives"
                ))
        
        # Check for SQL injection patterns
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                violations.append(GuardrailViolation(
                    category=GuardrailCategory.SECURITY_SCAN,
                    severity=GuardrailSeverity.CRITICAL,
                    message="Potential SQL injection vulnerability",
                    details=f"Code matches SQL injection pattern: {pattern}",
                    suggested_fix="Use WordPress $wpdb prepared statements"
                ))
        
        # Check WordPress security patterns
        for check_name, pattern in self.wordpress_security_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                severity = GuardrailSeverity.CRITICAL if check_name in ['missing_abspath', 'missing_nonce'] else GuardrailSeverity.HIGH
                violations.append(GuardrailViolation(
                    category=GuardrailCategory.SECURITY_SCAN,
                    severity=severity,
                    message=f"WordPress security issue: {check_name}",
                    details=f"Code matches security pattern: {pattern}",
                    suggested_fix=self._get_security_fix_suggestion(check_name)
                ))
        
        return violations
    
    def _check_plugin_files_security(self, files_content: str) -> List[GuardrailViolation]:
        """Check plugin files for security issues."""
        violations = []
        
        try:
            # Try to parse as JSON (plugin files format)
            files_data = json.loads(files_content)
            if isinstance(files_data, list):
                for file_data in files_data:
                    if isinstance(file_data, dict) and 'content' in file_data:
                        file_violations = self._check_code_security(file_data['content'])
                        # Add file path context to violations
                        for violation in file_violations:
                            violation.file_path = file_data.get('path', 'unknown')
                        violations.extend(file_violations)
        except json.JSONDecodeError:
            # If not JSON, treat as raw code
            violations.extend(self._check_code_security(files_content))
        
        return violations
    
    def _check_compliance_report(self, report: str) -> List[GuardrailViolation]:
        """Check compliance report for consistency."""
        violations = []
        
        # Basic validation for compliance reports
        if "error" in report.lower() and "critical" in report.lower():
            violations.append(GuardrailViolation(
                category=GuardrailCategory.OUTPUT_VALIDATION,
                severity=GuardrailSeverity.MEDIUM,
                message="Compliance report indicates critical errors",
                details="Generated plugin may have critical compliance issues",
                suggested_fix="Review and fix compliance issues before proceeding"
            ))
        
        return violations
    
    def _check_output_quality(self, output: str) -> List[GuardrailViolation]:
        """Check general output quality."""
        violations = []
        
        # Check for empty or minimal output
        if len(output.strip()) < 10:
            violations.append(GuardrailViolation(
                category=GuardrailCategory.OUTPUT_VALIDATION,
                severity=GuardrailSeverity.HIGH,
                message="Output is too short or empty",
                details=f"Output length: {len(output)} characters",
                suggested_fix="Regenerate with more detailed specifications"
            ))
        
        # Check for error messages in output
        error_patterns = [
            r'(?i)error.*occurred',
            r'(?i)failed.*to',
            r'(?i)unable.*to',
            r'(?i)invalid.*input',
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, output):
                violations.append(GuardrailViolation(
                    category=GuardrailCategory.OUTPUT_VALIDATION,
                    severity=GuardrailSeverity.MEDIUM,
                    message="Error indication in output",
                    details=f"Output contains error pattern: {pattern}",
                    suggested_fix="Check for underlying issues and regenerate"
                ))
        
        return violations
    
    def _get_security_fix_suggestion(self, check_name: str) -> str:
        """Get security fix suggestion for a specific check."""
        fixes = {
            'missing_abspath': "Add 'if (!defined('ABSPATH')) exit;' at the top of PHP files",
            'direct_file_access': "Use proper WordPress security checks",
            'missing_nonce': "Add wp_verify_nonce() verification for form submissions",
            'unsafe_output': "Use WordPress escaping functions like esc_html() or esc_attr()",
            'missing_capability': "Add current_user_can() capability checks",
        }
        return fixes.get(check_name, "Review WordPress security best practices")
    
    def check_and_raise_critical(self, violations: List[GuardrailViolation]):
        """Check violations and raise exception for critical issues."""
        critical_violations = [v for v in violations if v.severity == GuardrailSeverity.CRITICAL]
        if critical_violations:
            raise GuardrailTripwireTriggered(critical_violations[0])
    
    def get_violations_summary(self) -> Dict[str, int]:
        """Get summary of violations by severity."""
        summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for violation in self.violations:
            summary[violation.severity.value] += 1
        
        return summary
    
    def clear_violations(self):
        """Clear all recorded violations."""
        self.violations.clear()


# Global guardrails instance
security_guardrails = SecurityGuardrails()


def input_guardrail(user_input: str, context: Optional[PluginGenerationContext] = None) -> List[GuardrailViolation]:
    """Input guardrail function for OpenAI Agents integration."""
    violations = security_guardrails.validate_input(user_input, context)
    security_guardrails.check_and_raise_critical(violations)
    return violations


def output_guardrail(output: str, output_type: str = "code", context: Optional[PluginGenerationContext] = None) -> List[GuardrailViolation]:
    """Output guardrail function for OpenAI Agents integration."""
    violations = security_guardrails.validate_output(output, output_type, context)
    security_guardrails.check_and_raise_critical(violations)
    return violations


def plugin_security_scanner(plugin_files: List[Dict[str, Any]]) -> List[GuardrailViolation]:
    """Comprehensive security scanner for plugin files."""
    all_violations = []
    
    for file_data in plugin_files:
        if 'content' in file_data:
            violations = security_guardrails._check_code_security(file_data['content'])
            # Add file context
            for violation in violations:
                violation.file_path = file_data.get('path', 'unknown')
            all_violations.extend(violations)
    
    return all_violations