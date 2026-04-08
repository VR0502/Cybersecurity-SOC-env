from models import ThreatType

ALERT_SCENARIOS = {
    "phishing_low": {
        "srcIP": "192.168.1.105",
        "typ": ThreatType.PHISHING,
        "sev": 3,
        "desc": "User clicked suspicious link"
    },
    "brute_force_high": {
        "srcIP": "45.33.22.11",
        "typ": ThreatType.BRUTE_FORCE,
        "sev": 9,
        "desc": "SSH brute force from known malicious IP"
    },
    "malware_critical": {
        "srcIP": "10.0.0.47",
        "typ": ThreatType.MALWARE,
        "sev": 8,
        "desc": "Malware execution detected"
    }
}