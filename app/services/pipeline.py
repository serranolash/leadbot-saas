import os, time, random
from typing import List, Dict
from ..adapters.registry import get_registry
from ..utils.excel_export import export_excel
from .ranker import build_groups_from_query, extract_required_years, estimate_match
from ..settings import settings

def run_pipeline(tenant_creds_map: dict, query: str, target: int, min_score: int, min_groups: int, min_years: int) -> Dict:
    adapters = []
    for name, cls in get_registry().items():
        creds = tenant_creds_map.get(name) or {}
        adapters.append(cls(creds))
    if not adapters:
        return {"count": 0, "xlsx_path": None, "candidates_seen": 0}

    want = max(target * 6, 60)
    bag_urls: List[str] = []
    for ad in adapters:
        try:
            urls = ad.search(query, max(10, want // len(adapters)))
            bag_urls.extend(urls)
        except Exception:
            continue
    bag_urls = list(dict.fromkeys(bag_urls))

    groups = build_groups_from_query(query)
    if not groups:
        min_groups = max(1, min_groups)
    if min_years == 0:
        min_years = extract_required_years(query)

    selected = []
    for url in bag_urls:
        ad = None
        for candidate in adapters:
            if candidate.name == "linkedin" and "linkedin.com/in/" in url:
                ad = candidate; break
            if candidate.name == "computrabajo" and "computrabajo" in url:
                ad = candidate; break
        ad = ad or adapters[0]

        snap = ad.fetch(url)
        if not snap:
            continue
        ok, info = estimate_match(snap, groups, min_groups, min_score, min_years)
        if ok:
            selected.append({
                "name": snap.get("name"),
                "email": snap.get("email"),
                "phone": snap.get("phone"),
                "company": snap.get("company"),
                "location": snap.get("location"),
                "years_estimated": snap.get("years_estimated"),
                "url": snap.get("url"),
                **info
            })
        if len(selected) >= target:
            break
        time.sleep(random.uniform(0.8, 1.6))

    os.makedirs(settings.EXPORT_DIR, exist_ok=True)
    xlsx = os.path.join(settings.EXPORT_DIR, "leads.xlsx")
    export_excel(selected, xlsx)
    return {"count": len(selected), "xlsx_path": xlsx, "candidates_seen": len(bag_urls)}
