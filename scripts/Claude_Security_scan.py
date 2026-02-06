import json
import os
import sys
import anthropic

# Fetch the variable mapped in the YAML
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("AI_AUTO_REMEDIATION_TRIVY not found in environment!")

def analyze_vulnerability(cve_data):
    """Use AI to analyze CVE and suggest fix"""
    
    prompt = f"""You are a DevSecOps expert. Analyze this vulnerability and provide a fix.

CVE ID: {cve_data.get('VulnerabilityID', 'Unknown')}
Package: {cve_data.get('PkgName', 'Unknown')}
Installed Version: {cve_data.get('InstalledVersion', 'Unknown')}
Severity: {cve_data.get('Severity', 'Unknown')}
Description: {cve_data.get('Description', 'No description')}

Provide:
1. Root cause analysis (2-3 sentences)
2. Recommended fix (specific version upgrade or base image change)
3. Updated Dockerfile snippet if applicable

Format as JSON:
{{
  "root_cause": "...",
  "recommended_fix": "...",
  "dockerfile_change": "..."
}}
"""
    
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text

def main():
    # SCan Trivy results is present and analyze_vulnerability with claude
    if not os.path.exists('trivy-results.json'):
        print("No Trivy results found")
        sys.exit(0)
    
    with open('trivy-results.json', 'r') as f:
        trivy_data = json.load(f)
    
    vulnerabilities = []
    for result in trivy_data.get('Results', []):
        for vuln in result.get('Vulnerabilities', []):
            if vuln.get('Severity') in ['CRITICAL', 'HIGH']:
                vulnerabilities.append(vuln)
    
    if not vulnerabilities:
        print("No critical/high vulnerabilities found")
        sys.exit(0)
    
    print(f"Found {len(vulnerabilities)} critical/high vulnerabilities")
    
    # Analyze with AI
    fixes = []
    for vuln in vulnerabilities[:3]:  # Limit to 3 for cost
        print(f"Analyzing {vuln.get('VulnerabilityID')}...")
        ai_response = analyze_vulnerability(vuln)
        fixes.append(ai_response)
    
    # Generate report
    report = "# AI Security Remediation Report\n\n"
    for i, fix in enumerate(fixes):
        report += f"## Vulnerability {i+1}\n"
        report += f"{fix}\n\n"
    
    # Save report
    with open('ai-remediation-report.md', 'w') as f:
        f.write(report)
    
    print("Remediation report generated!")