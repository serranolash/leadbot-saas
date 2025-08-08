import re
import urllib.parse
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from .base import SourceAdapter

class ComputrabajoAdapter(SourceAdapter):
    name = "computrabajo"

    def search(self, query: str, want: int) -> List[str]:
        q = urllib.parse.quote_plus(query)
        base = f"https://ar.computrabajo.com/ofertas-de-trabajo/?q={q}"
        try:
            html = requests.get(base, timeout=20).text
        except Exception:
            return []
        soup = BeautifulSoup(html, "html.parser")
        urls: List[str] = []
        for a in soup.select("a.js-o-link.fc_base"):
            href = a.get("href", "")
            if not href:
                continue
            full = urllib.parse.urljoin(base, href)
            if full not in urls:
                urls.append(full)
            if len(urls) >= want:
                break
        return urls

    def fetch(self, url: str) -> Optional[Dict]:
        try:
            html = requests.get(url, timeout=20).text
            soup = BeautifulSoup(html, "html.parser")
            title_el = soup.select_one("h1")
            title = title_el.get_text(strip=True) if title_el else "Oferta Computrabajo"
            company_el = soup.select_one(".fc_base.mt5")
            company = company_el.get_text(strip=True) if company_el else None
            loc_el = soup.select_one(".fc_aux.t_orange")
            loc = loc_el.get_text(strip=True) if loc_el else None
            desc_el = soup.select_one("#p_oferta")
            desc = desc_el.get_text("\n", strip=True) if desc_el else ""
            email = None
            phone = None
            m = re.search(r'[\w\.-]+@[\w\.-]+', desc)
            if m: email = m.group(0)
            m2 = re.search(r'\+?\d[\d\-\s\(\)]{7,}\d', desc)
            if m2: phone = m2.group(0)
            return {
                "url": url,
                "name": title,
                "email": email,
                "phone": phone,
                "company": company,
                "location": loc,
                "headline": title,
                "about": desc[:1000],
                "exp_titles": [],
                "years_estimated": 0,
                "raw_text": desc,
            }
        except Exception:
            return None
