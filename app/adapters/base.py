from typing import List, Dict, Optional

class SourceAdapter:
    name = "base"
    def __init__(self, tenant_credentials: dict):
        self.creds = tenant_credentials or {}
    def search(self, query: str, want: int) -> List[str]:
        raise NotImplementedError
    def fetch(self, url: str) -> Optional[Dict]:
        raise NotImplementedError
