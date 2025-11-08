#!/usr/bin/env python3
"""
Security Audit Script for OverXchange Project
Checks for common security vulnerabilities and provides recommendations
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any

class SecurityAuditor:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.vulnerabilities = []
        self.recommendations = []
        
    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan a single file for security vulnerabilities"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return [{'type': 'error', 'message': f'Could not read file: {e}'}]
        
        # Check for hardcoded credentials
        credential_patterns = [
            r'mongodb\+srv://[^@]+@[^/]+',
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in credential_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'type': 'hardcoded_credential',
                        'line': i,
                        'message': f'Hardcoded credential found: {line.strip()}',
                        'severity': 'high'
                    })
        
        # Check for SQL injection patterns
        sql_patterns = [
            r'SELECT.*\+.*request',
            r'INSERT.*\+.*request',
            r'UPDATE.*\+.*request',
            r'DELETE.*\+.*request'
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in sql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'type': 'sql_injection',
                        'line': i,
                        'message': f'Potential SQL injection: {line.strip()}',
                        'severity': 'high'
                    })
        
        # Check for XSS vulnerabilities
        xss_patterns = [
            r'innerHTML\s*=\s*[^;]+',
            r'document\.write\s*\(',
            r'eval\s*\(',
            r'setTimeout\s*\(\s*["\'][^"\']*["\']'
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in xss_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'type': 'xss',
                        'line': i,
                        'message': f'Potential XSS vulnerability: {line.strip()}',
                        'severity': 'medium'
                    })
        
        # Check for unsafe file operations
        unsafe_file_patterns = [
            r'os\.system\s*\(',
            r'subprocess\.call\s*\(',
            r'exec\s*\(',
            r'eval\s*\('
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in unsafe_file_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'type': 'command_injection',
                        'line': i,
                        'message': f'Unsafe command execution: {line.strip()}',
                        'severity': 'high'
                    })
        
        # Check for weak CORS configuration
        if 'CORS' in content and 'origins: "*"' in content:
            issues.append({
                'type': 'weak_cors',
                'line': 0,
                'message': 'Weak CORS configuration: origins set to "*"',
                'severity': 'medium'
            })
        
        return issues
    
    def scan_dependencies(self) -> List[Dict[str, Any]]:
        """Scan for vulnerable dependencies"""
        issues = []
        
        # Check Python requirements
        requirements_file = self.project_root / 'backend' / 'requirements.txt'
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                content = f.read()
                
            # Check for outdated or vulnerable packages
            vulnerable_packages = {
                'Flask': '2.3.2',
                'werkzeug': '2.3.7',
                'requests': '2.31.0'
            }
            
            for package, min_version in vulnerable_packages.items():
                if package in content:
                    # Simple version check (in production, use proper version parsing)
                    if f'{package}==' in content:
                        issues.append({
                            'type': 'dependency',
                            'message': f'Check {package} version for vulnerabilities',
                            'severity': 'low'
                        })
        
        # Check Node.js dependencies
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            with open(package_json, 'r') as f:
                data = json.load(f)
                
            if 'dependencies' in data:
                for package, version in data['dependencies'].items():
                    if '^' in version or '~' in version:
                        issues.append({
                            'type': 'dependency',
                            'message': f'Consider pinning {package} version for security',
                            'severity': 'low'
                        })
        
        return issues
    
    def check_file_permissions(self) -> List[Dict[str, Any]]:
        """Check file permissions for security issues"""
        issues = []
        
        sensitive_files = [
            '.env',
            'config.py',
            'security.py',
            '*.key',
            '*.pem'
        ]
        
        for pattern in sensitive_files:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file():
                    stat = file_path.stat()
                    # Check if file is world-readable
                    if stat.st_mode & 0o004:
                        issues.append({
                            'type': 'file_permission',
                            'message': f'File {file_path} is world-readable',
                            'severity': 'medium'
                        })
        
        return issues
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        print("🔍 Starting security audit...")
        
        all_issues = []
        
        # Scan all Python and JavaScript files
        for ext in ['*.py', '*.js', '*.html']:
            for file_path in self.project_root.rglob(ext):
                if 'node_modules' not in str(file_path) and '.git' not in str(file_path):
                    issues = self.scan_file(file_path)
                    for issue in issues:
                        issue['file'] = str(file_path.relative_to(self.project_root))
                        all_issues.append(issue)
        
        # Scan dependencies
        dep_issues = self.scan_dependencies()
        all_issues.extend(dep_issues)
        
        # Check file permissions
        perm_issues = self.check_file_permissions()
        all_issues.extend(perm_issues)
        
        # Categorize issues by severity
        high_issues = [i for i in all_issues if i.get('severity') == 'high']
        medium_issues = [i for i in all_issues if i.get('severity') == 'medium']
        low_issues = [i for i in all_issues if i.get('severity') == 'low']
        
        # Generate recommendations
        recommendations = self.generate_recommendations(all_issues)
        
        report = {
            'summary': {
                'total_issues': len(all_issues),
                'high_severity': len(high_issues),
                'medium_severity': len(medium_issues),
                'low_severity': len(low_issues)
            },
            'issues': all_issues,
            'recommendations': recommendations
        }
        
        return report
    
    def generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on found issues"""
        recommendations = []
        
        if any(i['type'] == 'hardcoded_credential' for i in issues):
            recommendations.append("🔐 Move all hardcoded credentials to environment variables")
            recommendations.append("🔐 Use a secure secrets management system")
        
        if any(i['type'] == 'sql_injection' for i in issues):
            recommendations.append("🛡️ Use parameterized queries to prevent SQL injection")
            recommendations.append("🛡️ Implement input validation and sanitization")
        
        if any(i['type'] == 'xss' for i in issues):
            recommendations.append("🛡️ Sanitize all user input before rendering")
            recommendations.append("🛡️ Use textContent instead of innerHTML where possible")
        
        if any(i['type'] == 'weak_cors' for i in issues):
            recommendations.append("🌐 Configure CORS to only allow specific origins")
            recommendations.append("🌐 Implement proper CORS headers")
        
        if any(i['type'] == 'dependency' for i in issues):
            recommendations.append("📦 Regularly update dependencies and check for vulnerabilities")
            recommendations.append("📦 Use dependency scanning tools")
        
        if any(i['type'] == 'file_permission' for i in issues):
            recommendations.append("🔒 Set appropriate file permissions for sensitive files")
            recommendations.append("🔒 Use chmod 600 for sensitive configuration files")
        
        # General recommendations
        recommendations.extend([
            "🔐 Implement proper authentication and authorization",
            "🔐 Use HTTPS in production",
            "🔐 Implement rate limiting",
            "🔐 Add security headers (HSTS, CSP, etc.)",
            "🔐 Regular security audits and penetration testing",
            "🔐 Implement logging and monitoring",
            "🔐 Use secure session management",
            "🔐 Implement input validation on both client and server"
        ])
        
        return recommendations
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted security report"""
        print("\n" + "="*60)
        print("🔒 SECURITY AUDIT REPORT")
        print("="*60)
        
        summary = report['summary']
        print(f"\n📊 SUMMARY:")
        print(f"   Total Issues: {summary['total_issues']}")
        print(f"   High Severity: {summary['high_severity']}")
        print(f"   Medium Severity: {summary['medium_severity']}")
        print(f"   Low Severity: {summary['low_severity']}")
        
        if report['issues']:
            print(f"\n🚨 ISSUES FOUND:")
            for issue in report['issues']:
                severity_icon = "🔴" if issue.get('severity') == 'high' else "🟡" if issue.get('severity') == 'medium' else "🟢"
                print(f"   {severity_icon} {issue['type'].upper()}: {issue['message']}")
                if 'file' in issue and 'line' in issue:
                    print(f"      File: {issue['file']}:{issue['line']}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"   {rec}")
        
        print("\n" + "="*60)
        
        # Save report to file
        report_file = self.project_root / 'security_audit_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Detailed report saved to: {report_file}")

def main():
    """Main function to run security audit"""
    project_root = os.getcwd()
    auditor = SecurityAuditor(project_root)
    
    try:
        report = auditor.generate_report()
        auditor.print_report(report)
        
        # Exit with error code if high severity issues found
        if report['summary']['high_severity'] > 0:
            print("\n❌ High severity issues found! Please fix them before deployment.")
            exit(1)
        else:
            print("\n✅ No high severity issues found.")
            
    except Exception as e:
        print(f"❌ Error during security audit: {e}")
        exit(1)

if __name__ == "__main__":
    main() 