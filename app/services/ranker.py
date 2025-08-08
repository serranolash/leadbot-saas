import re
import unicodedata
from typing import Dict, List, Tuple

NEGATIVE_TERMS = [
    "data analyst","ux","qa","talent acquisition","hr","rrhh","marketing","ventas","account manager",
    "docente","teacher","student","estudiante","administrativo","recepcionista","atención al cliente"
]

def _norm(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text

def build_groups_from_query(query: str) -> List[List[str]]:
    q = _norm(query)
    import re as _re
    tokens = [t for t in _re.split(r"[^a-z0-9\+]+", q) if t]
    groups: List[List[str]] = []
    tech = []
    for t in tokens:
        if t in {"java","python","node","react","angular","php","dotnet","c#","c++","go","mysql","postgres","mongodb","aws","gcp","azure","shopify","magento","woocommerce","prestashop","ecommerce"}:
            tech.append(t)
    if tech: groups.append(tech)
    if any(t in tokens for t in ["backend","back","server"]):
        groups.append(["backend","back end","back-end"])
    if any(t in tokens for t in ["fullstack","full","fs"]):
        groups.append(["fullstack","full stack","full-stack"])
    if any(t in tokens for t in ["ecommerce","e-commerce","shopify","magento","woocommerce","prestashop"]):
        groups.append(["ecommerce","e-commerce","shopify","magento","woocommerce","prestashop"])
    if "senior" in tokens or "sr" in tokens:
        groups.append(["senior","sr","ssr","s sr"])
    if not groups:
        groups = [[t] for t in tokens if len(t) > 2][:3]
    return groups[:5]

def extract_required_years(query: str) -> int:
    q = _norm(query)
    m = re.search(r"(\d+)\s*(?:anos|años|years|yr|yrs)", q)
    return int(m.group(1)) if m else 0

def estimate_match(snap: Dict, groups: List[List[str]], min_groups: int, min_score: int, min_years: int) -> Tuple[bool, Dict]:
    text = " ".join([
        snap.get("headline") or "",
        snap.get("about") or "",
        " ".join(snap.get("exp_titles") or []),
        snap.get("raw_text") or "",
        snap.get("name") or "",
    ])
    text_n = _norm(text)

    score = 0
    matched_groups = 0
    for group in groups:
        if any(_norm(term) in text_n for term in group):
            matched_groups += 1
            score += 5
    if any(t in text_n for t in NEGATIVE_TERMS):
        score -= 4

    years = snap.get("years_estimated") or 0
    years_ok = (years >= (min_years or 0))

    ok = (matched_groups >= max(1, min_groups)) and (score >= min_score) and years_ok
    info = {"score": score, "groups_matched": matched_groups, "years_ok": years_ok}
    return ok, info
