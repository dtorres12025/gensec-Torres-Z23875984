# Author: Daniel Torres
# FAU ID: Z12345678
# Course: COT 5930 - Security Engineering Systems with Generative AI
"""Security advisory query tool for cybersecurity standards and remediations.

This module provides a LangChain tool enabling agents to retrieve standardized
cybersecurity advisories covering OWASP Top 10 categories, associated risk
severities, actionable remediation patterns, and NIST SP 800-53 control mappings.
"""

from typing import Dict, List, Optional, TypedDict
from langchain_core.tools import tool


class AdvisoryRecord(TypedDict):
    """Schema for a cybersecurity advisory record.

    Attributes:
        topic_name: Canonical title for the advisory topic.
        vulnerability: Formal vulnerability name and classification (e.g., OWASP/CWE).
        risk_severity: Qualitative severity rating (e.g., Critical, High, Medium).
        remediation: Prescribed secure coding pattern or technical remediation.
        nist_control: NIST SP 800-53 Rev. 5 control mapping identifier.
        aliases: List of alternate keywords or abbreviations mapped to this topic.
    """

    topic_name: str
    vulnerability: str
    risk_severity: str
    remediation: str
    nist_control: str
    aliases: List[str]


SECURITY_ADVISORIES: Dict[str, AdvisoryRecord] = {
    "sql injection": {
        "topic_name": "SQL Injection",
        "vulnerability": "OWASP A03:2021 - Injection (CWE-89: Improper Neutralization of Special Elements used in an SQL Command)",
        "risk_severity": "Critical",
        "remediation": (
            "Use parameterized queries (prepared statements) or Object-Relational Mapping (ORM) "
            "to separate SQL code from untrusted user input.\n"
            "Example Secure Pattern:\n"
            "    # Parameterized query with psycopg/sqlite\n"
            "    cursor.execute(\n"
            "        'SELECT id, username, email FROM users WHERE username = %s AND status = %s',\n"
            "        (username, 'active')\n"
            "    )"
        ),
        "nist_control": "NIST SP 800-53 Rev. 5: SI-10 (Information Input Validation), AC-3 (Access Enforcement)",
        "aliases": ["sql injection", "sqli", "sql-injection", "injection", "cwe-89", "a03"],
    },
    "broken access control": {
        "topic_name": "Broken Access Control",
        "vulnerability": "OWASP A01:2021 - Broken Access Control (CWE-200, CWE-284, CWE-639 IDOR)",
        "risk_severity": "Critical",
        "remediation": (
            "Enforce strict server-side authorization checks on all protected endpoints and resources. "
            "Deny access by default and adhere to the principle of least privilege.\n"
            "Example Secure Pattern:\n"
            "    # Enforce object-level access verification\n"
            "    record = db.query(Document).filter_by(id=doc_id).first()\n"
            "    if not record or record.owner_id != current_user.id:\n"
            "        raise PermissionDeniedError('Unauthorized access to requested resource.')"
        ),
        "nist_control": "NIST SP 800-53 Rev. 5: AC-3 (Access Enforcement), AC-4 (Information Flow Enforcement), AC-6 (Least Privilege)",
        "aliases": ["broken access control", "access control", "bac", "idor", "cwe-639", "a01", "authorization"],
    },
    "server-side request forgery": {
        "topic_name": "Server-Side Request Forgery (SSRF)",
        "vulnerability": "OWASP A10:2021 - Server-Side Request Forgery (SSRF) (CWE-918)",
        "risk_severity": "High",
        "remediation": (
            "Sanitize and validate destination URLs against a strict whitelist of permitted hostnames and protocols. "
            "Resolve target hostnames to IP addresses before request dispatch and block private, loopback, and metadata ranges (RFC 1918 / 169.254.169.254).\n"
            "Example Secure Pattern:\n"
            "    import ipaddress, socket, urllib.parse\n"
            "    parsed_url = urllib.parse.urlparse(target_url)\n"
            "    target_ip = socket.gethostbyname(parsed_url.hostname)\n"
            "    ip_obj = ipaddress.ip_address(target_ip)\n"
            "    if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:\n"
            "        raise SecurityValidationError('Destination address targets internal network resources.')"
        ),
        "nist_control": "NIST SP 800-53 Rev. 5: SC-7 (Boundary Protection), SI-10 (Information Input Validation)",
        "aliases": ["server-side request forgery", "server-side request forgery (ssrf)", "ssrf", "cwe-918", "a10"],
    },
    "insecure deserialization": {
        "topic_name": "Insecure Deserialization",
        "vulnerability": "OWASP A08:2021 - Software and Data Integrity Failures (CWE-502: Deserialization of Untrusted Data)",
        "risk_severity": "High",
        "remediation": (
            "Avoid deserializing binary formats (such as Python pickle or Java serialized objects) from untrusted sources. "
            "Utilize pure data serialization formats (JSON, Protocol Buffers) with strict schema validation.\n"
            "Example Secure Pattern:\n"
            "    import json\n"
            "    from pydantic import BaseModel, ValidationError\n"
            "    # Strictly parse and validate untrusted JSON payloads\n"
            "    data = json.loads(untrusted_payload)\n"
            "    validated_model = UserInputSchema.model_validate(data)"
        ),
        "nist_control": "NIST SP 800-53 Rev. 5: SI-7 (Software, Firmware, and Information Integrity), SC-18 (Mobile Code)",
        "aliases": ["insecure deserialization", "deserialization", "pickle", "software and data integrity failures", "cwe-502", "a08"],
    },
    "cryptographic failures": {
        "topic_name": "Cryptographic Failures",
        "vulnerability": "OWASP A02:2021 - Cryptographic Failures (CWE-326, CWE-327: Use of Broken or Risky Cryptographic Algorithms)",
        "risk_severity": "High",
        "remediation": (
            "Encrypt all sensitive data in transit using TLS 1.3 and at rest with authenticated ciphers (AES-256-GCM). "
            "Store passwords using salted, work-factor adjustable cryptographic hashing functions (Argon2id, bcrypt).\n"
            "Example Secure Pattern:\n"
            "    import bcrypt\n"
            "    salt = bcrypt.gensalt(rounds=12)\n"
            "    hashed_secret = bcrypt.hashpw(plain_password.encode('utf-8'), salt)"
        ),
        "nist_control": "NIST SP 800-53 Rev. 5: SC-13 (Cryptographic Protection), SC-28 (Protection of Information at Rest)",
        "aliases": ["cryptographic failures", "crypto", "broken cryptography", "cwe-327", "cwe-326", "a02", "sensitive data exposure"],
    },
    "cross-site scripting": {
        "topic_name": "Cross-Site Scripting (XSS)",
        "vulnerability": "OWASP A03:2021 - Injection (CWE-79: Improper Neutralization of Input During Web Page Generation)",
        "risk_severity": "High",
        "remediation": (
            "Contextually encode untrusted input before rendering into HTML, attributes, JavaScript, or CSS contexts. "
            "Deploy a restrictive Content Security Policy (CSP) header to mitigate script execution risks.\n"
            "Example Secure Pattern:\n"
            "    import html\n"
            "    safe_output = html.escape(untrusted_user_input, quote=True)"
        ),
        "nist_control": "NIST SP 800-53 Rev. 5: SI-10 (Information Input Validation), SC-8 (Transmission Confidentiality and Integrity)",
        "aliases": ["cross-site scripting", "xss", "stored xss", "reflected xss", "cwe-79"],
    },
    "security misconfiguration": {
        "topic_name": "Security Misconfiguration",
        "vulnerability": "OWASP A05:2021 - Security Misconfiguration (CWE-16)",
        "risk_severity": "Medium",
        "remediation": (
            "Disable debug endpoints and verbose error tracebacks in production environments. "
            "Implement automated configuration auditing and remove default credentials and unused services.\n"
            "Example Secure Pattern:\n"
            "    # Production environment hardening\n"
            "    DEBUG = False\n"
            "    SECURE_HSTS_SECONDS = 31536000\n"
            "    SECURE_CONTENT_TYPE_NOSNIFF = True"
        ),
        "nist_control": "NIST SP 800-53 Rev. 5: CM-6 (Configuration Settings), CM-7 (Least Functionality)",
        "aliases": ["security misconfiguration", "misconfiguration", "cwe-16", "a05", "default credentials"],
    },
    "identification and authentication failures": {
        "topic_name": "Identification and Authentication Failures",
        "vulnerability": "OWASP A07:2021 - Identification and Authentication Failures (CWE-287, CWE-384)",
        "risk_severity": "High",
        "remediation": (
            "Require Multi-Factor Authentication (MFA) for privileged and sensitive access. "
            "Implement account lockout / rate limiting mechanisms on login interfaces and invalidate sessions upon sign-out.\n"
            "Example Secure Pattern:\n"
            "    # Invalidate session token on logout\n"
            "    session.invalidate()\n"
            "    response.delete_cookie('session_id', secure=True, httponly=True, samesite='Strict')"
        ),
        "nist_control": "NIST SP 800-53 Rev. 5: IA-2 (Identification and Authentication), AC-7 (Unsuccessful Logon Attempts)",
        "aliases": ["identification and authentication failures", "broken authentication", "authentication", "mfa", "cwe-287", "a07"],
    },
}


def _find_advisory(query: str) -> Optional[AdvisoryRecord]:
    """Search for a matching advisory record using exact or alias matching.

    Args:
        query: User supplied topic or vulnerability keyword string.

    Returns:
        The matched AdvisoryRecord if found; otherwise, None.
    """
    normalized_query: str = query.strip().lower()
    if not normalized_query:
        return None

    # Check for direct key match
    if normalized_query in SECURITY_ADVISORIES:
        return SECURITY_ADVISORIES[normalized_query]

    # Check across aliases and canonical names
    for record in SECURITY_ADVISORIES.values():
        canonical_lower: str = record["topic_name"].lower()
        if normalized_query == canonical_lower or normalized_query in canonical_lower:
            return record
        for alias in record["aliases"]:
            if normalized_query == alias or normalized_query in alias or alias in normalized_query:
                return record

    return None


def _format_advisory(advisory: AdvisoryRecord) -> str:
    """Format an advisory record into a structured output string.

    Args:
        advisory: The advisory dictionary containing vulnerability details.

    Returns:
        Structured string representation containing Vulnerability, Risk Severity,
        NIST Control Mapping, and Remediation Code/Pattern.
    """
    return (
        f"Vulnerability: {advisory['vulnerability']}\n"
        f"Risk Severity: {advisory['risk_severity']}\n"
        f"NIST Control Mapping: {advisory['nist_control']}\n"
        f"Remediation Code/Pattern:\n{advisory['remediation']}"
    )


def _format_fallback_message(query: str) -> str:
    """Construct a fallback message listing all valid searchable topics.

    Args:
        query: The unrecognized topic string submitted by the caller.

    Returns:
        A formatted message informing the user of the invalid query and providing
        a list of supported topics.
    """
    valid_topics: List[str] = sorted(
        {record["topic_name"] for record in SECURITY_ADVISORIES.values()}
    )
    topic_list_str: str = "\n".join(f"- {topic}" for topic in valid_topics)
    return (
        f"Security advisory for topic '{query}' was not found in the database.\n"
        f"Valid searchable topics include:\n{topic_list_str}"
    )


@tool
def query_security_advisory(topic: str) -> str:
    """Query structured cybersecurity advisories for vulnerabilities and remediation patterns.

    Searches an internal database of cybersecurity standards (OWASP Top 10, CWE, NIST)
    for a given vulnerability topic, providing detailed risk severities, secure remediation
    code patterns, and NIST SP 800-53 control mappings.

    Args:
        topic: The name, acronym, or category of the security vulnerability to query
            (e.g., 'SQL Injection', 'Broken Access Control', 'SSRF', 'Insecure Deserialization',
            'Cryptographic Failures').

    Returns:
        A structured security advisory detailing Vulnerability, Risk Severity,
        NIST Control Mapping, and Remediation Code/Pattern if a match is found;
        otherwise, a fallback message enumerating all valid searchable topics.
    """
    match: Optional[AdvisoryRecord] = _find_advisory(topic)
    if match is not None:
        return _format_advisory(match)
    return _format_fallback_message(topic)
