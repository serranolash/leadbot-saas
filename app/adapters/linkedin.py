import time, random
from typing import List, Dict, Optional
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from .base import SourceAdapter

LOGIN_URL = "https://www.linkedin.com/login"
SEARCH_URL_TPL = "https://www.linkedin.com/search/results/people/?keywords={kw}&origin=SWITCH_SEARCH_VERTICAL"

def _init_driver(profile_path: Optional[str] = None, binary_path: Optional[str] = None):
    options = Options()
    if binary_path:
        options.binary_location = binary_path
    if profile_path:
        options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1280,900")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

class LinkedInAdapter(SourceAdapter):
    name = "linkedin"

    def __init__(self, tenant_credentials: dict):
        super().__init__(tenant_credentials)
        self.driver = None

    def _login(self, driver) -> bool:
        user = self.creds.get("user")
        pwd  = self.creds.get("pass")
        if not user or not pwd:
            print("[linkedin] Falta user/pass en credenciales del tenant")
            return False
        w = WebDriverWait(driver, 20)
        driver.get(LOGIN_URL)
        w.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(user)
        driver.find_element(By.ID, "password").send_keys(pwd)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        w.until(EC.any_of(
            EC.url_contains("/feed"),
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder]"))
        ))
        return True

    def search(self, query: str, want: int) -> List[str]:
        profile_path = self.creds.get("chrome_profile")
        binary_path = self.creds.get("chrome_binary")
        self.driver = _init_driver(profile_path, binary_path)
        d = self.driver

        if not self._login(d):
            return []

        d.get(SEARCH_URL_TPL.format(kw=quote_plus(query)))
        time.sleep(1.0)

        urls: List[str] = []
        seen = set()

        def harvest():
            cards = d.find_elements(By.CSS_SELECTOR, "li.reusable-search__result-container, div.entity-result")
            for c in cards:
                try:
                    a = c.find_element(By.CSS_SELECTOR, "a.app-aware-link[href*='/in/']")
                    href = a.get_attribute("href").split("?")[0]
                    if href and href not in seen:
                        seen.add(href); urls.append(href)
                except Exception:
                    continue

        harvest()
        for p in range(2, 10):
            d.get(d.current_url + f"&page={p}")
            time.sleep(random.uniform(1.0, 1.8))
            d.execute_script("window.scrollBy(0, document.body.scrollHeight*0.85);")
            time.sleep(0.6)
            harvest()
            if len(urls) >= want:
                break
        return urls[:want]

    def fetch(self, url: str) -> Optional[Dict]:
        if not self.driver:
            return None
        d = self.driver
        w = WebDriverWait(d, 20)
        try:
            d.get(url)
            w.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
            time.sleep(0.6)
            def safe_text(css):
                try:
                    return d.find_element(By.CSS_SELECTOR, css).text.strip()
                except Exception:
                    return None
            name = safe_text("h1")
            headline = safe_text("div.pv-text-details__left-panel div.text-body-medium") or safe_text("div.text-body-medium.break-words")
            loc = safe_text("span.text-body-small.t-black--light.inline")
            email = phone = None
            try:
                btn = d.find_element(By.XPATH, "//a[contains(@href,'overlay/contact-info')]")
                d.execute_script("arguments[0].click();", btn)
                time.sleep(0.5)
                modal = d.find_element(By.CSS_SELECTOR, "div.pv-contact-info, div.artdeco-modal")
                modal_txt = modal.text
                import re
                m = re.search(r'[\w\.-]+@[\w\.-]+', modal_txt or "")
                if m: email = m.group(0)
                m2 = re.search(r'\+?\d[\d\-\s\(\)]{7,}\d', modal_txt or "")
                if m2: phone = m2.group(0)
                try:
                    d.find_element(By.CSS_SELECTOR, "button[aria-label='Dismiss']").click()
                except Exception:
                    pass
            except Exception:
                pass

            exp_titles, years_estimated = [], 0
            try:
                exp_url = url.rstrip("/") + "/details/experience/"
                d.get(exp_url); time.sleep(0.6)
                for el in d.find_elements(By.XPATH, "//span[contains(@class,'t-bold') and @aria-hidden='true']"):
                    t = el.text.strip()
                    if t and t not in exp_titles:
                        exp_titles.append(t)
                body = d.find_element(By.TAG_NAME, "body").text
                import re
                yrs = re.findall(r'(\d+)\s*(?:anos|años|years|yrs|yr)', body.lower())
                years_estimated = max([int(x) for x in yrs]) if yrs else 0
                d.get(url); w.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
            except Exception:
                pass

            body_text = d.find_element(By.TAG_NAME, "body").text
            return {
                "url": url,
                "name": name,
                "email": email,
                "phone": phone,
                "company": None,
                "location": loc,
                "headline": headline,
                "about": "",
                "exp_titles": exp_titles[:12],
                "years_estimated": years_estimated,
                "raw_text": body_text[:5000],
            }
        except Exception:
            return None
