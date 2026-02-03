"""
API client for Chemical Equipment backend (Django REST).
"""
import base64
import requests
from typing import Optional, List, Dict, Any

DEFAULT_BASE = "http://127.0.0.1:8000/api"


class EquipmentAPIClient:
    def __init__(self, base_url: str = DEFAULT_BASE, username: Optional[str] = None, password: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if username and password:
            self.session.auth = (username, password)
            self.session.headers["Authorization"] = "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()

    def upload_csv(self, file_path: str, name: Optional[str] = None) -> Dict[str, Any]:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.split("/")[-1].split("\\")[-1], f, "text/csv")}
            data = {} if not name else {"name": name}
            r = self.session.post(f"{self.base_url}/upload/", files=files, data=data, timeout=30)
        r.raise_for_status()
        return r.json()

    def get_summary(self, dataset_id: int) -> Dict[str, Any]:
        r = self.session.get(f"{self.base_url}/summary/{dataset_id}/", timeout=10)
        r.raise_for_status()
        return r.json()

    def get_history(self) -> List[Dict[str, Any]]:
        r = self.session.get(f"{self.base_url}/history/", timeout=10)
        r.raise_for_status()
        return r.json()

    def download_pdf(self, dataset_id: int, save_path: str) -> None:
        r = self.session.get(f"{self.base_url}/report/{dataset_id}/pdf/", timeout=30)
        r.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(r.content)
