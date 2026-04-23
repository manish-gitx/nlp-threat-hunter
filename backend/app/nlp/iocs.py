import re
from typing import Dict, List

# Regex-based Indicator of Compromise extractors. Patterns are intentionally
# conservative so noise from log formats doesn't flood results.

_PATTERNS: Dict[str, re.Pattern] = {
    "ipv4": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b"
    ),
    "ipv6": re.compile(r"\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b"),
    "url": re.compile(r"\bhttps?://[^\s<>\"']+", re.IGNORECASE),
    "domain": re.compile(
        r"\b(?=[a-z0-9-]{1,63}\.)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+"
        r"(?:com|net|org|io|ru|cn|co|info|biz|xyz|top|dev|gov|mil|edu|tk|ml|ga|cf)\b",
        re.IGNORECASE,
    ),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "md5": re.compile(r"\b[a-f0-9]{32}\b", re.IGNORECASE),
    "sha1": re.compile(r"\b[a-f0-9]{40}\b", re.IGNORECASE),
    "sha256": re.compile(r"\b[a-f0-9]{64}\b", re.IGNORECASE),
    "cve": re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE),
    "file_path_windows": re.compile(r"\b[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]+"),
    "registry_key": re.compile(r"\bHKEY_[A-Z_]+\\[^\s]+"),
    "port": re.compile(r"\bport\s+(\d{1,5})\b", re.IGNORECASE),
    "mitre_technique": re.compile(r"\bT\d{4}(?:\.\d{3})?\b"),
}


def extract_iocs(text: str) -> List[dict]:
    found: List[dict] = []
    seen: set[tuple[str, str]] = set()
    for ioc_type, pattern in _PATTERNS.items():
        for match in pattern.findall(text):
            value = match if isinstance(match, str) else match[0]
            value = value.strip().rstrip(".,;:)\"'")
            key = (ioc_type, value.lower())
            if key in seen or not value:
                continue
            seen.add(key)
            found.append({"value": value, "ioc_type": ioc_type})
    return found
