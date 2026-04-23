from typing import List, Optional

import spacy
from spacy.language import Language

from app.config import get_settings

_nlp: Optional[Language] = None

# Curated lists of threat actors, malware families, and tools so the NER layer
# picks them up even without a fine-tuned cybersecurity model.
_THREAT_ACTORS = [
    "APT28", "APT29", "APT33", "APT41", "Lazarus", "Fancy Bear", "Cozy Bear",
    "FIN7", "FIN8", "Turla", "Sandworm", "Wizard Spider", "Conti Group",
    "Equation Group", "Kimsuky", "BlackMatter", "DarkSide",
]
_MALWARE = [
    "Emotet", "TrickBot", "Qakbot", "IcedID", "Dridex", "Ryuk", "Conti",
    "LockBit", "REvil", "WannaCry", "NotPetya", "Cobalt Strike", "Mimikatz",
    "Raccoon", "RedLine", "Agent Tesla", "FormBook", "njRAT", "Remcos",
    "BlackCat", "ALPHV", "Maze", "Cuba", "Hive",
]
_TOOLS = [
    "PowerShell", "PsExec", "Rubeus", "BloodHound", "Impacket", "Metasploit",
    "Nmap", "Responder", "Sliver", "Brute Ratel",
]


def _build_patterns():
    return (
        [{"label": "THREAT_ACTOR", "pattern": name} for name in _THREAT_ACTORS]
        + [{"label": "MALWARE", "pattern": name} for name in _MALWARE]
        + [{"label": "TOOL", "pattern": name} for name in _TOOLS]
    )


def get_nlp() -> Language:
    global _nlp
    if _nlp is not None:
        return _nlp
    settings = get_settings()
    try:
        nlp = spacy.load(settings.spacy_model)
    except OSError:
        # Fall back to a blank English pipeline if the model isn't installed.
        # NER quality will be lower, but the app still runs.
        nlp = spacy.blank("en")
    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler", before="ner" if "ner" in nlp.pipe_names else None)
        ruler.add_patterns(_build_patterns())
    _nlp = nlp
    return nlp


_INTERESTING_LABELS = {
    "ORG", "PERSON", "GPE", "LOC", "PRODUCT", "EVENT", "DATE", "TIME",
    "THREAT_ACTOR", "MALWARE", "TOOL",
}


def extract_entities(text: str) -> List[dict]:
    nlp = get_nlp()
    doc = nlp(text)
    seen: set[tuple[str, str]] = set()
    out: List[dict] = []
    for ent in doc.ents:
        if ent.label_ not in _INTERESTING_LABELS:
            continue
        key = (ent.label_, ent.text.lower())
        if key in seen:
            continue
        seen.add(key)
        out.append({"text": ent.text, "label": ent.label_})
    return out
