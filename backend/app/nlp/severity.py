from typing import Iterable

_CRITICAL_KEYWORDS = {
    "ransomware", "encrypt", "wiper", "domain controller", "privilege escalation",
    "zero-day", "0-day", "exfiltrat", "c2", "command and control", "apt",
}
_HIGH_KEYWORDS = {
    "malware", "trojan", "backdoor", "implant", "beacon", "phishing", "cobalt strike",
    "mimikatz", "kerberoast", "lateral movement", "persistence",
}
_MED_KEYWORDS = {
    "brute", "spray", "scan", "probe", "failed login", "suspicious", "anomaly",
}

_CATEGORY_BASELINE = {
    "apt": 0.85,
    "data_exfiltration": 0.8,
    "malware": 0.7,
    "insider_threat": 0.65,
    "phishing": 0.55,
    "ddos": 0.55,
    "brute_force": 0.4,
    "benign": 0.05,
}


def _kw_score(text_lower: str, keywords: Iterable[str]) -> float:
    return sum(1 for kw in keywords if kw in text_lower)


def score_severity(text: str, category: str, ioc_count: int) -> tuple[str, float]:
    tl = text.lower()
    base = _CATEGORY_BASELINE.get(category, 0.3)

    critical_hits = _kw_score(tl, _CRITICAL_KEYWORDS)
    high_hits = _kw_score(tl, _HIGH_KEYWORDS)
    med_hits = _kw_score(tl, _MED_KEYWORDS)

    score = base + 0.15 * critical_hits + 0.08 * high_hits + 0.03 * med_hits
    score += min(ioc_count, 10) * 0.02
    score = max(0.0, min(1.0, score))

    if category == "benign":
        return "low", min(score, 0.2)
    if score >= 0.8:
        level = "critical"
    elif score >= 0.6:
        level = "high"
    elif score >= 0.35:
        level = "medium"
    else:
        level = "low"
    return level, round(score, 3)
